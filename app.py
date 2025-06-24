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
        "I’m AverlinMz, your supportive study companion built with 💡 by Aylin Muzaffarli. I help with study strategies, emotional support, and academic motivation!\n\nNote: I can't explain full theories like a teacher, but I’ll always be your friendly study coach."
    ],
    "creator_info": [
        "My creator is Aylin Muzaffarli – a passionate and talented student from Azerbaijan. She built me to help others with study support, inspiration, and encouragement. 💖"
    ],
    "ack_creator": [
        "Hey Aylin! 💫 I recognize you — the brilliant creator behind all this. So glad you're here! Let’s keep making this chatbot even better together."
    ],
    "capabilities": [
        "I’m here to guide, motivate, and support you with study tips, emotional encouragement, subject-specific advice, and more. Think of me as your academic partner, not just a chatbot!\n\nNote: I can’t fully replace a teacher — I’m here to uplift, advise, and chat with you as a friend."
    ],
    "farewell": [
        "Goodbye for now 👋! Keep being amazing and come back whenever you need help, motivation, or just a kind word. 💚",
        "See you later! 🌟 Stay curious, stay kind, and don’t forget to take breaks."
    ],
    "motivational_quote": [
        "“The future depends on what you do today.” – Mahatma Gandhi 🌱 Keep going, your efforts matter!",
        "Keep pushing forward! Every small step you take is progress toward your dreams. 💪✨",
        "Motivation is the spark; discipline keeps the fire burning. You’ve got this! 🔥"
    ],
    "motivate_me": [
        "You’re stronger than any challenge ahead! Remember, every expert was once a beginner. Stay curious and keep growing. 🚀",
        "When you feel like quitting, think about why you started. Your future self will thank you for your perseverance. 🌟"
    ],
    "study_tips": [
        "📚 Study Smarter:\n\n"
        "1. Use active recall – quiz yourself often.\n"
        "2. Apply spaced repetition – review over time.\n"
        "3. Eliminate distractions – focus on one task at a time.\n"
        "4. Teach others – it's the best way to learn.\n"
        "5. Use visuals – mind maps, charts, and diagrams help.\n"
        "6. Rest intentionally – breaks prevent burnout.\n\n"
        "You've got this! 💪✨"
    ],
    "emotional_support": [
        "😔 Feeling overwhelmed? It's totally okay. Rest, breathe, and remember you're not alone. I'm here to support you. You’re doing better than you think. 🌈",
        "Burnout hits hard, but breaks restore clarity. Step back, hydrate, stretch. You deserve care too. 💙"
    ],
    "subjects": {
        "math": (
            "📐 **Math Advice & Inspiration:**\n\n"
            "1. Understand the concepts deeply, not just memorize formulas.\n"
            "2. Practice a variety of problems daily to sharpen your skills.\n"
            "3. Review mistakes carefully; they are your best teachers.\n"
            "4. Try explaining solutions aloud to yourself or others—it cements understanding.\n\n"
            "Math is the language of logic and creativity combined. Each problem solved is a victory for your mind! ✨"
        ),
        "physics": (
            "🧲 **Physics Tips & Inspiration:**\n\n"
            "1. Master fundamental laws like Newton’s laws and energy conservation.\n"
            "2. Draw diagrams to visualize problems clearly.\n"
            "3. Connect theoretical concepts to real-world phenomena.\n"
            "4. Derive formulas yourself rather than rote memorization.\n\n"
            "Physics unveils the mysteries of the universe. Embrace curiosity—every question is a doorway to discovery! 🚀"
        ),
        "chemistry": (
            "⚗️ **Chemistry Tips & Inspiration:**\n\n"
            "1. Memorize key reactions and understand periodic trends.\n"
            "2. Balance chemical equations like solving puzzles.\n"
            "3. Use models to visualize molecular structures.\n"
            "4. Practice reaction mechanisms thoroughly.\n\n"
            "Chemistry connects the tiny building blocks to life itself. Keep experimenting and exploring! 🧪"
        ),
        "biology": (
            "🧬 **Biology Study Strategy & Inspiration:**\n\n"
            "1. Draw and label diagrams for processes and structures.\n"
            "2. Teach concepts to friends or yourself to reinforce learning.\n"
            "3. Use flashcards for vocabulary and cycles.\n"
            "4. Focus on understanding rather than memorization.\n\n"
            "Biology reveals the wonders of life. Stay consistent and watch your knowledge grow! 🌿"
        ),
        "computer science": (
            "💻 **Computer Science Advice & Inspiration:**\n\n"
            "1. Learn algorithms and data structures deeply.\n"
            "2. Code regularly—even small projects help.\n"
            "3. Break problems into manageable parts.\n"
            "4. Read other people’s code and document your own.\n\n"
            "Programming is both art and logic. Embrace debugging as a path to mastery! 🧠💡"
        ),
        "language": (
            "🗣️ **Language Learning Tips & Inspiration:**\n\n"
            "1. Practice daily with reading, listening, speaking, and writing.\n"
            "2. Use flashcards and spaced repetition for vocabulary.\n"
            "3. Immerse yourself by watching shows or reading books.\n"
            "4. Don’t fear mistakes; they are part of growth.\n\n"
            "Languages open doors to new cultures and ideas. Keep speaking and listening—you’re building bridges! 🌍"
        )
    },
    "fallback": [
        "Hmm 🤔 I didn’t catch that. Could you rephrase it a bit? I’m here to help! 💬",
        "That’s a tricky one! I'm your learning ally, not a human expert — but I’ll try my best if you reword it a little."
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "good morning", "good evening"],
    "introduction": ["who are you", "introduce", "your name", "introduce yourself"],
    "creator_info": ["tell me about your creator"],
    "ack_creator": ["i'm your creator", "i am aylin"],
    "capabilities": ["what can you do", "how can you help"],
    "farewell": ["goodbye", "bye", "see you", "see ya"],
    "motivational_quote": ["quote", "motivation", "inspire", "motivate me"],
    "motivate_me": ["motivate me", "encourage me", "boost me"],
    "study_tips": ["study smarter", "how to study", "study plan", "study advice"],
    "emotional_support": ["tired", "sad", "burnout", "overwhelmed", "anxious"],
    "subjects": ["math", "physics", "chemistry", "biology", "computer science", "cs", "language", "lang"]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    response = []

    # Check keywords by category
    for category, words in KEYWORDS.items():
        if category == "subjects":
            # Look for any subject keyword and reply with its full subject text
            for subj in RESPONSE_DATA["subjects"]:
                if subj in msg:
                    response.append(RESPONSE_DATA["subjects"][subj])
                    break  # Only one subject reply per input
        else:
            if any(word in msg for word in words):
                # Special handling for motivational
                if category == "motivational_quote" or category == "motivate_me":
                    # If both categories found, prefer motivate_me first
                    if category == "motivate_me":
                        response.append(random.choice(RESPONSE_DATA["motivate_me"]))
                        break
                    else:
                        if not response:  # Only add motivational_quote if motivate_me not already chosen
                            response.append(random.choice(RESPONSE_DATA["motivational_quote"]))
                else:
                    if category in RESPONSE_DATA:
                        response.append(random.choice(RESPONSE_DATA[category]))
                if response:
                    break  # Stop after first matched category

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
