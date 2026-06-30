# Simplicity Life

AI 驱动的智能日程管理 App。支持自然语言、图片、语音、链接多种输入方式，一键提取并确认日程。

## 功能

- **Day/Week/Month/Year 四视图** — 时间线、时间块纵轴、日历网格、年概览
- **AI 日程提取** — 文字输入、图片识别、链接分析、语音输入（阿里通义千问）
- **手动添加** — 多事件卡片、时间选择器、优先级、地点、会议链接
- **提醒引擎** — 单次/循环提醒
- **中英文切换** — 完整 i18n 覆盖
- **深色/浅色模式**
- **数据导入导出** — JSON 备份

## 技术栈

- [Flask](https://flask.palletsprojects.com/) 后端（`app.py`）
- [阿里云百炼 DashScope API](https://dashscope.aliyun.com) — qwen-plus（文字）、qwen-vl-max（图片）、qwen-audio-turbo（语音）
- SQLite 本地存储（`data/items.db`）
- Tailwind CSS（CDN）
- 原生 JavaScript（`static/js/app.js`、`static/js/i18n.js`）

## 部署

```bash
pip install -r requirements.txt
echo "ALIYUN_API_KEY=sk-..." > .env
python app.py
```

打开 `http://localhost:5050`。

## 安全

- AI 接口按 IP 限流（突发 10，持续 12/分钟）
- 链接抓取做了 SSRF 防护（拒绝私有 IP、回环、链路本地地址）
- 批量删除接口要求 `X-Confirm: DELETE_ALL` 头
- 所有 AI 调用有 try/except，失败返回 502 而非 500
- 数据库连接全部走 context manager，异常时不会泄漏
