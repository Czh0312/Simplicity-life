import base64
import io
import json
import os
import sqlite3
from datetime import datetime, timezone

import httpx
from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "items.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
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
    conn.close()


init_db()


def get_ai_client():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    return Anthropic(api_key=key)


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
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    summary = call_ai_text(text)
    item_id = save_item("text", content=text, ai_summary=summary)
    return jsonify({"id": item_id, "summary": summary, "tags": []})


@app.route("/api/process/image", methods=["POST"])
def process_image():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image provided"}), 400

    mime = file.mimetype or "image/png"
    raw = file.read()

    summary = call_ai_vision(raw, mime)
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
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "No link provided"}), 400

    page_text = fetch_url_text(url)
    summary = call_ai_link(url, page_text)
    item_id = save_item("link", content=url, ai_summary=summary)
    return jsonify({"id": item_id, "summary": summary, "tags": []})


@app.route("/api/process/voice", methods=["POST"])
def process_voice():
    file = request.files.get("audio")
    if not file:
        return jsonify({"error": "No audio provided"}), 400

    raw = file.read()
    # Save audio as base64 for AI processing
    b64 = base64.b64encode(raw).decode("utf-8")
    mime = file.mimetype or "audio/webm"

    summary = call_ai_audio(b64, mime)
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
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM items ORDER BY created_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/items/<int:item_id>/complete", methods=["POST"])
def complete_item(item_id):
    conn = get_db()
    row = conn.execute("SELECT ai_tags FROM items WHERE id = ?", (item_id,)).fetchone()
    if row:
        tags = row["ai_tags"] or ""
        if "completed" in tags:
            tags = tags.replace("completed", "").replace(",", "").strip()
        else:
            tags = (tags + ",completed").strip(",")
        conn.execute("UPDATE items SET ai_tags = ? WHERE id = ?", (tags, item_id))
        conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = get_db()
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/items/<int:item_id>/update", methods=["POST"])
def update_item(item_id):
    data = request.get_json()
    conn = get_db()
    conn.execute(
        "UPDATE items SET content = ?, ai_summary = ? WHERE id = ?",
        (data.get("content", ""), data.get("ai_summary", ""), item_id),
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


# ── API: Data Export / Import ─────────────────────────────────


@app.route("/api/export")
def export_data():
    conn = get_db()
    rows = conn.execute("SELECT * FROM items ORDER BY created_at ASC").fetchall()
    conn.close()
    data = [dict(r) for r in rows]
    buf = io.BytesIO()
    buf.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
    buf.seek(0)
    filename = f"simplicity_life_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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

    conn = get_db()
    count = 0
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
    conn.close()
    return jsonify({"ok": True, "imported": count})


# ── AI Helpers ────────────────────────────────────────────────


def call_ai_text(text: str) -> str:
    client = get_ai_client()
    if not client:
        return f"[AI未配置] 你输入了: {text[:200]}"

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system="你是一个生活助手。分析用户的文字，提取关键信息（事件、时间、地点、待办事项），给出简洁的结构化摘要，并建议如何组织这些信息。用中文回复。",
        messages=[{"role": "user", "content": text}],
    )
    return resp.content[0].text


def call_ai_vision(image_bytes: bytes, mime: str) -> str:
    client = get_ai_client()
    if not client:
        return "[AI未配置] 图片已接收，但需要配置 ANTHROPIC_API_KEY 才能分析。"

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system="你是一个生活助手。分析用户上传的图片，提取其中的关键信息（活动海报、门票日期、截屏内容等），给出简洁的结构化摘要。用中文回复。",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime,
                            "data": b64,
                        },
                    },
                    {"type": "text", "text": "请分析这张图片中的信息。"},
                ],
            }
        ],
    )
    return resp.content[0].text


def call_ai_link(url: str, page_text: str) -> str:
    client = get_ai_client()
    if not client:
        return f"[AI未配置] 链接: {url}"

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system="你是一个生活助手。分析用户分享的网页链接内容，提取关键信息，给出简洁的结构化摘要。用中文回复。",
        messages=[
            {
                "role": "user",
                "content": f"链接: {url}\n\n网页内容:\n{page_text[:4000]}",
            }
        ],
    )
    return resp.content[0].text


def call_ai_audio(audio_b64: str, mime: str) -> str:
    """Process audio by sending it to Claude for transcription and analysis."""
    client = get_ai_client()
    if not client:
        return "[AI未配置] 音频已接收，但需要配置 ANTHROPIC_API_KEY 才能转写和分析。"

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system="你是一个生活助手。用户上传了一段语音。请根据音频内容进行转写和分析，提取关键信息。用中文回复。",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "source": {
                            "type": "base64",
                            "media_type": mime,
                            "data": audio_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "请转写并分析这段语音中的信息。",
                    },
                ],
            }
        ],
    )
    return resp.content[0].text


def fetch_url_text(url: str) -> str:
    try:
        r = httpx.get(url, timeout=10, follow_redirects=True)
        # Simple text extraction: just grab first 4000 chars of body
        text = r.text[:8000]
        return text
    except Exception:
        return "[无法获取网页内容]"


def save_item(
    item_type: str,
    content: str = "",
    filename: str = None,
    mime_type: str = None,
    ai_summary: str = "",
) -> int:
    conn = get_db()
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
    item_id = cur.lastrowid
    conn.close()
    return item_id


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
