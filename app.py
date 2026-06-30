import base64
import ipaddress
import io
import json
import os
import socket
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "items.db")

DASHSCOPE_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
AI_TEXT_MODEL = "qwen-plus"
AI_VISION_MODEL = "qwen-vl-max"
AI_AUDIO_MODEL = "qwen-audio-turbo"
AI_MAX_TOKENS = 300


def _is_private_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def is_safe_host(hostname: str) -> bool:
    """Resolve hostname locally and reject private/loopback/link-local addresses."""
    if not hostname:
        return False
    if hostname.lower() in ("localhost",):
        return False
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = info[4][0]
        if _is_private_ip(ip):
            return False
    return True


class SafeTransport(httpx.HTTPTransport):
    """Re-validate resolved IP at connect time to defeat DNS rebinding."""

    def handle_request(self, request):
        parsed = urlparse(str(request.url))
        if not is_safe_host(parsed.hostname):
            raise httpx.ConnectError(f"Blocked unsafe host: {parsed.hostname}")
        return super().handle_request(request)


class RateLimiter:
    """Simple in-memory token bucket per IP. Sufficient for single-process deploy."""

    def __init__(self, capacity: int = 10, refill_per_sec: float = 0.2):
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self.buckets: dict[str, tuple[float, float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        tokens, last = self.buckets.get(key, (self.capacity, now))
        tokens = min(self.capacity, tokens + (now - last) * self.refill_per_sec)
        if tokens < 1:
            self.buckets[key] = (tokens, now)
            return False
        self.buckets[key] = (tokens - 1, now)
        return True


ai_limiter = RateLimiter(capacity=10, refill_per_sec=0.2)  # 10 burst, 12/min sustained


def client_ip() -> str:
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.remote_addr or "unknown"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                content TEXT,
                filename TEXT,
                mime_type TEXT,
                ai_summary TEXT,
                ai_tags TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


init_db()


def ai_headers():
    """Return auth headers for DashScope, or None if not configured."""
    key = os.getenv("ALIYUN_API_KEY")
    if not key:
        return None
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def dashscope_chat(messages, model=AI_TEXT_MODEL):
    """Send a chat completion to DashScope. Returns assistant text. Raises on error."""
    headers = ai_headers()
    if not headers:
        return None
    body = {"model": model, "messages": messages, "max_tokens": AI_MAX_TOKENS}
    r = httpx.post(
        f"{DASHSCOPE_BASE}/chat/completions",
        headers=headers,
        json=body,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


# ── Page Routes ──────────────────────────────────────────────


@app.route("/")
def home():
    return render_template("home.html", active_page="home")


@app.route("/add")
def add():
    return render_template("add.html", active_page="add")


@app.route("/profile")
def profile():
    return render_template("profile.html", active_page="profile")


# ── API: Process with AI ─────────────────────────────────────


@app.route("/api/process/text", methods=["POST"])
def process_text():
    if not ai_limiter.allow(client_ip()):
        return jsonify({"error": "请求过于频繁，请稍后再试"}), 429
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        summary = call_ai_text(text)
    except Exception as e:
        print(f"[AI text error] {e}")
        return jsonify({"error": "AI 处理失败，请稍后重试"}), 502
    item_id = save_item("text", content=text, ai_summary=summary)
    return jsonify({"id": item_id, "summary": summary, "tags": []})


@app.route("/api/process/image", methods=["POST"])
def process_image():
    if not ai_limiter.allow(client_ip()):
        return jsonify({"error": "请求过于频繁，请稍后再试"}), 429
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image provided"}), 400

    mime = file.mimetype or "image/png"
    raw = file.read()

    try:
        summary = call_ai_vision(raw, mime)
    except Exception as e:
        print(f"[AI vision error] {e}")
        return jsonify({"error": "AI 图片分析失败，请稍后重试"}), 502
    item_id = save_item(
        "image",
        content=file.filename,
        filename=file.filename,
        mime_type=mime,
        ai_summary=summary,
    )
    return jsonify({"id": item_id, "summary": summary, "tags": []})


@app.route("/api/process/link", methods=["POST"])
def process_link():
    if not ai_limiter.allow(client_ip()):
        return jsonify({"error": "请求过于频繁，请稍后再试"}), 429
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No link provided"}), 400

    page_text = fetch_url_text(url)
    try:
        summary = call_ai_link(url, page_text)
    except Exception as e:
        print(f"[AI link error] {e}")
        return jsonify({"error": "AI 链接分析失败，请稍后重试"}), 502
    item_id = save_item("link", content=url, ai_summary=summary)
    return jsonify({"id": item_id, "summary": summary, "tags": []})


@app.route("/api/process/voice", methods=["POST"])
def process_voice():
    if not ai_limiter.allow(client_ip()):
        return jsonify({"error": "请求过于频繁，请稍后再试"}), 429
    file = request.files.get("audio")
    if not file:
        return jsonify({"error": "No audio provided"}), 400

    raw = file.read()
    b64 = base64.b64encode(raw).decode("utf-8")
    mime = file.mimetype or "audio/webm"

    try:
        summary = call_ai_audio(b64, mime)
    except Exception as e:
        print(f"[AI audio error] {e}")
        return jsonify({"error": "AI 语音处理失败，请稍后重试"}), 502
    item_id = save_item(
        "voice",
        content=file.filename or "voice_note",
        filename=file.filename,
        mime_type=mime,
        ai_summary=summary,
    )
    return jsonify({"id": item_id, "summary": summary, "tags": []})


# ── API: Items CRUD ──────────────────────────────────────────


@app.route("/api/items")
def list_items():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM items ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/items/<int:item_id>/complete", methods=["POST"])
def complete_item(item_id):
    with get_db() as conn:
        row = conn.execute("SELECT ai_tags FROM items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Item not found"}), 404
        tags = json.loads(row["ai_tags"] or "[]")
        if "completed" in tags:
            tags.remove("completed")
        else:
            tags.append("completed")
        conn.execute("UPDATE items SET ai_tags = ? WHERE id = ?", (json.dumps(tags), item_id))
        conn.commit()
    return jsonify({"ok": True})


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    with get_db() as conn:
        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
    return jsonify({"ok": True})


@app.route("/api/items", methods=["DELETE"])
def clear_all_items():
    # Require explicit confirmation token to prevent accidental / cross-origin wipes.
    token = request.headers.get("X-Confirm") or (request.get_json(silent=True) or {}).get("confirm")
    if token != "DELETE_ALL":
        return jsonify({"error": "Confirmation required", "hint": "Send header X-Confirm: DELETE_ALL"}), 400
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        conn.execute("DELETE FROM items")
        conn.commit()
    return jsonify({"ok": True, "deleted": count})


@app.route("/api/items/<int:item_id>/update", methods=["POST"])
def update_item(item_id):
    data = request.get_json()
    with get_db() as conn:
        conn.execute(
            "UPDATE items SET content = ?, ai_summary = ? WHERE id = ?",
            (data.get("content", ""), data.get("ai_summary", ""), item_id),
        )
        conn.commit()
    return jsonify({"ok": True})


# ── API: Data Export / Import ─────────────────────────────────


@app.route("/api/export")
def export_data():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM items ORDER BY created_at ASC").fetchall()
    data = [dict(r) for r in rows]
    buf = io.BytesIO()
    buf.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
    buf.seek(0)
    filename = f"simplicity_life_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    return send_file(
        buf,
        mimetype="application/json",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/api/import", methods=["POST"])
def import_data():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    try:
        data = json.loads(file.read())
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON file"}), 400

    if not isinstance(data, list):
        return jsonify({"error": "Expected a JSON array of items"}), 400

    with get_db() as conn:
        count = 0
        try:
            for item in data:
                if not isinstance(item, dict):
                    continue
                conn.execute(
                    """INSERT INTO items (type, content, filename, mime_type, ai_summary, ai_tags, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        item.get("type", "text"),
                        item.get("content", ""),
                        item.get("filename"),
                        item.get("mime_type"),
                        item.get("ai_summary"),
                        item.get("ai_tags"),
                        item.get("created_at", datetime.now(timezone.utc).isoformat()),
                    ),
                )
                count += 1
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return jsonify({"ok": True, "imported": count})


# ── AI Helpers ────────────────────────────────────────────────


def call_ai_text(text: str) -> str:
    result = dashscope_chat([
        {"role": "system", "content": "你是一个生活助手。分析用户的文字，提取关键信息（事件、时间、地点、待办事项），给出简洁的结构化摘要，并建议如何组织这些信息。用中文回复。"},
        {"role": "user", "content": text},
    ])
    if result is None:
        return f"[AI未配置] 你输入了: {text[:200]}"
    return result


def call_ai_vision(image_bytes: bytes, mime: str) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime};base64,{b64}"
    result = dashscope_chat([
        {"role": "system", "content": "你是一个生活助手。分析用户上传的图片，提取其中的关键信息（活动海报、门票日期、截屏内容等），给出简洁的结构化摘要。用中文回复。"},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": data_url}},
            {"type": "text", "text": "请分析这张图片中的信息。"},
        ]},
    ], model=AI_VISION_MODEL)
    if result is None:
        return "[AI未配置] 图片已接收，但需要配置 ALIYUN_API_KEY 才能分析。"
    return result


def call_ai_link(url: str, page_text: str) -> str:
    result = dashscope_chat([
        {"role": "system", "content": "你是一个生活助手。分析用户分享的网页链接内容，提取关键信息，给出简洁的结构化摘要。用中文回复。"},
        {"role": "user", "content": f"链接: {url}\n\n网页内容:\n{page_text[:4000]}"},
    ])
    if result is None:
        return f"[AI未配置] 链接: {url}"
    return result


def call_ai_audio(audio_b64: str, mime: str) -> str:
    data_url = f"data:{mime};base64,{audio_b64}"
    result = dashscope_chat([
        {"role": "system", "content": "你是一个生活助手。用户上传了一段语音。请根据音频内容进行转写和分析，提取关键信息。用中文回复。"},
        {"role": "user", "content": [
            {"type": "input_audio", "input_audio": {"data": data_url}},
            {"type": "text", "text": "请转写并分析这段语音中的信息。"},
        ]},
    ], model=AI_AUDIO_MODEL)
    if result is None:
        return "[AI未配置] 音频已接收，但需要配置 ALIYUN_API_KEY 才能转写和分析。"
    return result


def is_safe_url(url: str) -> bool:
    """Quick pre-check on scheme + hostname (does not defeat rebinding on its own)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    return is_safe_host(hostname)


def fetch_url_text(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not is_safe_host(parsed.hostname):
        return "[不安全的链接，已拒绝访问]"
    client = httpx.Client(
        timeout=10,
        follow_redirects=True,
        max_redirects=5,
        transport=SafeTransport(),
    )
    try:
        r = client.get(url)
        r.raise_for_status()
        return r.text[:8000]
    except httpx.HTTPStatusError as e:
        print(f"[fetch_url_text] HTTP {e.response.status_code} for {url}")
        return f"[网页返回错误 {e.response.status_code}]"
    except httpx.ConnectError as e:
        print(f"[fetch_url_text] blocked: {e}")
        return "[不安全的链接，已拒绝访问]"
    except Exception as e:
        print(f"[fetch_url_text] {e}")
        return "[无法获取网页内容]"
    finally:
        client.close()


def save_item(
    item_type: str,
    content: str = "",
    filename: str = None,
    mime_type: str = None,
    ai_summary: str = "",
) -> int:
    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO items (type, content, filename, mime_type, ai_summary, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                item_type,
                content,
                filename,
                mime_type,
                ai_summary,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host="0.0.0.0", port=5050)
