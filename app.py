# app.py

import streamlit as st
import random
import string
from html import escape

# ─────────────── RESPONSE DATA & KEYWORDS ───────────────

RESPONSE_DATA = {
    "greetings": [
        "Hello there! 👋 How’s your day going? Ready to dive into learning today?",
        "Hey hey! 🌟 Hope you’re feeling inspired today. What’s on your mind?",
        "Hi friend! 😊 I’m here for you — whether you want to study, vent, or just chat."
    ],
    "how_are_you": [
        "I'm doing well, thanks for asking! 💬 How are you feeling today?",
        "Feeling smart and helpful — as always! 😊 How can I assist you today?"
    ],
    "user_feeling_good": [
        "That’s amazing to hear! 🎉 Keep riding that good energy!",
        "Awesome! Let’s keep the momentum going! 💪"
    ],
    "user_feeling_bad": [
        "Sorry to hear that. I’m always here if you want to talk or need a study boost. 💙🌟",
        "It’s okay to feel this way. Just remember you’re not alone. I'm here with you. 🤗"
    ],
    "exam_prep": [
        "1️⃣ Start early and create a study plan.\n2️⃣ Break subjects into small topics.\n3️⃣ Use spaced repetition.\n4️⃣ Teach someone else to reinforce concepts.\n5️⃣ Rest well and stay hydrated. 📘💧",
        "Plan 📝 → Study 📚 → Practice 🧠 → Revise 🔁 → Sleep 😴. That's a golden strategy!"
    ],
    "passed_exam": [
        "🎉 CONGRATULATIONS! That’s amazing news! I knew you could do it.",
        "Woohoo! So proud of you! 🥳 What’s next on your journey?"
    ],
    "love": [
        "Aww 💖 That's sweet! I'm just code, but I support you 100%!",
        "Sending you virtual hugs and happy vibes 💕"
    ],
    "capabilities": [
        "I can give study tips, answer basic academic questions, track your mood, and motivate you. 🤓",
        "I'm designed to help students stay focused and positive. Ask me anything about learning! 💬"
    ],
    "introduction": [
        "I'm AverlinMz, your study chatbot 🌱. My creator is Aylin Muzaffarli (b.2011, Azerbaijan). She loves music, programming, robotics, AI, physics, and more. Reach her at https://github.com/AverlinMz!"
    ],
    "creator_info": [
        "I was created by Aylin Muzaffarli — a passionate student from Azerbaijan who codes, studies physics and AI, and inspires others! 💡",
        "My developer is Aylin Muzaffarli, born in 2011. She built me to support learners like you!"
    ],
    "contact_creator": [
        "You can contact my creator on GitHub: https://github.com/AverlinMz 📬",
        "Want to talk to Aylin? Try reaching out via GitHub – she's awesome! 🌟"
    ],
    "ack_creator": [
        "Yes, Aylin is super talented! 😄",
        "Absolutely! All credit goes to Aylin Muzaffarli! 🌟"
    ],
    "farewell": [
        "Goodbye! 👋 Come back soon for more study tips!",
        "See you later! Keep up the great work! 📘",
        "Bye for now! You’ve got this! 💪",
        "Take care! Don’t forget to smile and stay curious! 😊",
        "Catch you next time! Keep learning and dreaming big! ✨"
    ],
    "subjects": {
        "math": "🧮 Math Tips:\n1️⃣ Practice daily — it's the key to mastery.\n2️⃣ Understand concepts, don't just memorize.\n3️⃣ Use visuals like graphs and number lines.\n4️⃣ Solve real-world problems.\n5️⃣ Review your mistakes and learn from them.",
        "physics": "🧪 Physics Tips:\n1️⃣ Master the basics: units, vectors, motion.\n2️⃣ Solve numerical problems to strengthen concepts.\n3️⃣ Create diagrams to visualize problems.\n4️⃣ Memorize core formulas.\n5️⃣ Watch experiments online to connect theory with practice.",
        "chemistry": "🧫 Chemistry Tips:\n1️⃣ Know your periodic table well.\n2️⃣ Understand how and why reactions happen.\n3️⃣ Use flashcards for equations and compounds.\n4️⃣ Practice balancing equations.\n5️⃣ Watch reaction videos to make it fun!",
        "biology": "🧬 Biology Tips:\n1️⃣ Learn through diagrams (cells, organs, systems).\n2️⃣ Connect terms with real-life examples.\n3️⃣ Summarize topics using mind maps.\n4️⃣ Quiz yourself with apps.\n5️⃣ Talk about biology topics out loud.",
        "english": "📚 Language Tips:\n1️⃣ Read a bit every day (books, articles, stories).\n2️⃣ Speak or write in English regularly.\n3️⃣ Learn 5 new words daily and use them.\n4️⃣ Practice grammar through fun apps.\n5️⃣ Watch English shows with subtitles!",
        "robotics": "🤖 Robotics Tips:\n1️⃣ Start with block coding (like Scratch).\n2️⃣ Move on to Arduino and sensors.\n3️⃣ Join a club or competition.\n4️⃣ Watch tutorials and build projects.\n5️⃣ Learn how to debug and fix errors. Patience is key!",
        "ai": "🧠 AI Tips:\n1️⃣ Start with Python basics.\n2️⃣ Learn about data types and logic.\n3️⃣ Try building chatbots or mini classifiers.\n4️⃣ Study math behind AI: linear algebra, probability.\n5️⃣ Follow real AI projects online to stay inspired!"
    },
    "fallback": [
        "Hmm, I’m not sure how to answer that — try rephrasing or asking something about study or motivation! 🤔",
        "I didn’t quite get that, but I’m here to help! Maybe ask about a subject or how you feel. 😊"
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "greetings", "salam"],
    "how_are_you": ["how are you", "how's it going", "how do you feel"],
    "user_feeling_good": ["i'm fine", "i'm good", "great", "happy", "excellent"],
    "user_feeling_bad": ["i'm sad", "not good", "tired", "depressed", "bad", "feeling sad", "i'm feeling sad", "i feel bad"],
    "love": ["i love you", "you are cute", "like you"],
    "exam_prep": ["exam tips", "how to prepare", "study for test", "exam help", "give me advice for exam prep", "tips for exam"],
    "passed_exam": ["i passed", "got good mark", "i won"],
    "capabilities": ["what can you do", "your functions", "features"],
    "introduction": ["introduce", "who are you", "your name", "about you", "creator", "who made you", "introduce yourself"],
    "creator_info": ["who is aylin", "who made you", "your developer", "tell me about aylin"],
    "contact_creator": ["how to contact", "reach aylin", "contact you", "talk to aylin", "how can i contact to aylin"],
    "ack_creator": ["aylin is cool", "thank aylin", "credit to aylin"],
    "farewell": ["goodbye", "bye", "see you", "talk later", "see ya", "later"],
    "subjects": ["math", "physics", "chemistry", "biology", "english", "robotics", "ai"]
}

# ─────────────── SESSION & PAGE SETUP ───────────────

def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
init_session()

st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────── CSS & TITLE ───────────────

st.markdown("""
<style>
.stApp { padding: 0 !important; margin: 0 !important; }
header, footer { display: none !important; }
#MainMenu, .css-1v3fvcr { visibility: hidden !important; }

.chat-container { display: flex; flex-direction: column; max-width: 900px; margin: 0 auto; padding: 20px; }
.title-container { text-align: center; padding-bottom: 10px; background: white; font-family: 'Poppins', sans-serif; font-weight: 600; }
.title-container h1 { color: black; margin: 0; }

.chat-window { flex-grow: 1; overflow-y: auto; max-height: 60vh; padding: 15px; display: flex; flex-direction: column; gap: 15px; }
.user, .bot { align-self: center; width: 100%; word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-family: 'Poppins', sans-serif; }
.user { background-color: #D1F2EB; color: #0B3D2E; padding: 12px 16px; border-radius: 18px 18px 4px 18px; }
.bot  { background-color: #EFEFEF; color: #333; padding: 12px 16px; border-radius: 18px 18px 18px 4px; animation: typing 1s ease-in-out; }

.chat-window::-webkit-scrollbar { width: 8px; }
.chat-window::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb:hover { background: #a1a1a1; }

@keyframes typing { from { opacity: 0; } to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

# ─────────────── BOT LOGIC ───────────────

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    cleaned = {cat: [clean_text(kw) for kw in kws] for cat, kws in KEYWORDS.items()}

    # 1) Top-level categories except 'subjects'
    for cat in RESPONSE_DATA:
        if cat == "subjects":
            continue
        if any(kw in msg for kw in cleaned.get(cat, [])):
            return random.choice(RESPONSE_DATA[cat])

    # 2) 'subjects'
    for subj in cleaned.get("subjects", []):
        if subj in msg:
            return RESPONSE_DATA["subjects"][subj]

    # 3) fallback
    return random.choice(RESPONSE_DATA["fallback"])

# ─────────────── CHAT UI ───────────────

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Write your message…", key="input_field")
    if st.form_submit_button("Send") and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "bot", "content": get_bot_reply(user_input)})

st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
for i in range(len(st.session_state.messages) - 2, -1, -2):
    user_msg = st.session_state.messages[i]["content"]
    bot_msg = st.session_state.messages[i+1]["content"] if i+1 < len(st.session_state.messages) else ""
    st.markdown(f'<div class="user">{escape(user_msg)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot">{escape(bot_msg)}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 💡 Tips")
    st.info(
        "- Say ‘hi’ or ‘hello’\n"
        "- Ask for ‘exam tips’\n"
        "- Try ‘I passed my exam’\n"
        "- Or simply ‘goodbye’ to see the farewell!"
    )
