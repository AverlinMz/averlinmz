import streamlit as st
import difflib
import random
import time
import string
from html import escape

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "typing" not in st.session_state:
    st.session_state.typing = False

if "last_bot_reply" not in st.session_state:
    st.session_state.last_bot_reply = ""

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
.stApp { padding: 0 !important; margin: 0 !important; }
header, footer { display: none !important; }
#MainMenu, .css-1v3fvcr { visibility: hidden !important; }

.chat-container {
    display: flex; flex-direction: column;
    max-width: 900px; margin: 0 auto;
    padding: 20px; box-sizing: border-box;
}

.title-container {
    text-align: center; padding-bottom: 10px; background: white;
    font-family: 'Poppins', sans-serif; font-weight: 600;
}
.title-container h1 { color: black; margin: 0; }

.chat-window {
    flex-grow: 1; overflow-y: auto; max-height: 60vh;
    padding: 15px; display: flex; flex-direction: column-reverse;
    gap: 15px;
}

.user,
.bot {
    align-self: center;
    width: 100%;
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

# Title
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

RESPONSE_DATA = {
    "greetings": [
        "Hello there! 👋 How’s your day going? Ready to dive into learning today?",
        "Hey hey! 🌟 Hope you’re feeling inspired today. What’s on your mind?",
        "Hi friend! 😊 I’m here for you — whether you want to study, vent, or just chat."
    ],
    "study_tips": [
        "Here are some smart study strategies:\n1. Use active recall — test yourself often.\n2. Practice spaced repetition — revisit content over time.\n3. Avoid multitasking — focus deeply for short bursts.\n4. Teach the material — it reveals your blind spots.\nYou’ve got this! 🌟🚀",
        "Study smarter, not harder! Plan with intention, set small goals, reward progress, and take breaks. Consistency wins! 📊🙌"
    ],
    "emotional_support": [
        "Feeling overwhelmed? 😔 It’s okay. Take a deep breath. Rest is part of the process. I’m here with you. 🌈",
        "Mistakes happen — they’re how we grow. Progress isn’t linear, and every step counts. Keep going. You matter. ✨"
    ],
    "capabilities": [
        "I'm AverlinMz, your friendly study buddy! 🌟 I can give subject tips, study advice, encouragement, and help you stay on track. Think of me like a super-charged school companion."
    ],
    "subjects": [
        "Math: ✅ Focus on solving problems, not just memorizing formulas. Understand the *why*, not just the *how*. Break problems down and revisit your mistakes.",
        "Physics: ✨ Build strong intuition. Use visualizations and diagrams. Try explaining concepts aloud or simulating with tools like VPython!",
        "Chemistry: 🔮 Understand periodic trends, bonding principles, and reactions deeply. Practice balancing equations and visualizing molecular structures.",
        "Biology: 🧬 Create concept maps. Focus on big systems (like cells and genetics). Draw diagrams and explain aloud.",
        "Computer Science: 🪡 Learn by building! Solve small coding problems daily. Read others' code. Comment your logic and debug step by step."
    ],
    "intro": [
        "Hi there! I’m AverlinMz 🤖, your AI-powered chatbot friend. Created by Aylin Müzaffərli from Azerbaijan, I love helping students learn, stay motivated, and feel supported."
    ],
    "quote": [
        "“Success is the sum of small efforts, repeated day in and day out.” — Robert Collier 🚀",
        "“Believe you can and you're halfway there.” — Theodore Roosevelt 🌟"
    ],
    "fallback": [
        "Hmm 🤔 That one’s tricky. I’m still learning. Try asking differently? Or ask about studying, feelings, or a subject you love!",
        "I'm best at giving advice, support, and tips! Think of me more like a buddy than a textbook. 🪡"
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey"],
    "study_tips": ["study", "tips", "advice", "plan"],
    "emotional_support": ["tired", "sad", "burnout", "overwhelmed"],
    "capabilities": ["what can you do", "how can you help"],
    "subjects": ["math", "physics", "chemistry", "biology", "computer science"],
    "intro": ["introduce", "who are you"],
    "quote": ["quote", "inspire", "motivation"]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    replies = []
    for key, words in KEYWORDS.items():
        if any(word in msg for word in words):
            replies.append(random.choice(RESPONSE_DATA[key]))
    return "\n\n".join(replies) if replies else random.choice(RESPONSE_DATA["fallback"])

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
        st.session_state.messages.append({"role": "user", "content": user_input})
        reply = get_bot_reply(user_input)
        st.session_state.last_bot_reply = reply
        st.session_state.messages.append({"role": "bot", "content": None})
        st.session_state.typing = True

# Render chat window
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)

# Display all messages
pairs = []
msgs = st.session_state.messages
for i in range(0, len(msgs), 2):
    if i + 1 < len(msgs):
        pairs.append((msgs[i], msgs[i+1]))

pairs.reverse()

for user_msg, bot_msg in pairs:
    st.markdown(f'<div class="user">{escape(user_msg["content"]).replace("\n","<br>")}</div>', unsafe_allow_html=True)
    if bot_msg["content"] is None:
        container = st.empty()
        if st.session_state.typing:
            container.markdown('<div class="bot">🤖 Typing...</div>', unsafe_allow_html=True)
            time.sleep(2)
            container.markdown(f'<div class="bot">{escape(st.session_state.last_bot_reply).replace("\n","<br>")}</div>', unsafe_allow_html=True)
            for i in range(len(st.session_state.messages) - 1, -1, -1):
                if st.session_state.messages[i]["role"] == "bot" and st.session_state.messages[i]["content"] is None:
                    st.session_state.messages[i]["content"] = st.session_state.last_bot_reply
                    break
            st.session_state.typing = False
        else:
            container.markdown(f'<div class="bot">{escape(bot_msg["content"]).replace("\n","<br>")}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{escape(bot_msg["content"]).replace("\n","<br>")}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
