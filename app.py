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
    "introduction": [
        "I’m AverlinMz, your supportive study companion built with 💡 by Aylin Muzaffarli. I help with study strategies, emotional support, and academic motivation!"
    ],
    "capabilities": [
        "I’m here to guide, motivate, and support you with study tips, emotional encouragement, subject-specific advice, and more. Think of me as your academic partner, not just a chatbot!"
    ],
    "study_tips": [
        "📚 Study Smarter:
1. Use active recall – quiz yourself often.
2. Apply spaced repetition – review over time.
3. Eliminate distractions – one task at a time.
4. Teach others – best way to learn.
5. Use visuals – mind maps, charts.
6. Rest intentionally – avoid burnout.
You've got this! 💪✨"
    ],
    "emotional_support": [
        "😔 Feeling overwhelmed? It's totally okay. Rest, breathe, and remember you're not alone. I'm here to support you. You’re doing better than you think. 🌈",
        "Burnout hits hard, but breaks restore clarity. Step back, hydrate, stretch. You deserve care too. 💙"
    ],
    "motivational_quote": [
        "“The future depends on what you do today.” – Mahatma Gandhi 🌱 Keep going, your efforts matter!"
    ],
    "subjects": {
        "math": "📐 Math Advice:
1. Understand the concept, not just the formula.
2. Practice daily with variety.
3. Rework incorrect problems.
4. Study proofs to sharpen logic.
5. Explain solutions aloud.
You're solving your way to brilliance! ✨",
        "physics": "🧲 Physics Advice:
1. Master the basics – Newton’s laws, energy, motion.
2. Visualize problems through diagrams.
3. Link theory to real-world examples.
4. Derive formulas – don't memorize blindly.
5. Solve conceptually first, then numerically.
Curiosity fuels understanding! 🚀",
        "chemistry": "⚗️ Chemistry Tips:
1. Memorize key reactions and periodic trends.
2. Balance equations like puzzles.
3. Use molecular models to visualize structures.
4. Practice with reaction mechanisms.
5. Link theory to lab experience.
You're building a molecular mindset! 🧪",
        "biology": "🧬 Biology Strategy:
1. Draw and label diagrams.
2. Learn by teaching – explain processes.
3. Use flashcards for vocab and cycles.
4. Understand over memorization.
5. Study in small, repeated sessions.
Life science loves consistency! 🌿",
        "cs": "💻 Computer Science:
1. Master algorithms and data structures.
2. Code daily – even small exercises count.
3. Break problems into parts.
4. Read others’ code for inspiration.
5. Document your learning.
Debugging is discovery! 🧠💡"
    },
    "fallback": [
        "Hmm 🤔 I didn’t catch that. Could you rephrase it a bit? I’m here to help! 💬",
        "That’s a tricky one! I'm your learning ally, not a human expert — but I’ll try my best if you reword it a little."
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "good morning", "good evening"],
    "introduction": ["who are you", "introduce", "your name", "tell me about your creator"],
    "capabilities": ["what can you do", "how can you help"],
    "study_tips": ["study smarter", "how to study", "study plan", "study advice"],
    "emotional_support": ["tired", "sad", "burnout", "overwhelmed", "anxious"],
    "motivational_quote": ["quote", "motivation", "inspire"],
    "subjects": ["math", "physics", "chemistry", "biology", "computer science", "cs"]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    response = []
    for category, words in KEYWORDS.items():
        if category == "subjects":
            for subj in RESPONSE_DATA["subjects"]:
                if subj in msg:
                    response.append(RESPONSE_DATA["subjects"][subj])
        elif any(word in msg for word in words):
            if category in RESPONSE_DATA:
                response.append(random.choice(RESPONSE_DATA[category]))
    if not response:
        response.append(random.choice(RESPONSE_DATA["fallback"]))
    return "\n\n".join(response)

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
