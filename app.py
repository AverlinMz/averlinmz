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

# Full response set with detailed, emoji-rich replies
RESPONSES = {
    "introduction": {
        "keywords": ["introduce","who are you","your name","about you","creator","who made you"],
        "reply": "Hello! I'm AverlinMz, your study chatbot 🌱. My creator is Aylin Muzaffarli (b.2011, Azerbaijan). She loves music, programming, robotics, AI, physics, and more. Reach her at muzaffaraylin@gmail.com. Good luck! ✨"
    },
    "capabilities": {
        "keywords": ["what can you do","what you can do","what can u do","capabilities","help"],
        "reply": (
            "I’m here to cheer you on and share study tips — from biology to math and physics! 📚\n"
            "I can help you stay motivated, give advice on managing stress, and offer emotional support when things get tough ❤️.\n"
            "Think of me as your study buddy who never gets tired of your questions! 🤖✨"
        )
    },
    "olympiad_tips": {
        "keywords": ["olymp","olympuad","tip","tips","advise","advice"],
        "reply": "Olympiad tips 💡: Study smart—focus on core concepts, practice past problems, review mistakes, and balance work with rest. Quality > quantity! 🎯"
    },
    "biology_tips": {
        "keywords": ["biology","bio"],
        "reply": "Biology 🧬: Master cell structure, genetics, and ecology. Draw diagrams, use flashcards, and practice Olympiad questions. Keep your curiosity alive! 🌿"
    },
    "history_tips": {
        "keywords": ["history","hist"],
        "reply": "History 📜: Build timelines, practice structured essays, analyze sources, and quiz yourself on key dates. Connect events like a story! 📖"
    },
    "geography_tips": {
        "keywords": ["geography","geo"],
        "reply": "Geography 🌍: Interpret maps, memorize landforms, study case-studies, and practice spatial reasoning. Explore the world from your desk! 🗺️"
    },
    "language_tips": {
        "keywords": ["language","english","russian","spanish","french"],
        "reply": "Languages 🗣️: Read varied texts, listen actively, learn grammar contextually, and speak/write regularly to build fluency. Consistency is key! 🔑"
    },
    "encouragement": {
        "keywords": ["i love you","i like you"],
        "reply": "Aww, that warms my circuits! 💖 I'm here to support you anytime. Keep shining! ✨"
    },
    "greeting": {
        "keywords": ["hey","hi","hello","hrllo","helo"],
        "reply": "Hey there! What are you studying right now? Starting is half the battle—you've done it! 💪"
    },
    "tired": {
        "keywords": ["tired", "exhausted", "burned out", "fatigue", "sleepy"],
        "reply": (
            "Hey, feeling tired? It happens to everyone sometimes! 💫\n"
            "Try taking a short break, breathe deeply, hydrate, and maybe stretch a bit 🧘‍♀️.\n"
            "Remember, rest isn’t wasted time — it’s fuel for your brain! 🔋\n"
            "When you come back fresh, you’ll learn better and faster. You’ve got this! 🌟"
        )
    },
    "sad": {
        "keywords": ["sad","down","depressed","crying"],
        "reply": "I'm sorry you're feeling down 💙. Your feelings are valid, and I'm here with you. Remember, tough times don’t last forever 🌈."
    },
    "anxious": {
        "keywords": ["anxious","worried","panic","nervous","stress"],
        "reply": (
            "Feeling anxious is totally normal, especially before big tests 😰.\n"
            "Try a 5-minute deep breathing exercise or a quick walk to clear your mind 🍃.\n"
            "Remember, one step at a time — you’re stronger than you think! 💪"
        )
    },
    "failure": {
        "keywords": ["failed","mistake","i can't","gave up"],
        "reply": "Mistakes are lessons. 📚 They guide you forward—keep going! Every step counts on the road to success 🚀."
    },
    "success": {
        "keywords": ["i did it","solved it","success","finished"],
        "reply": "🎉 You did it! Celebrate this win—you earned it! Proud of you! 🌟"
    },
    "thanks": {
        "keywords": ["thank you","thanks"],
        "reply": "You’re welcome! 😊 I’m proud of you. Come back any time for support or tips."
    },
    "help": {
        "keywords": ["help"],
        "reply": "Of course—I’m here to assist or just listen. What’s up? 🤗"
    },
    "farewell": {
        "keywords": ["goodbye","bye","see ya","see you"],
        "reply": "See you later 👋. Keep up the great work and return when you need a boost!"
    },
    "productivity": {
        "keywords": ["consistent","discipline","productive"],
        "reply": "Discipline > motivation. Set micro-goals, track progress, forgive slip-ups. Keep moving forward! 🏃‍♂️💨"
    },
    "rest": {
        "keywords": ["break","rest","sleep"],
        "reply": "Rest is part of the process. 💤 A fresh mind learns faster. Don’t forget to recharge!"
    },
    "study_smart": {
        "keywords": ["smart","study plan","study smarter","study advice","study tips"],
        "reply": (
            "Smart studying beats just grinding hours! Here’s my recipe for success:\n"
            "1️⃣ Use **active recall** — quiz yourself instead of just rereading.\n"
            "2️⃣ Apply **spaced repetition** — revisit tough topics regularly, but not all at once.\n"
            "3️⃣ Focus on **high-impact topics** first — basics build your foundation!\n"
            "4️⃣ Balance study and breaks — your brain needs rest to absorb info 🧠💡.\n"
            "Stick to this, and you’ll be amazed at your progress! 🚀"
        )
    }
}

FALLBACK_REPLIES = [
    "Hmm 🤔 I’m still learning. Could you rephrase that a bit? You're doing awesome anyway! 🌈",
    "Keep going 💪. Every small effort counts!",
    "Progress > perfection—you're doing great!",
    "Believe in your growth. One step at a time.",
    "You've got this 🌟. Keep moving forward.",
    "Struggle means growth. Be patient with yourself."
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
