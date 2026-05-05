// ── Voice Recording ──────────────────────────────────────────
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

async function startVoice() {
    if (isRecording) { stopRecording(); return; }
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm';
        mediaRecorder = new MediaRecorder(stream, { mimeType });
        audioChunks = [];
        mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) audioChunks.push(e.data); };
        mediaRecorder.onstop = async () => { stream.getTracks().forEach(t => t.stop()); const blob = new Blob(audioChunks, { type: mimeType }); await sendVoice(blob); };
        mediaRecorder.start();
        isRecording = true;
        updateVoiceUI(true);
    } catch (err) { alert(t('add.mic_denied')); }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') mediaRecorder.stop();
    isRecording = false;
    updateVoiceUI(false);
}

function updateVoiceUI(recording) {
    const icon = document.getElementById('voice-icon');
    const label = document.getElementById('voice-label');
    const status = document.getElementById('voice-status');
    const btn = document.getElementById('btn-voice');
    if (recording) {
        icon.textContent = 'stop';
        label.setAttribute('data-i18n','add.voice_recording'); label.textContent = t('add.voice_recording');
        status.setAttribute('data-i18n','add.voice_tap_stop'); status.textContent = t('add.voice_tap_stop');
        btn.classList.add('animate-pulse'); btn.style.background = '#ba1a1a';
    } else {
        icon.textContent = 'mic';
        label.setAttribute('data-i18n','add.voice_note'); label.textContent = t('add.voice_note');
        status.setAttribute('data-i18n','add.voice_speak'); status.textContent = t('add.voice_speak');
        btn.classList.remove('animate-pulse'); btn.style.background = '';
    }
}

async function sendVoice(blob) {
    showResult(t('add.processing_voice'));
    const fd = new FormData(); fd.append('audio', blob, 'recording.webm');
    try { const r = await fetch('/api/process/voice', { method: 'POST', body: fd }); const data = await r.json(); showResult(data.error ? 'Error: ' + data.error : data.summary); }
    catch (e) { showResult(t('add.network_error')); }
}

async function uploadImage(input) {
    const file = input.files[0]; if (!file) return;
    showResult(t('add.analyzing_image'));
    const fd = new FormData(); fd.append('image', file);
    try { const r = await fetch('/api/process/image', { method: 'POST', body: fd }); const data = await r.json(); showResult(data.error ? 'Error: ' + data.error : data.summary); }
    catch (e) { showResult(t('add.network_error')); }
    input.value = '';
}

async function pasteLink() {
    let url;
    try { const text = await navigator.clipboard.readText(); url = /^https?:\/\/\S+/.test(text) ? text : prompt(t('add.paste_link'), text); }
    catch { url = prompt(t('add.paste_link')); }
    if (!url) return;
    if (!url.startsWith('http')) url = 'https://' + url;
    showResult(t('add.analyzing_link'));
    try { const r = await fetch('/api/process/link', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url }) }); const data = await r.json(); showResult(data.error ? 'Error: ' + data.error : data.summary); }
    catch (e) { showResult(t('add.network_error')); }
}

async function sendText() {
    const textarea = document.getElementById('text-input');
    const text = textarea.value.trim(); if (!text) return;
    showResult(t('add.thinking'));
    textarea.value = '';
    try { const r = await fetch('/api/process/text', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) }); const data = await r.json(); showResult(data.error ? 'Error: ' + data.error : data.summary); }
    catch (e) { showResult(t('add.network_error')); }
}

function showResult(text) {
    const panel = document.getElementById('result-panel');
    const content = document.getElementById('result-content');
    panel.classList.remove('hidden');
    content.textContent = text;
    panel.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
function closeResult() { document.getElementById('result-panel').classList.add('hidden'); }

document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('text-input');
    if (textarea) { textarea.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendText(); } }); }
});
