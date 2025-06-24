import streamlit as st
import random
import difflib
from html import escape

# — Page config for full-width layout —
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# — CSS and JS for auto-scroll and styling —
st.markdown("""
<style>
body, .css-18e3th9 {  /* streamlit main container */
    padding: 0;
    margin: 0;
    background-color: #F7F9FA;
}
header, footer { display: none; }  /* hide header/footer */
#MainMenu, .css-1v3fvcr { visibility: hidden; }  /* hide menu bar */

.chat-window {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 60px;  /* leave space for input */
    overflow-y: auto;
    padding: 20px;
    box-sizing: border-box;
}
.chat-container {
    display: flex;
    flex-direction: column-reverse;  /* newest first */
    gap: 12px;
    max-width: 800px;
    margin: auto;
}
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
.input-area {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    padding: 10px 20px;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 10px;
    box-sizing: border-box;
}
.input-area input[type="text"] {
    flex-grow: 1;
    padding: 12px 16px;
    font-size: 16px;
    border: 2px solid #ccc;
    border-radius: 25px;
    outline: none;
    box-sizing: border-box;
    transition: border-color 0.3s ease;
}
.input-area input[type="text"]:focus {
    border-color: #3CA887; /* green highlight on focus */
}
.input-area button {
    padding: 12px 20px;
    font-size: 16px;
    border: none;
    border-radius: 25px;
    background-color: #3CA887;
    color: white;
    cursor: pointer;
    transition: background-color 0.3s ease;
}
.input-area button:hover {
    background-color: #2E7D6F;
}
input, button {
    font-family: 'Poppins', sans-serif;
}
</style>

<script>
// Auto-scroll to bottom on new message
window.addEventListener('load', () => {
    const chatWindow = document.querySelector('.chat-window');
    chatWindow.scrollTop = chatWindow.scrollHeight;
});
</script>
""", unsafe_allow_html=True)

# — Title (black color) —
st.markdown("<h1 style='color: black; text-align: center; font-family: Poppins;'>AverlinMz – Study Chatbot</h1>", unsafe_allow_html=True)

# — Initialize chat history —
if "messages" not in st.session_state:
    st.session_state.messages = []

# — Predefined responses (organized for maintainability) —
RESPONSES = {
    "introduction": {
        "keywords": ["introduce", "who are you", "your name", "about you", "creator", "who made you"],
        "reply": "Hello! I’m AverlinMz, your study chatbot 🌱. My creator is Aylin Muzaffarli (b.2011, Azerbaijan). She loves music, programming, robotics, AI, physics, and more. Reach her at muzaffaraylin@gmail.com. Good luck!"
    },
    "capabilities": {
        "keywords": ["what can you do", "what you can do", "what can u do"],
        "reply": "I can cheer you on, share study tips (general or subject-specific!), and offer emotional support. Chat anytime you need a boost!"
    },
    "olympiad_tips": {
        "keywords": ["olymp", "olympuad", "tip", "tips", "advise", "advice"],
        "reply": "Olympiad tips 💡: Study smart—focus on core concepts, practice past problems, review mistakes, and balance work with rest. Quality > quantity!"
    },
    # Add more categories here...
}

# Fallback replies if no keyword matches
FALLBACK_REPLIES = [
    "Keep going 💪. Every small effort counts.",
    "Progress > perfection—you’re doing great!",
    "Believe in your growth. One step at a time.",
]

# — Fuzzy keyword helper —
def contains_keyword(msg, keywords, cutoff=0.75):
    msg = msg.lower()
    words = msg.split()
    for kw in keywords:
        if kw in msg:
            return True
        for w in words:
            if difflib.SequenceMatcher(None, w, kw).ratio() >= cutoff:
                return True
    return False

# — Reply logic (optimized) —
def generate_reply(user_msg):
    user_msg = user_msg.lower()
    
    # Check predefined responses
    for category, data in RESPONSES.items():
        if contains_keyword(user_msg, data["keywords"]):
            return data["reply"]
    
    # Subject-specific tips (add more as needed)
    if contains_keyword(user_msg, ["biology"]) and contains_keyword(user_msg, ["tip", "tips"]):
        return "Biology 🧬: Master cell structure, genetics, and ecology. Draw diagrams, use flashcards, and practice Olympiad questions."
    
    # Emotional support
    if contains_keyword(user_msg, ["sad", "down", "depressed"]):
        return "I’m sorry you’re feeling down 💙. Your feelings are valid, and I’m here with you."
    
    # Fallback
    return random.choice(FALLBACK_REPLIES)

# — Chat input (fixed at bottom) —
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder="Write your message…", key="input_field")
    send = st.form_submit_button("Send")
    
    if send and user_input.strip():
        # Add to history (with XSS protection via escape())
        st.session_state.messages.insert(0, {"role": "bot", "content": generate_reply(user_input)})
        st.session_state.messages.insert(0, {"role": "user", "content": user_input})

# — Render chat messages —
st.markdown('<div class="chat-window">', unsafe_allow_html=True)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user">{escape(msg["content"])}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{escape(msg["content"])}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
