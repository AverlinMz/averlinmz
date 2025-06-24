import streamlit as st
import random
import difflib

# — Page config for full-width layout —
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# — CSS for full-screen chat, bubbles & input area —
st.markdown("""
<style>
/* Hide Streamlit UI */
header, footer { display: none !important; }
#MainMenu, .css-1v3fvcr { visibility: hidden !important; }

/* Title styling */
h1 {
    margin: 0;
    padding: 20px 0;
    text-align: center;
    font-family: 'Poppins', sans-serif;
    font-weight: bold;
    color: #000000;
}

/* Full-screen chat window */
.chat-window {
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    bottom: 100px;  /* leave room for input */
    overflow-y: auto;
    padding: 20px 0;
    background-color: #F7F9FA;
    box-sizing: border-box;
}

/* Container for messages, newest first */
.chat-container {
    display: flex;
    flex-direction: column-reverse;
    gap: 12px;
    max-width: 800px;
    margin: auto;
}

/* User bubble */
.user {
    align-self: flex-end;
    background-color: #D1F2EB;
    color: #0B3D2E;
    padding: 10px 14px;
    border-radius: 16px 16px 4px 16px;
    font-family: 'Poppins', sans-serif;
    max-width: 80%;
    word-wrap: break-word;
}

/* Bot bubble */
.bot {
    align-self: flex-start;
    background-color: #EFEFEF;
    color: #333333;
    padding: 10px 14px;
    border-radius: 16px 16px 16px 4px;
    font-family: 'Poppins', sans-serif;
    max-width: 80%;
    word-wrap: break-word;
}

/* Input area fixed at bottom */
.input-area {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #FFFFFF;
    padding: 10px 20px;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 8px;
    box-sizing: border-box;
}
</style>
""", unsafe_allow_html=True)

# — Title —
st.markdown("<h1>AverlinMz – Study Chatbot</h1>", unsafe_allow_html=True)

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Helper: fuzzy-match keyword
def contains_keyword(msg, keywords, cutoff=0.75):
    words = msg.split()
    for kw in keywords:
        if kw in msg:
            return True
        for w in words:
            if difflib.SequenceMatcher(None, w, kw).ratio() >= cutoff:
                return True
    return False

# Full bot reply logic
def generate_reply(user_msg):
    msg = user_msg.lower()
    # ... (same logic as before) ...
    replies = [
        "Keep going 💪. Every small effort counts.",
        "Progress > perfection—you’re doing great!",
        "Believe in your growth—one step at a time.",
        "You’ve got this 🌟. Keep moving forward.",
        "Struggle means growth. Be patient with yourself."
    ]
    return random.choice(replies)

# — Render chat bubbles in full-screen window —
st.markdown('<div class="chat-window"><div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if "user" in msg:
        st.markdown(f'<div class="user">{msg["user"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{msg["bot"]}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# — Chat input form (Enter to send) —
st.markdown('<div class="input-area">', unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder="Write your message…")
    send = st.form_submit_button("Send")
    if send and user_input.strip():
        # insert user then bot reply
        st.session_state.messages.insert(0, {"user": user_input})
        st.session_state.messages.insert(0, {"bot": generate_reply(user_input)})
st.markdown('</div>', unsafe_allow_html=True)
