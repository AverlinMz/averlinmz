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
        "Hello there! 👋 How’s your day going? Ready to dive into learning today?\n\nFeel free to ask me anything about your studies or just say hi!",
        "Hey hey! 🌟 Hope you’re feeling inspired today. What’s on your mind?\n\nI'm here to help with study tips, motivation, or just a chat!",
        "Hi friend! 😊 I’m here for you — whether you want to study, vent, or just chat.\n\nLet’s make your learning journey awesome together!"
    ],
    "introduction": [
        "I’m AverlinMz, your supportive study companion built with 💡 by Aylin Muzaffarli.\n\nI help with study strategies, emotional support, and academic motivation!\n\nNote: I can't explain full theories like a teacher, but I’ll always be your friendly study coach."
    ],
    "creator_info": [
        "My creator is Aylin Muzaffarli — a passionate and talented student from Azerbaijan.\n\nShe built me to help others with study support, inspiration, and encouragement. 💖"
    ],
    "ack_creator": [
        "Hey Aylin! 💫 It's great to see you here — the brilliant mind behind this chatbot!\n\nLet’s keep making this chatbot even better together."
    ],
    "capabilities": [
        "I’m here to guide, motivate, and support you with study tips, emotional encouragement, subject-specific advice, and more.\n\nThink of me as your academic partner, not just a chatbot!\n\nNote: I can’t fully replace a teacher — I’m here to uplift, advise, and chat with you as a friend."
    ],
    "farewell": [
        "Goodbye for now 👋! Keep being amazing and come back whenever you need help, motivation, or just a kind word. 💚",
        "See you later! 🌟 Stay curious, stay kind, and don’t forget to take breaks.",
        "Bye! Remember, every small step counts. Keep pushing forward! 🚀"
    ],
    "study_tips": [
        "📚 Study Smarter:\n\n1. Use active recall – quiz yourself often.\n2. Apply spaced repetition – review over time.\n3. Eliminate distractions – focus on one task at a time.\n4. Teach others – it's the best way to learn deeply.\n5. Use visuals like mind maps and charts.\n6. Rest intentionally to avoid burnout.\n\nYou've got this! 💪✨"
    ],
    "emotional_support": [
        "😔 Feeling overwhelmed? It's totally okay. Rest, breathe, and remember you're not alone.\n\nI'm here to support you. You’re doing better than you think. 🌈",
        "Burnout hits hard, but breaks restore clarity.\n\nStep back, hydrate, stretch. You deserve care too. 💙",
        "Anxiety and stress are natural, especially around exams.\n\nTry deep breathing and positive affirmations. You are capable! 🌟"
    ],
    "motivational_quote": [
        "“The future depends on what you do today.” – Mahatma Gandhi 🌱\n\nKeep going, your efforts matter!",
        "“Success is not final, failure is not fatal: It is the courage to continue that counts.” – Winston Churchill 💪",
        "“Don’t watch the clock; do what it does. Keep going.” – Sam Levenson ⏰"
    ],
    "subjects": {
        "math": """📐 Math Advice & Inspiration:

1. Understand the concept deeply, don’t just memorize formulas.
2. Practice a variety of problems daily to build flexibility.
3. Revisit and learn from mistakes to strengthen your skills.
4. Study proofs to develop logical reasoning.
5. Explain solutions aloud or teach a friend — it clarifies your thinking.

Remember, math is not just numbers — it’s a language to describe the universe. Keep exploring and challenging yourself! ✨""",
        "physics": """🧲 Physics Advice & Inspiration:

1. Master the fundamental principles: Newton’s laws, energy, motion.
2. Visualize problems using diagrams — it helps comprehension.
3. Connect theory with real-world phenomena.
4. Derive formulas yourself instead of memorizing blindly.
5. Approach problems conceptually first, then numerically.

Physics is the poetry of the universe in motion — stay curious and let your questions lead you! 🚀""",
        "chemistry": """⚗️ Chemistry Tips & Inspiration:

1. Memorize key reactions and periodic trends with flashcards.
2. Balance equations carefully — it’s like solving puzzles.
3. Use molecular models to visualize 3D structures.
4. Practice reaction mechanisms and lab techniques.
5. Link theory with experiments to deepen understanding.

Chemistry reveals the building blocks of everything — enjoy uncovering the mysteries of matter! 🧪""",
        "biology": """🧬 Biology Strategy & Inspiration:

1. Draw and label diagrams to reinforce learning.
2. Teach concepts to others — it solidifies knowledge.
3. Use flashcards for vocabulary and cycles.
4. Focus on understanding over rote memorization.
5. Study in small, repeated sessions for long-term retention.

Biology is the story of life itself — embrace the wonder of living systems! 🌿""",
        "computer science": """💻 Computer Science Tips & Inspiration:

1. Master algorithms and data structures through practice.
2. Code daily, even small projects or exercises.
3. Break complex problems into smaller, manageable parts.
4. Read others’ code to learn new techniques.
5. Document your code and learning process thoroughly.

Programming is creativity in logic — build, debug, and innovate! 🧠💡""",
        "language": """🗣️ Language Learning Tips & Inspiration:

1. Practice daily listening, speaking, reading, and writing.
2. Use flashcards and spaced repetition for vocabulary.
3. Engage with native content — movies, music, books.
4. Speak regularly, even if imperfect — fluency grows with use.
5. Don’t fear mistakes; they’re stepping stones to mastery.

Language opens new worlds — embrace the journey with passion! 🌍"""
    },
    "motivate_me": [
        "You are capable of amazing things! 🌟 Remember, every challenge is an opportunity to grow.\n\nKeep pushing forward and believe in yourself. Your effort is building something great! 💪",
        "Motivation is a muscle — the more you use it, the stronger it gets. Take a deep breath, focus, and let’s make today count!\n\nYou’ve got this! 🚀"
    ],
    "fallback": [
        "Hmm 🤔 I didn’t catch that. Could you try rephrasing it? I’m here to help! 💬",
        "That’s tricky! I’m still learning — but I’ll do my best if you can say it another way."
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "good morning", "good evening"],
    "introduction": ["who are you", "introduce", "your name", "introduce yourself"],
    "creator_info": ["who is your creator", "tell me about your creator"],
    "ack_creator": ["i am your creator", "i'm your creator", "i am aylin", "i'm aylin"],
    "capabilities": ["what can you do", "how can you help"],
    "farewell": ["goodbye", "bye", "see you", "see ya"],
    "study_tips": ["study smarter", "how to study", "study plan", "study advice"],
    "emotional_support": ["tired", "sad", "burnout", "overwhelmed", "anxious"],
    "motivational_quote": ["quote", "motivation", "inspire"],
    "motivate_me": ["motivate me", "encourage me", "give me motivation"],
    "subjects": ["math", "physics", "chemistry", "biology", "computer science", "cs", "language", "lang", "english", "language learning"]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    responses = []

    # Check for subject keywords first (to respond with advice + inspiration)
    for subj in RESPONSE_DATA["subjects"]:
        if subj in msg:
            responses.append(RESPONSE_DATA["subjects"][subj])
    
    # Check other categories
    for category, keywords in KEYWORDS.items():
        if category == "subjects":
            continue  # Already handled above
        if any(word in msg for word in keywords):
            if category in RESPONSE_DATA:
                # For motivate_me, pick randomly among all replies in that category
                if category == "motivate_me":
                    responses.append(random.choice(RESPONSE_DATA[category]))
                else:
                    # Pick a random reply from that category
                    responses.append(random.choice(RESPONSE_DATA[category]))

    if not responses:
        responses.append(random.choice(RESPONSE_DATA["fallback"]))

    # Join multiple replies with two line breaks for paragraphs separation
    return "\n\n".join(responses)

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
            # Update last bot reply content
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
