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
.stApp {
    padding: 0 !important;
    margin: 0 !important;
}
header, footer { 
    display: none !important;
}
#MainMenu, .css-1v3fvcr { 
    visibility: hidden !important; 
}

/* Container styling */
.chat-container {
    display: flex;
    flex-direction: column;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    box-sizing: border-box;
}

/* Title */
.title-container {
    text-align: center;
    padding-bottom: 10px;
    background: white;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
}
.title-container h1 {
    color: black;  /* black title */
    margin: 0;
}

/* Input area (normal flow, not fixed) */
.input-area {
    display: flex;
    gap: 10px;
    padding: 10px 0 20px 0;
    background: white;
}
.input-area input {
    flex-grow: 1;
    padding: 14px 18px;
    font-size: 16px;
    border: 2px solid #ddd;
    border-radius: 30px;
    outline: none;
    transition: border-color 0.3s;
    font-family: 'Poppins', sans-serif;
}
.input-area input:focus {
    border-color: #3CA887;
}
.input-area button {
    padding: 14px 24px;
    font-size: 16px;
    border: none;
    border-radius: 30px;
    background-color: #3CA887;
    color: white;
    cursor: pointer;
    transition: background-color 0.3s;
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
}
.input-area button:hover {
    background-color: #2E7D6F;
}

/* Chat window */
.chat-window {
    flex-grow: 1;
    overflow-y: auto;
    max-height: 60vh;
    padding: 15px;
    display: flex;
    flex-direction: column-reverse;  /* newest at bottom */
    gap: 15px;
}

/* Message bubbles */
.user {
    align-self: flex-end;
    background-color: #D1F2EB;
    color: #0B3D2E;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    font-family: 'Poppins', sans-serif;
    max-width: 80%;
    word-wrap: break-word;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.bot {
    align-self: flex-start;
    background-color: #EFEFEF;
    color: #333333;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    font-family: 'Poppins', sans-serif;
    max-width: 80%;
    word-wrap: break-word;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Scrollbar styling */
.chat-window::-webkit-scrollbar {
    width: 8px;
}
.chat-window::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}
.chat-window::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 10px;
}
.chat-window::-webkit-scrollbar-thumb:hover {
    background: #a1a1a1;
}
</style>
""", unsafe_allow_html=True)

# Auto-scroll JS
st.markdown("""
<script>
function scrollToBottom() {
    const chatWindow = document.querySelector('.chat-window');
    if (chatWindow) {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}
window.onload = scrollToBottom;
const observer = new MutationObserver(scrollToBottom);
document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.querySelector('.chat-window');
    if (chatWindow) observer.observe(chatWindow, { childList: true, subtree: true });
});
</script>
""", unsafe_allow_html=True)

# Responses dict
RESPONSES = {
    "introduction": {
        "keywords": ["introduce", "who are you", "your name", "about you", "creator", "who made you"],
        "reply": "Hello! I'm AverlinMz, your study chatbot 🌱. My creator is Aylin Muzaffarli (b.2011, Azerbaijan). She loves music, programming, robotics, AI, physics, and more. Reach her at muzaffaraylin@gmail.com. Good luck!"
    },
    "capabilities": {
        "keywords": ["what can you do", "what you can do", "what can u do"],
        "reply": "I can cheer you on, share study tips (general or subject-specific!), and offer emotional support. Chat anytime you need a boost!"
    },
    "olympiad_tips": {
        "keywords": ["olymp", "olympuad", "tip", "tips", "advise", "advice"],
        "reply": "Olympiad tips 💡: Study smart—focus on core concepts, practice past problems, review mistakes, and balance work with rest. Quality > quantity!"
    },
    "biology_tips": {
        "keywords": ["biology", "bio"],
        "reply": "Biology 🧬: Master cell structure, genetics, and ecology. Draw diagrams, use flashcards, and practice Olympiad questions."
    },
    "history_tips": {
        "keywords": ["history", "hist"],
        "reply": "History 📜: Build timelines, practice structured essays, analyze sources, and quiz yourself on key dates."
    },
    "geography_tips": {
        "keywords": ["geography", "geo"],
        "reply": "Geography 🌍: Interpret maps, memorize landforms, study case-studies, and practice spatial reasoning."
    },
    "language_tips": {
        "keywords": ["language", "english", "russian", "spanish", "french"],
        "reply": "Languages 🗣️: Read varied texts, listen actively, learn grammar contextually, and speak/write regularly to build fluency."
    },
    "encouragement": {
        "keywords": ["i love you", "i like you"],
        "reply": "Aww, that warms my circuits! 💖 I'm here to support you anytime."
    },
    "greeting": {
        "keywords": ["hey", "hi", "hello", "hrllo", "helo"],
        "reply": "Hey there! What are you studying right now? Starting is half the battle—you've done it!"
    },
    "tired": {
        "keywords": ["tired", "exhausted", "fatigue"],
        "reply": "Feeling tired? 😴 Pause for a break—stretch, hydrate, breathe—and come back refreshed."
    },
    "sad": {
        "keywords": ["sad", "down", "depressed", "crying"],
        "reply": "I'm sorry you're feeling down 💙. Your feelings are valid, and I'm here with you."
    },
    "anxious": {
        "keywords": ["anxious", "worried", "panic", "nervous"],
        "reply": "Anxiety's tough. Pause, breathe deeply, or take a 5-minute walk. One step at a time 🧘."
    },
    "failure": {
        "keywords": ["failed", "mistake", "i can't", "gave up"],
        "reply": "Mistakes are lessons. 📚 They guide you forward—keep going!"
    },
    "success": {
        "keywords": ["i did it", "solved it", "success", "finished"],
        "reply": "🎉 You did it! Celebrate this win—you earned it!"
    },
    "thanks": {
        "keywords": ["thank you", "thanks"],
        "reply": "You’re welcome! 😊 I’m proud of you. Come back any time."
    },
    "help": {
        "keywords": ["help"],
        "reply": "Of course—I’m here to assist or just listen. What’s up?"
    },
    "farewell": {
        "keywords": ["goodbye", "bye", "see ya", "see you"],
        "reply": "See you later 👋. Keep up the great work and return when you need a boost."
    },
    "productivity": {
        "keywords": ["consistent", "discipline", "productive"],
        "reply": "Discipline > motivation. Set micro-goals, track progress, forgive slip-ups."
    },
    "rest": {
        "keywords": ["break", "rest", "sleep"],
        "reply": "Rest is part of the process. 💤 A fresh mind learns faster."
    },
    "study_smart": {
        "keywords": ["smart", "study plan", "study smarter"],
        "reply": "Study smart: active recall, spaced repetition, and high-impact topics."
    }
}

# Fallback replies
FALLBACK_REPLIES = [
    "Keep going 💪. Every small effort counts!",
    "Progress > perfection—you're doing great!",
    "Believe in your growth. One step at a time.",
    "You've got this 🌟. Keep moving forward.",
    "Struggle means growth. Be patient with yourself.",
]

# Helper for fuzzy keyword detection
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

# Generate reply based on user message
def generate_reply(user_msg):
    user_msg_lower = user_msg.lower()

    # Check responses
    for category, data in RESPONSES.items():
        if contains_keyword(user_msg_lower, data["keywords"]):
            return data["reply"]

    # Handle some subject-specific advice requiring multiple keywords
    if contains_keyword(user_msg_lower, ["biology"]) and contains_keyword(user_msg_lower, ["tip", "tips"]):
        return RESPONSES["biology_tips"]["reply"]

    if contains_keyword(user_msg_lower, ["history"]) and contains_keyword(user_msg_lower, ["tip", "tips"]):
        return RESPONSES["history_tips"]["reply"]

    if contains_keyword(user_msg_lower, ["geography"]) and contains_keyword(user_msg_lower, ["tip", "tips"]):
        return RESPONSES["geography_tips"]["reply"]

    if contains_keyword(user_msg_lower, ["language", "english", "russian"]) and contains_keyword(user_msg_lower, ["tip", "tips"]):
        return RESPONSES["language_tips"]["reply"]

    if contains_keyword(user_msg_lower, ["sad", "down", "depressed"]):
        return RESPONSES["sad"]["reply"]

    # Default fallback
    return random.choice(FALLBACK_REPLIES)


# --- Page content ---

# Title
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

# Input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder="Write your message...", key="input_field", label_visibility="collapsed")
    submit = st.form_submit_button("Send")
    if submit and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Add bot reply
        bot_response = generate_reply(user_input)
        st.session_state.messages.append({"role": "bot", "content": bot_response})

        # Use the standard rerun function instead of experimental
        st.rerun()  # FIXED: Replaced experimental_rerun with rerun

# Chat container and window
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.markdown('<div class="chat-window">', unsafe_allow_html=True)

# Show messages in reverse (newest bottom)
for msg in reversed(st.session_state.messages):
    content_safe = escape(msg["content"])
    if msg["role"] == "user":
        st.markdown(f'<div class="user">{content_safe}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{content_safe}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close chat-window
st.markdown('</div>', unsafe_allow_html=True)  # close chat-container
