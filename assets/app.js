const messages = document.getElementById('messages');
const form = document.getElementById('chatForm');
const input = document.getElementById('message');
const send = document.getElementById('send');

// IMPORTANT: Change this URL when you deploy! 
// e.g. const API_BASE = 'https://yourusername.pythonanywhere.com/api';
const API_BASE = 'https://navneetyadavcode.pythonanywhere.com/api';

if (window.markedKatex) marked.use(window.markedKatex({ throwOnError: false }));
function addBubble(text, who='ai') { 
    const row = document.createElement('div'); 
    row.className = 'bubble ' + who; 
    let html = ''; 
    if(who === 'ai') {
        html = DOMPurify.sanitize(marked.parse(text), {USE_PROFILES:{mathMl:true}});
    } else {
        html = '<p>' + escapeHtml(text).replace(/\n/g,'<br>') + '</p>';
    } 
    row.innerHTML = `<div class="avatar">${who === 'ai' ? 'AI' : 'You'}</div><div class="msg-content">${html}</div>`; 
    messages.appendChild(row); 
    messages.scrollTop = messages.scrollHeight; 
    return row;
}
function escapeHtml(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
document.querySelectorAll('[data-q]').forEach(b=>b.addEventListener('click',()=>{input.value=b.dataset.q;form.requestSubmit();}));

// Enter to send (Shift+Enter for new line)
input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        form.requestSubmit();
    }
});

// Load config and history on startup
async function initChatbot() {
    try {
        // We use credentials: 'include' so that PythonAnywhere sees the session cookie
        const r = await fetch(`${API_BASE}/init`, { method: 'GET', credentials: 'include' });
        const data = await r.json();
        
        if (data.success) {
            // Update UI dynamically
            document.title = `${data.institute_name} — AI Assistant`;
            const h1 = document.querySelector('.topbar h1');
            if (h1) h1.textContent = data.institute_name;
            
            // Set welcome message if history is empty
            if (!data.history || data.history.length === 0) {
                messages.innerHTML = `<div class="bubble ai"><div class="avatar">AI</div><div><p>${data.welcome_message}</p>
                <div class="chips">
                    <button data-q="What are the fees?">Fees</button>
                    <button data-q="What are the class timings?">Timings</button>
                    <button data-q="How can I take admission?">Admission</button>
                    <button data-q="Help me with a subject question">Subject help</button>
                </div></div></div>`;
                // Re-bind quick question chips
                document.querySelectorAll('.chips button').forEach(b=>b.addEventListener('click',()=>{input.value=b.dataset.q;form.requestSubmit();}));
            } else {
                messages.innerHTML = ''; // Clear default
                data.history.forEach(chat => {
                    addBubble(chat.user, 'user');
                    addBubble(chat.ai, 'ai');
                });
            }
        }
    } catch (err) {
        console.error("Failed to initialize chatbot. Is the backend running?", err);
    }
}
// Start initialization
initChatbot();

form.addEventListener('submit', async e => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text || send.disabled) return;
    
    addBubble(text, 'user');
    input.value = '';
    send.disabled = true;
    
    // Add typing indicator bubble
    const typingBubble = document.createElement('div');
    typingBubble.className = 'bubble ai';
    typingBubble.innerHTML = `<div class="avatar">AI</div><div class="msg-content"><div class="typing"><span></span><span></span><span></span></div></div>`;
    messages.appendChild(typingBubble);
    messages.scrollTop = messages.scrollHeight;
    
    try {
        const r = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ message: text })
        });
        const data = await r.json();
        typingBubble.remove();
        addBubble(data.success ? data.answer : (data.message || 'Sorry, something went wrong.'));
    } catch (err) {
        typingBubble.remove();
        addBubble('Unable to connect to the chatbot server. Please try again.');
    } finally {
        send.disabled = false;
        input.focus();
    }
});
