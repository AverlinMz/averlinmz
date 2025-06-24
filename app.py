import streamlit as st
import difflib
import random
from html import escape

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Page config
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS styling
st.markdown("""
<style>
/* Reset Streamlit default styles */
.stApp { padding: 0 !important; margin: 0 !important; }
header, footer { display: none !important; }
#MainMenu, .css-1v3fvcr { visibility: hidden !important; }

/* Container styling */
.chat-container {
    display: flex; flex-direction: column;
    max-width: 900px; margin: 0 auto;
    padding: 20px; box-sizing: border-box;
}

/* Title */
.title-container {
    text-align: center; padding-bottom: 10px; background: white;
    font-family: 'Poppins', sans-serif; font-weight: 600;
}
.title-container h1 { color: black; margin: 0; }

/* Input area */
.input-area {
    display: flex; gap: 10px;
    padding: 10px 0 20px 0; background: white;
}
.input-area input {
    flex-grow: 1; padding: 14px 18px; font-size: 16px;
    border: 2px solid #ddd; border-radius: 30px;
    outline: none; transition: border-color 0.3s;
    font-family: 'Poppins', sans-serif;
}
.input-area input:focus { border-color: #3CA887; }
.input-area button {
    padding: 14px 24px; font-size: 16px;
    border: none; border-radius: 30px;
    background-color: #3CA887; color: white;
    cursor: pointer; transition: background-color 0.3s;
    font-family: 'Poppins', sans-serif; font-weight: 500;
}
.input-area button:hover { background-color: #2E7D6F; }

/* Chat window */
.chat-window {
    flex-grow: 1; overflow-y: auto; max-height: 60vh;
    padding: 15px; display: flex; flex-direction: column-reverse;
    gap: 15px;
}

/* Message bubbles full-width */
.user,
.bot {
    align-self: center;
    width: 100%;       /* fill the entire container width */
}
.user {
    background-color: #D1F2EB; color: #0B3D2E;
    padding: 12px 16px; border-radius: 18px 18px 4px 18px;
    font-family: 'Poppins', sans-serif;
    word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.bot {
    background-color: #EFEFEF; color: #333;
    padding: 12px 16px; border-radius: 18px 18px 18px 4px;
    font-family: 'Poppins', sans-serif;
    word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Scrollbar */
.chat-window::-webkit-scrollbar { width: 8px; }
.chat-window::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb:hover { background: #a1a1a1; }
</style>
""", unsafe_allow_html=True)

# Auto-scroll JS
st.markdown("""
<script>
function scrollToBottom() {
    const w = document.querySelector('.chat-window');
    if (w) w.scrollTop = w.scrollHeight;
}
window.onload = scrollToBottom;
new MutationObserver(scrollToBottom).observe(
    document.querySelector('.chat-window'),
    { childList: true, subtree: true }
);
</script>
""", unsafe_allow_html=True)

# Full response set
RESPONSES = {
    "introduction": {
        "keywords": ["introduce","who are you","your name","about you","creator","who made you"],
        "reply": "Hello! I'm AverlinMz, your study chatbot 🌱. My creator is Aylin Muzaffarli (b.2011, Azerbaijan). She loves music, programming, robotics, AI, physics, and more. Reach her at muzaffaraylin@gmail.com. Good luck!"
    },
    # … include all your other response entries here …
    "study_smart": {
        "keywords": ["smart","study plan","study smarter"],
        "reply": "Study smart: active recall, spaced repetition, and high-impact topics."
    }
}

FALLBACK_REPLIES = [
    "Keep going 💪. Every small effort counts!",
    "Progress > perfection—you're doing great!",
    "Believe in your growth. One step at a time.",
    "You've got this 🌟. Keep moving forward.",
    "Struggle means growth. Be patient with yourself.",
]

def contains_keyword(msg, keywords, cutoff=0.75):
    msg = msg.lower()
    for kw in keywords:
        if kw in msg:
            return True
        for w in msg.split():
            if difflib.SequenceMatcher(None, w, kw).ratio() >= cutoff:
                return True
    return False

def generate_reply(user_msg):
    lm = user_msg.lower()
    for data in RESPONSES.values():
        if contains_keyword(lm, data["keywords"]):
            return data["reply"]
    # … any multi-key logic …
    return random.choice(FALLBACK_REPLIES)

# Render UI

# Title
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

# Input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "message_input",
        placeholder="Write your message…",
        key="input_field",
        label_visibility="collapsed"
    )
    submit = st.form_submit_button("Send")
    if submit and user_input.strip():
        st.session_state.messages.append({"role":"user","content":user_input})
        st.session_state.messages.append({"role":"bot","content":generate_reply(user_input)})

# Chat window
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
for msg in reversed(st.session_state.messages):
    text = escape(msg["content"])
    cls = "user" if msg["role"]=="user" else "bot"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)
