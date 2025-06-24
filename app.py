import streamlit as st
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
        "I’m AverlinMz, your supportive study companion built with 💡 by Aylin Muzaffarli.\n\n"
        "I help with study strategies, emotional support, and academic motivation!\n\n"
        "Note: I can't explain full theories like a teacher, but I’ll always be your friendly study coach."
    ],
    "creator_info": [
        "My creator is Aylin Muzaffarli – a passionate and talented student from Azerbaijan.\n\n"
        "She built me to help others with study support, inspiration, and encouragement. 💖"
    ],
    "ack_creator": [
        "Hey Aylin! 💫 It's great to see you here — the brilliant mind behind this chatbot!\n\n"
        "Let’s keep making this chatbot even better together."
    ],
    "capabilities": [
        "I’m here to guide, motivate, and support you with study tips, emotional encouragement, subject-specific advice, and more.\n\n"
        "Think of me as your academic partner, not just a chatbot!\n\n"
        "Note: I can’t fully replace a teacher — I’m here to uplift, advise, and chat with you as a friend."
    ],
    "study_tips": [
        "📚 Study Smarter:\n"
        "1. Use active recall – quiz yourself often.\n"
        "2. Apply spaced repetition – review material over time.\n"
        "3. Eliminate distractions – focus on one task at a time.\n"
        "4. Teach others – explaining concepts helps retention.\n"
        "5. Use visuals – mind maps and charts improve memory.\n"
        "6. Rest intentionally – breaks prevent burnout.\n\n"
        "You've got this! 💪✨"
    ],
    "emotional_support": [
        "😔 Feeling overwhelmed? It's totally okay.\n\n"
        "Rest, breathe deeply, and remember you're not alone.\n\n"
        "I'm here to support you. You’re doing better than you think. 🌈",
        "Burnout hits hard, but breaks restore clarity.\n\n"
        "Step back, hydrate, stretch.\n\n"
        "You deserve care too. 💙"
    ],
    "motivational_quote": [
        "“The future depends on what you do today.” – Mahatma Gandhi 🌱\n\nKeep going, your efforts matter!"
    ],
    "subjects": {
        "math": (
            "📐 Math Advice & Inspiration:\n\n"
            "1. Understand the concepts deeply, not just formulas.\n"
            "2. Practice a wide variety of problems daily.\n"
            "3. Revisit and rework problems you got wrong.\n"
            "4. Study proofs to sharpen your logical thinking.\n"
            "5. Explain your solutions aloud or to a friend.\n\n"
            "Math is like a puzzle — every problem you solve builds your brilliance! Keep going! ✨"
        ),
        "physics": (
            "🧲 Physics Advice & Inspiration:\n\n"
            "1. Master fundamental laws like Newton’s laws, energy, and motion.\n"
            "2. Draw diagrams to visualize problems.\n"
            "3. Connect theory with real-world examples.\n"
            "4. Derive formulas yourself rather than just memorizing.\n"
            "5. Solve conceptually before crunching numbers.\n\n"
            "Physics helps you see the world’s secrets — stay curious and explore! 🚀"
        ),
        "chemistry": (
            "⚗️ Chemistry Tips & Inspiration:\n\n"
            "1. Memorize key reactions and periodic table trends.\n"
            "2. Balance chemical equations carefully.\n"
            "3. Use molecular models to understand structure.\n"
            "4. Practice reaction mechanisms and lab techniques.\n"
            "5. Relate theoretical concepts to experiments.\n\n"
            "Chemistry unveils the molecular dance of life — enjoy the discovery! 🧪"
        ),
        "biology": (
            "🧬 Biology Strategy & Inspiration:\n\n"
            "1. Draw and label biological diagrams.\n"
            "2. Teach others to reinforce what you learn.\n"
            "3. Use flashcards for vocabulary and cycles.\n"
            "4. Aim for understanding, not just memorization.\n"
            "5. Study in short, frequent sessions.\n\n"
            "Biology reveals life’s amazing complexity — keep exploring! 🌿"
        ),
        "computer science": (
            "💻 Computer Science Advice & Inspiration:\n\n"
            "1. Master core algorithms and data structures.\n"
            "2. Code daily, even small exercises help.\n"
            "3. Break big problems into manageable parts.\n"
            "4. Read and learn from others’ code.\n"
            "5. Document your progress and code clearly.\n\n"
            "Programming is creative problem-solving — keep building and learning! 🧠💡"
        ),
        "language": (
            "🗣️ Language Learning Tips & Inspiration:\n\n"
            "1. Practice speaking regularly, even with yourself.\n"
            "2. Read diverse materials for vocabulary.\n"
            "3. Listen to native speakers via podcasts or videos.\n"
            "4. Use spaced repetition for vocabulary retention.\n"
            "5. Don’t fear mistakes; they’re part of learning.\n\n"
            "Languages open doors to new cultures — enjoy the journey! 🌍"
        )
    },
    "farewell": [
        "Goodbye for now 👋! Keep being amazing and come back whenever you need help, motivation, or just a kind word. 💚",
        "See you later! 🌟 Stay curious, stay kind, and don’t forget to take breaks."
    ],
    "fallback": [
        "Hmm 🤔 I didn’t catch that. Could you rephrase it a bit? I’m here to help! 💬",
        "That’s a tricky one! I'm your learning ally, not a human expert — but I’ll try my best if you reword it a little."
    ]
}

# Add more keyword variations especially for creator recognition and other categories
KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "good morning", "good evening"],
    "introduction": ["who are you", "introduce", "your name", "introduce yourself"],
    "creator_info": ["who is your creator", "tell me about your creator", "creator"],
    "ack_creator": [
        "i am your creator",
        "i'm your creator",
        "im your creator",
        "i am aylin",
        "i'm aylin",
        "im aylin",
        "im ur creator",
        "i'm ur creator",
        "i am ur creator"
    ],
    "capabilities": ["what can you do", "how can you help", "capabilities"],
    "study_tips": ["study smarter", "how to study", "study plan", "study advice"],
    "emotional_support": ["tired", "sad", "burnout", "overwhelmed", "anxious"],
    "motivational_quote": ["quote", "motivation", "inspire", "motivate me", "motivation please"],
    "farewell": ["goodbye", "bye", "see you", "see ya"],
    "subjects": ["math", "physics", "chemistry", "biology", "computer science", "cs", "language", "lang"]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    response = []

    # Check for subjects first to provide inspiring answers for subjects
    for subj in RESPONSE_DATA["subjects"]:
        if subj in msg:
            response.append(RESPONSE_DATA["subjects"][subj])

    # Then check other categories
    for category, words in KEYWORDS.items():
        if category == "subjects":
            continue  # already handled above
        if any(word in msg for word in words):
            if category == "motivational_quote":
                # For "motivate me" or similar
                response.append(random.choice(RESPONSE_DATA["motivational_quote"]))
            elif category in RESPONSE_DATA:
                response.append(random.choice(RESPONSE_DATA[category]))

    # If user says "im your creator" or similar, prefer acknowledgment
    if any(phrase in msg for phrase in KEYWORDS["ack_creator"]):
        response = [random.choice(RESPONSE_DATA["ack_creator"])]

    # If user asks about creator explicitly, prefer creator info
    if any(phrase in msg for phrase in KEYWORDS["creator_info"]):
        response = [random.choice(RESPONSE_DATA["creator_info"])]

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
