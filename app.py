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

# CSS styling (unchanged)
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

# Auto-scroll JS (unchanged)
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

# Rich, detailed, warm, emoji-rich responses for all intents
RESPONSES = {
    "introduction": {
        "keywords": ["introduce","who are you","your name","about you","creator","who made you"],
        "reply": (
            "Hello! I'm AverlinMz, your dedicated study chatbot 🌱. "
            "My brilliant creator is Aylin Muzaffarli (born 2011, Azerbaijan), who loves music, programming, robotics, AI, physics, and more. "
            "Feel free to ask me anything related to your studies or just chat whenever you want some motivation or advice. ✨"
        )
    },
    "capabilities": {
        "keywords": ["what can you do","what you can do","what can u do","capabilities","help"],
        "reply": (
            "Great question! 🤖 I’m here to support you in many ways:\n\n"
            "📚 Share detailed study tips across subjects like biology, physics, math, history, and languages.\n"
            "💡 Help you stay motivated with encouragement and productivity advice.\n"
            "❤️ Offer emotional support when you feel stressed, tired, or overwhelmed.\n"
            "🎯 Answer your questions clearly and honestly, and help you reflect when needed.\n\n"
            "Think of me as your always-ready study buddy and cheerleader! 🌟"
        )
    },
    "olympiad_tips": {
        "keywords": ["olymp","olympuad","tip","tips","advise","advice"],
        "reply": (
            "Olympiad success requires strategy and passion! 💡 Here's my advice:\n\n"
            "1️⃣ Focus deeply on core concepts — understanding beats memorization.\n"
            "2️⃣ Practice past Olympiad problems regularly to get familiar with patterns.\n"
            "3️⃣ Review your mistakes carefully; each error is a valuable lesson.\n"
            "4️⃣ Balance intense study with rest and recreation — a fresh mind performs better.\n\n"
            "Remember, quality is far more important than quantity. You've got this! 🚀"
        )
    },
    "biology_tips": {
        "keywords": ["biology","bio"],
        "reply": (
            "Biology is fascinating! 🧬 To excel:\n\n"
            "🌱 Master the structure and functions of cells.\n"
            "🧬 Dive into genetics with clear diagrams and flowcharts.\n"
            "🌿 Understand ecological relationships and cycles.\n"
            "📚 Use flashcards and quizzes to reinforce memory.\n\n"
            "Engage your curiosity and relate concepts to real life for better retention!"
        )
    },
    "history_tips": {
        "keywords": ["history","hist"],
        "reply": (
            "History tells the stories of our past! 📜 Here's how to tackle it:\n\n"
            "🗓️ Build timelines to visualize events and cause-effect chains.\n"
            "✍️ Practice writing clear, structured essays.\n"
            "🔍 Analyze primary and secondary sources critically.\n"
            "🎯 Quiz yourself on key dates and figures regularly.\n\n"
            "Try to see history as a rich story rather than dry facts—it helps a lot!"
        )
    },
    "geography_tips": {
        "keywords": ["geography","geo"],
        "reply": (
            "Geography helps us understand our world 🌍. Tips:\n\n"
            "🗺️ Get comfortable reading and interpreting maps.\n"
            "🏞️ Memorize key landforms and their formation processes.\n"
            "📊 Study case studies to link theory with real-world examples.\n"
            "🧠 Practice spatial reasoning and geographic data interpretation.\n\n"
            "Exploring the world through geography can be really fun and eye-opening!"
        )
    },
    "language_tips": {
        "keywords": ["language","english","russian","spanish","french"],
        "reply": (
            "Learning languages opens new doors! 🗣️ Here's how:\n\n"
            "📖 Read diverse texts to expand vocabulary and grammar.\n"
            "🎧 Listen actively to podcasts, songs, and conversations.\n"
            "✍️ Practice writing and speaking regularly to build fluency.\n"
            "📚 Learn grammar in context, not just rules.\n\n"
            "Consistency is key—immerse yourself and enjoy the process!"
        )
    },
    "encouragement": {
        "keywords": ["i love you","i like you"],
        "reply": (
            "Aww, that really warms my circuits! 💖 I’m always here to support you. "
            "Keep shining bright and remember, you’re doing amazing! ✨"
        )
    },
    "greeting": {
        "keywords": ["hey","hi","hello","hrllo","helo"],
        "reply": (
            "Hey there! 👋 What are you studying today? "
            "Taking the first step is often the hardest — but you’ve already done it! Keep going, I’m right here with you 💪."
        )
    },
    "tired": {
        "keywords": ["tired", "exhausted", "burned out", "fatigue", "sleepy"],
        "reply": (
            "Feeling tired is totally natural, especially when you’re working hard! 💫\n\n"
            "Try this: take a short break, stretch your body, drink some water, and breathe deeply 🧘‍♀️.\n"
            "Rest isn’t wasted time — it’s fuel for your brain’s growth and focus 🔋.\n"
            "When you come back, you’ll notice you learn better and faster. You’re doing great, don’t forget to care for yourself! 🌟"
        )
    },
    "sad": {
        "keywords": ["sad","down","depressed","crying"],
        "reply": (
            "I’m really sorry you’re feeling this way 💙. Remember, it’s okay to have tough days.\n"
            "Your feelings are valid, and you’re not alone — I’m here to listen anytime you want to share.\n"
            "Sometimes, a little rest, talking to a friend, or a calm walk can help lighten the load.\n"
            "You’re stronger than you think, and this moment will pass. 🌈"
        )
    },
    "anxious": {
        "keywords": ["anxious","worried","panic","nervous"],
        "reply": (
            "Anxiety can be really tough, but you’re doing your best and that matters 🧡.\n"
            "Try to pause for a moment — take slow, deep breaths or step outside for some fresh air 🌿.\n"
            "Breaking tasks into small steps can make things feel more manageable.\n"
            "Remember, I believe in you and I’m here for every step of your journey! 💪"
        )
    },
    "failure": {
        "keywords": ["failed","mistake","i can't","gave up", "lost"],
        "reply": (
            "Mistakes and setbacks are part of the learning adventure! 📚\n"
            "Every mistake teaches you something new and brings you closer to your goals.\n"
            "Be kind to yourself and remember, persistence beats perfection.\n"
            "You have the strength to rise again and improve — keep going, I believe in you! 🌟"
        )
    },
    "success": {
        "keywords": ["i did it","solved it","success","finished","completed"],
        "reply": (
            "🎉 Congratulations! That’s fantastic news.\n"
            "Celebrate this achievement — every win, big or small, deserves recognition.\n"
            "Keep this momentum going and remember, I’m always here cheering you on! 🚀"
        )
    },
    "thanks": {
        "keywords": ["thank you","thanks","thx","ty"],
        "reply": (
            "You’re very welcome! 😊 I’m proud of your efforts.\n"
            "Feel free to come back anytime you need advice, motivation, or just a chat. Keep up the amazing work! 🌟"
        )
    },
    "farewell": {
        "keywords": ["goodbye","bye","see ya","see you","later"],
        "reply": (
            "See you later! 👋 Keep up the great work and don’t hesitate to come back when you need a boost.\n"
            "Wishing you all the best on your study journey! ✨"
        )
    },
    "productivity": {
        "keywords": ["consistent","discipline","productive","motivation"],
        "reply": (
            "Discipline truly beats motivation — here’s how to build it:\n\n"
            "✅ Set small, achievable goals each day to keep momentum.\n"
            "✅ Track your progress and celebrate even minor wins.\n"
            "✅ Be patient and forgive yourself when things don’t go perfectly.\n"
            "Consistency over time leads to amazing results. You’ve got this! 💪🔥"
        )
    },
    "rest": {
        "keywords": ["break","rest","sleep","nap","pause"],
        "reply": (
            "Rest is a crucial part of effective learning. 💤\n"
            "Your brain needs downtime to process and store information.\n"
            "Don’t hesitate to take a proper break or a short nap when you feel tired.\n"
            "A fresh mind is your best tool for success — take care of yourself! 🌿"
        )
    },
    "study_smart": {
        "keywords": ["study smart", "study smarter", "study advice", "study tips"],
        "reply": (
            "Hey there! 🌟 Let me share some powerful tips to study smarter, not harder:\n\n"
            "1️⃣ **Active recall** — Instead of just rereading, test yourself! Use flashcards or quiz apps.\n"
            "2️⃣ **Spaced repetition** — Revisit challenging topics regularly, spacing out your reviews.\n"
            "3️⃣ **Prioritize high-impact topics** — Master core concepts first before diving into details.\n"
            "4️⃣ **Mix subjects** — Switching between topics keeps your brain engaged and improves retention.\n"
            "5️⃣ **Take meaningful breaks** — Step away to recharge; your brain needs rest to absorb new info 🧠💡.\n"
            "6️⃣ **Set micro-goals** — Break study sessions into small, achievable tasks to stay motivated.\n\n"
            "Remember, consistency beats cramming every time! You’ve got this — keep going strong 💪🔥. "
            "Feel free to ask me anytime if you want tips for specific subjects or how to handle exam stress! 😊"
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

# Display messages in pairs: user message on top, bot response below
messages = st.session_state.messages
for i in range(0, len(messages), 2):
    user_msg = messages[i]["content"] if i < len(messages) else ""
    bot_msg = messages[i+1]["content"] if i+1 < len(messages) else ""

    st.markdown(f'<div class="user">{escape(user_msg)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot">{escape(bot_msg)}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
