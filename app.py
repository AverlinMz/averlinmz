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

# Responses organized by theme
RESPONSE_DATA = {
    "greetings": [
        "Hey there! 🌟 How’s your day going so far? Let’s make today productive!",
        "Hi! 😊 I’m so glad you stopped by. What would you like to focus on today?",
        "Hello friend! 👋 I’m always here to help you grow and achieve more."
    ],
    "introduce": [
        "I’m AverlinMz, your friendly study companion 🤖💡. Created by Aylin Muzaffarli, I’m here to support your learning journey, encourage your progress, and help you stay on track. Let’s level up together!"
    ],
    "capabilities": [
        "Here’s what I can do 🧠:
- Motivate you with kind words and real talk 💬
- Share study tips, time management tricks and exam strategies 📚
- Provide subject-specific advice: math, physics, biology and more! 🔬
- Help you stay emotionally balanced 🧘‍♀️
- Be your cheerleader through tough times and victories 🎉"
    ],
    "study_tips": [
        "Here’s how to study smart, not hard! 💡
1. Use active recall — test yourself instead of just rereading notes.
2. Do spaced repetition — review material regularly over time.
3. Eliminate distractions — study in focused sessions with full attention.
4. Teach others — explaining concepts makes them stick.
5. Reward progress — small wins deserve celebrations! 🎉"
    ],
    "subject_tips": [
        "📐 Math: Practice regularly and don’t skip proofs. Learn shortcuts, but understand the logic.",
        "🔬 Physics: Focus on concepts, not just formulas. Visualize problems and use real-world examples.",
        "🧪 Chemistry: Learn patterns in the periodic table and do experiments when possible.",
        "🧬 Biology: Draw diagrams, understand processes, and use mnemonics.",
        "💻 CS: Practice coding daily, read documentation, and build small projects."
    ],
    "emotional_support": [
        "It’s okay to feel overwhelmed. 🌧️ Take a breath, rest if needed, and come back stronger. Your journey matters. 💙",
        "Burnout is real. Step away, recharge, and remember: you’re not alone in this. 🌿 I believe in you."
    ],
    "motivation": [
        "“Success is the sum of small efforts, repeated day in and day out.” — Robert Collier 💪",
        "Every step you take is progress. Don’t stop now — your dreams need your courage! 🌈"
    ],
    "goodbye": [
        "Goodbye! 👋 Keep being awesome, and remember: I’m always here when you need me.",
        "See you soon! 🎓 Study well, rest well, live well."
    ],
    "fallback": [
        "Hmm 🤔 I’m still learning. Could you rephrase that a bit? I’ll try my best to help next time!",
        "I may not have the perfect answer yet, but I’m cheering for you anyway! 🎉 Try a different question?"
    ]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    if any(word in msg for word in ["hello", "hi", "hey", "greetings"]):
        return random.choice(RESPONSE_DATA["greetings"])
    elif "introduce" in msg or "who are you" in msg:
        return random.choice(RESPONSE_DATA["introduce"])
    elif "what can you do" in msg or "capabilities" in msg:
        return random.choice(RESPONSE_DATA["capabilities"])
    elif any(word in msg for word in ["study", "tips", "advice", "study smart"]):
        return random.choice(RESPONSE_DATA["study_tips"])
    elif any(word in msg for word in ["math", "physics", "chemistry", "biology", "computer"]):
        return random.choice(RESPONSE_DATA["subject_tips"])
    elif any(word in msg for word in ["tired", "burned", "sad", "down", "anxious", "exhausted"]):
        return random.choice(RESPONSE_DATA["emotional_support"])
    elif "quote" in msg or "inspire" in msg:
        return random.choice(RESPONSE_DATA["motivation"])
    elif any(word in msg for word in ["bye", "goodbye", "see you"]):
        return random.choice(RESPONSE_DATA["goodbye"])
    else:
        return random.choice(RESPONSE_DATA["fallback"])

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
            container.markdown(f'<div class="bot">{escape(st.session_state.last_bot_reply).replace("\n","<br>")}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{escape(bot_msg["content"]).replace("\n","<br>")}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
