# Simplicity Life

AI 驱动的智能日程管理 App。支持自然语言、图片、语音、链接多种输入方式，一键提取并确认日程。

## 功能

- **Day/Week/Month/Year 四视图** — 时间线、时间块纵轴、日历网格、年概览
- **AI 日程提取** — 文字输入、图片识别（阿里通义千问 qwen-vl-max）、链接分析、语音输入
- **手动添加** — 多事件卡片、时间选择器、优先级（红/黄/绿）、地点导航、会议链接
- **提醒引擎** — 单次/循环提醒，系统通知 + 提示音
- **中英文切换** — 完整 i18n 覆盖
- **深色/浅色模式**
- **数据导入导出** — JSON 备份

## 技术栈

- 纯前端单页应用 (SPA)，一个 `index.html` 即可运行
- [Tailwind CSS](https://tailwindcss.com) CDN
- [阿里云百炼 DashScope API](https://dashscope.aliyun.com) — qwen-vl-max / qwen-plus
- 浏览器 Web Speech API 语音识别
- localStorage 本地数据存储

## 部署

已部署于 [Cloudflare Pages](https://simplicity-life.pages.dev)，直接访问即可使用。内置默认 API Key，开箱即用 AI 功能。

也可本地打开：双击 `index.html`。
