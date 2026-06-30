// ── i18n Translations ───────────────────────────────────────
const I18N = {
    zh: {
        // Nav
        "nav.home": "首页",
        "nav.ai_add": "AI 添加",
        "nav.profile": "我的",

        // Home page
        "home.today": "今天",
        "home.this_week": "本周",
        "home.day": "日",
        "home.week": "周",
        "home.month": "月",
        "home.year": "年",
        "home.add_with_ai": "AI 添加",
        "home.add_subtitle": "语音、图片、链接或文字",
        "home.loading": "加载中...",
        "home.nothing": "暂无内容",
        "home.add_something": "去添加",
        "home.tap_to_edit": "点击编辑详情",
        "home.failed": "加载失败",

        // Edit modal
        "edit.title": "编辑事件",
        "edit.event_title": "事件标题",
        "edit.date": "日期",
        "edit.time": "时间",
        "edit.location": "地点",
        "edit.meeting_link": "会议链接",
        "edit.reminder": "提醒",
        "edit.once": "单次",
        "edit.recurring": "循环",
        "edit.priority": "优先级",
        "edit.low": "低",
        "edit.med": "中",
        "edit.high": "高",
        "edit.notes": "备注",
        "edit.delete": "删除",
        "edit.save": "保存",
        "edit.add_location": "添加地点...",
        "edit.add_link": "添加链接...",
        "edit.event_placeholder": "输入事件标题...",
        "edit.time_placeholder": "例如 9:00 AM - 10:00 AM",
        "edit.notes_placeholder": "添加备注...",

        // Delete confirm
        "edit.delete_confirm": "确认删除此事件？",

        // Add page - AI mode
        "add.ai_title": "AI 助手",
        "add.add_to_life": "添加到你的生活",
        "add.ai_subtitle": "记录细节，让 AI 帮你组织和安排。",
        "add.voice_note": "语音笔记",
        "add.voice_speak": "说出你的想法，解放双手",
        "add.voice_recording": "录音中...",
        "add.voice_tap_stop": "点击停止",
        "add.upload_image": "上传图片",
        "add.image_subtitle": "海报、门票、截图",
        "add.paste_link": "粘贴链接",
        "add.link_subtitle": "文章、邀请、地点",
        "add.text_placeholder": "或直接输入...",
        "add.ai_analysis": "AI 分析",
        "add.processing_voice": "正在处理语音...",
        "add.analyzing_image": "正在分析图片...",
        "add.analyzing_link": "正在分析链接...",
        "add.thinking": "思考中...",
        "add.network_error": "网络错误，服务器是否在运行？",
        "add.mic_denied": "无法访问麦克风，请在浏览器设置中允许麦克风权限。",

        // Add page - Manual mode
        "add.manual_title": "手动添加",
        "add.review_details": "确认详情",
        "add.review_subtitle": "请确认新日程的详细信息。",
        "add.confirm_add": "确认 %d &amp; 添加到日程",
        "add.cancel": "取消",
        "add.no_title": "请输入事件标题。",
        "add.added_success": "%d 个事件已添加！前往首页查看时间线。",
        "add.add_failed": "添加失败，服务器是否在运行？",

        // Manual card fields
        "manual.event_title": "事件标题",
        "manual.date": "日期",
        "manual.time": "时间",
        "manual.location": "地点",
        "manual.meeting_link": "会议链接",
        "manual.reminder": "提醒",
        "manual.once": "单次",
        "manual.recurring": "循环",
        "manual.priority": "优先级",
        "manual.low": "低",
        "manual.med": "中",
        "manual.high": "高",
        "manual.notes": "备注",
        "manual.title_placeholder": "输入事件标题...",
        "manual.time_placeholder": "例如 9:00 AM - 10:00 AM",
        "manual.location_placeholder": "添加地点...",
        "manual.link_placeholder": "添加会议链接...",
        "manual.notes_placeholder": "添加备注...",
        "manual.daily": "每天",

        // Profile page
        "profile.settings": "设置",
        "profile.local_mode": "本地模式",
        "profile.edit_profile": "编辑资料",
        "profile.language": "语言",
        "profile.english": "English",
        "profile.chinese": "简体中文",
        "profile.appearance": "外观",
        "profile.light": "浅色",
        "profile.dark": "深色",
        "profile.notifications": "通知",
        "profile.push_title": "推送通知",
        "profile.push_desc": "每日提醒和警报",
        "profile.email_title": "邮件更新",
        "profile.email_desc": "每周摘要和新闻",
        "profile.ai_prefs": "AI 偏好",
        "profile.ai_desc": "配置 AI 如何协助你完成日常任务和日程优化。",
        "profile.ai_manage": "管理 AI 设置",
        "profile.data_sync": "数据同步",
        "profile.auto": "自动",
        "profile.last_synced": "上次同步",
        "profile.just_now": "刚刚",
        "profile.sync_info1": "使用导出功能将数据保存为 JSON 文件。使用导入功能从备份恢复。",
        "profile.sync_info2": "跨所有设备同步日程。",
        "profile.export_data": "导出数据",
        "profile.clear_data": "清空数据",
        "profile.clear_confirm": "删除所有数据？此操作不可撤销。",
        "profile.clear_failed": "清空数据失败。",

        // Month page
        "month.today_btn": "今天",

        // General
        "general.loading": "加载中...",
    },

    en: {
        // Nav
        "nav.home": "Home",
        "nav.ai_add": "AI Add",
        "nav.profile": "Profile",

        // Home page
        "home.today": "Today",
        "home.this_week": "This Week",
        "home.day": "Day",
        "home.week": "Week",
        "home.month": "Month",
        "home.year": "Year",
        "home.add_with_ai": "Add with AI",
        "home.add_subtitle": "Voice, image, link, or text",
        "home.loading": "Loading...",
        "home.nothing": "Nothing here yet.",
        "home.add_something": "Add something",
        "home.tap_to_edit": "Tap to edit details",
        "home.failed": "Failed to load items.",

        // Edit modal
        "edit.title": "Edit Event",
        "edit.event_title": "Event Title",
        "edit.date": "Date",
        "edit.time": "Time",
        "edit.location": "Location",
        "edit.meeting_link": "Meeting Link",
        "edit.reminder": "Reminder",
        "edit.once": "One-time",
        "edit.recurring": "Recurring",
        "edit.priority": "Priority",
        "edit.low": "Low",
        "edit.med": "Med",
        "edit.high": "High",
        "edit.notes": "Notes",
        "edit.delete": "Delete",
        "edit.save": "Save Changes",
        "edit.add_location": "Add location...",
        "edit.add_link": "Add meeting link...",
        "edit.event_placeholder": "Enter event title...",
        "edit.time_placeholder": "e.g. 9:00 AM - 10:00 AM",
        "edit.notes_placeholder": "Add notes...",

        // Delete confirm
        "edit.delete_confirm": "Delete this event?",

        // Add page - AI mode
        "add.ai_title": "AI Assistant",
        "add.add_to_life": "Add to your life",
        "add.ai_subtitle": "Capture the details. Let AI handle the organization and scheduling.",
        "add.voice_note": "Voice Note",
        "add.voice_speak": "Speak your mind, hands-free",
        "add.voice_recording": "Recording...",
        "add.voice_tap_stop": "Tap to stop",
        "add.upload_image": "Upload Image",
        "add.image_subtitle": "Posters, tickets, screenshots",
        "add.paste_link": "Paste Link",
        "add.link_subtitle": "Articles, invites, locations",
        "add.text_placeholder": "Or just type it here...",
        "add.ai_analysis": "AI Analysis",
        "add.processing_voice": "Processing voice note...",
        "add.analyzing_image": "Analyzing image...",
        "add.analyzing_link": "Analyzing link...",
        "add.thinking": "Thinking...",
        "add.network_error": "Network error. Is the server running?",
        "add.mic_denied": "Microphone access denied. Please allow microphone permissions.",

        // Add page - Manual mode
        "add.manual_title": "Add by yourself",
        "add.review_details": "Review Details",
        "add.review_subtitle": "Please confirm the details of your new schedule item.",
        "add.confirm_add": "Confirm %d &amp; Add to Schedule",
        "add.cancel": "Cancel",
        "add.no_title": "Please enter an event title.",
        "add.added_success": "%d event(s) added! Go to Home to see your timeline.",
        "add.add_failed": "Failed to add event. Is the server running?",

        // Manual card fields
        "manual.event_title": "Event Title",
        "manual.date": "Date",
        "manual.time": "Time",
        "manual.location": "Location",
        "manual.meeting_link": "Meeting Link",
        "manual.reminder": "Reminder",
        "manual.once": "One-time",
        "manual.recurring": "Recurring",
        "manual.priority": "Priority",
        "manual.low": "Low",
        "manual.med": "Med",
        "manual.high": "High",
        "manual.notes": "Notes",
        "manual.title_placeholder": "Enter event title...",
        "manual.time_placeholder": "e.g. 9:00 AM - 10:00 AM",
        "manual.location_placeholder": "Add location...",
        "manual.link_placeholder": "Add meeting link...",
        "manual.notes_placeholder": "Add notes...",
        "manual.daily": "Daily",

        // Profile page
        "profile.settings": "Settings",
        "profile.local_mode": "Local Mode",
        "profile.edit_profile": "Edit Profile",
        "profile.language": "Language",
        "profile.english": "English",
        "profile.chinese": "简体中文 (Chinese)",
        "profile.appearance": "Appearance",
        "profile.light": "Light",
        "profile.dark": "Dark",
        "profile.notifications": "Notifications",
        "profile.push_title": "Push Notifications",
        "profile.push_desc": "Daily reminders and alerts",
        "profile.email_title": "Email Updates",
        "profile.email_desc": "Weekly summaries and news",
        "profile.ai_prefs": "AI Preferences",
        "profile.ai_desc": "Configure how the AI assists you with daily tasks and schedule optimization.",
        "profile.ai_manage": "Manage AI Settings",
        "profile.data_sync": "Data Sync",
        "profile.auto": "Automatic",
        "profile.last_synced": "Last synced",
        "profile.just_now": "Just now",
        "profile.sync_info1": "Use Export to save your data as a JSON file. Use Import to restore from a backup.",
        "profile.sync_info2": "Synchronize schedules across all your devices.",
        "profile.export_data": "Export Data",
        "profile.clear_data": "Clear All Data",
        "profile.clear_confirm": "Delete all data? This cannot be undone.",
        "profile.clear_failed": "Failed to clear data.",

        // Month page
        "month.today_btn": "Today",

        // General
        "general.loading": "Loading...",
    }
};

// ── Current Language ───────────────────────────────────────
let currentLang = localStorage.getItem('lang') || 'zh';

function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    applyI18n();
}

// ── Theme Toggle ───────────────────────────────────────────
let currentTheme = localStorage.getItem('theme') || 'light';

function setTheme(theme) {
    currentTheme = theme;
    localStorage.setItem('theme', theme);
    applyTheme();
}

function applyTheme() {
    if (currentTheme === 'dark') {
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
    } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
    }
    document.dispatchEvent(new CustomEvent('theme-updated', { detail: { theme: currentTheme } }));
}

// Apply theme on load
applyTheme();

function t(key) {
    if (I18N[currentLang] && I18N[currentLang][key]) return I18N[currentLang][key];
    if (I18N['en'] && I18N['en'][key]) return I18N['en'][key];
    if (typeof console !== 'undefined') console.warn('[i18n] missing key:', key);
    return key;
}

function applyI18n() {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const text = t(key);
        if (text) el.textContent = text;
    });

    // Update all elements with data-i18n-placeholder attribute
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        const text = t(key);
        if (text) el.placeholder = text;
    });

    // Update HTML lang attribute
    document.documentElement.lang = currentLang === 'zh' ? 'zh-CN' : 'en';

    // Trigger custom event for dynamic content
    document.dispatchEvent(new CustomEvent('i18n-updated', { detail: { lang: currentLang } }));
}

// Apply on load
document.addEventListener('DOMContentLoaded', applyI18n);
