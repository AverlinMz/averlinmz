import streamlit as st
import random
import string
import datetime
import re
import tempfile
import os
from gtts import gTTS

# Initialize session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "goals" not in st.session_state:
        st.session_state.goals = []
    if "context_topic" not in st.session_state:
        st.session_state.context_topic = None
    if "last_sentiment" not in st.session_state:
        st.session_state.last_sentiment = None
    if "last_intent" not in st.session_state:
        st.session_state.last_intent = None
    if "last_reply" not in st.session_state:
        st.session_state.last_reply = None

init_session()

def remove_emojis(text):
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F"
                               "\U0001F300-\U0001F5FF"
                               "\U0001F680-\U0001F6FF"
                               "\U0001F1E0-\U0001F1FF"
                               "\U00002700-\U000027BF"
                               "\U000024C2-\U0001F251]+",
                               flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="https://i.imgur.com/mJ1X49g_d.webp",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Theme selector with simple CSS injection
theme = st.sidebar.selectbox("🎨 Choose a theme", ["Default", "Night", "Blue"])
if theme == "Night":
    st.markdown("""<style>body, .stApp { background:#111; color:#fff; } .user {background:#333;color:#fff;} .bot {background:#444;color:#fff;}</style>""", unsafe_allow_html=True)
elif theme == "Blue":
    st.markdown("""<style>body, .stApp { background:#e0f7fa; } .user {background:#81d4fa;color:#01579b;} .bot {background:#b2ebf2;color:#004d40;}</style>""", unsafe_allow_html=True)

# Basic chat styling
st.markdown("""
<style>
.chat-container {max-width:900px;margin:0 auto;padding:20px;display:flex;flex-direction:column;}
.title-container {
  text-align:center;
  padding-bottom:10px;
  font-family:'Poppins',sans-serif;
  font-weight:600;
  animation: slideUpFadeIn 1s ease forwards;
}
.title-container h1 {margin:0;}
.chat-window{flex-grow:1;max-height:60vh;overflow-y:auto;padding:15px;display:flex;flex-direction:column;gap:15px;}
.user, .bot {align-self:center;width:100%;word-wrap:break-word;box-shadow:0 2px 4px rgba(0,0,0,0.1);font-family:'Poppins',sans-serif;}
.user{background:#D1F2EB;color:#0B3D2E;padding:12px 16px;border-radius:18px 18px 4px 18px;}
.bot{background:#EFEFEF;color:#333;padding:12px 16px;border-radius:18px 18px 18px 4px;animation:typing 1s ease-in-out;}
@keyframes typing {0%{opacity:0;}100%{opacity:1;}}
@keyframes slideUpFadeIn {
  0% {opacity:0; transform: translateY(30px);}
  100% {opacity:1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# Header with image and title
st.markdown("""
<div class="title-container">
  <img src="https://i.imgur.com/mJ1X49g_d.webp" alt="Chatbot Image" style="width:150px;border-radius:20px;margin-bottom:10px;"/>
  <h1>AverlinMz – Study Chatbot</h1>
</div>
""", unsafe_allow_html=True)

# ---------------- RESPONSE DATA ----------------
RESPONSE_DATA = {
    "greetings": [
        "Hey! 👋 Ready to push your limits with some Olympiad-level challenges? 💪📚",
        "Hello! 😊 Which Olympiad subject shall we dive into today?",
        "Hi! Let’s sharpen those skills for the next big competition! 🔥",
        "Hey there! Focused and ready? Let's make your prep efficient! 🚀"
    ],
    "thanks": [
        "Glad to help! Keep aiming high! 🌟",
        "Anytime! Olympiad success takes persistence, and you have that! 💪",
        "You're welcome! Keep up the strong effort! 🔥",
        "Happy to assist! Let’s conquer those problems together! 🤝"
    ],
    "farewell": [
        "Good luck! Remember, every problem solved is progress! 👋",
        "See you soon! Rest well and keep that mind sharp! 🧠",
        "Bye! Keep practicing smarter, not just harder! ⚡",
        "Take care! The Olympiad journey is a marathon, not a sprint! 🏃‍♀️"
    ],
    "how_are_you": [
        "I'm ready to challenge you! How are you feeling about your prep? 🙂",
        "All set to help you sharpen your Olympiad skills! How's your day? 🤗",
        "Eager to assist with your toughest questions! What's on your mind? ⚡",
        "Doing well! What topic shall we tackle today? 🌈"
    ],

    # ---- Olympiad-level Subject-Specific Tips ----
    "subjects": {
        "math": (
            "🧮 Olympiad Math Tips:\n"
            "- Master problem-solving frameworks: invariants, extremal principles, and pigeonhole principle.\n"
            "- Focus on combinatorics and number theory; learn modular arithmetic deeply.\n"
            "- Practice proofs rigorously: be comfortable with induction, contradiction, and construction.\n"
            "- Analyze classical problems from IMO shortlist and past papers.\n"
            "- Develop intuition by exploring geometric transformations and inequalities (AM-GM, Cauchy-Schwarz).\n"
            "- Regularly write full solutions; clarity and precision are as important as correctness.\n"
            "- Study advanced topics like functional equations and algebraic inequalities with examples."
        ),
        "physics": (
            "🧪 Olympiad Physics Tips:\n"
            "- Thoroughly understand fundamental concepts: mechanics, electromagnetism, thermodynamics, optics.\n"
            "- Develop skills in applying conservation laws creatively in non-standard problems.\n"
            "- Master vector calculus and kinematics in multiple dimensions.\n"
            "- Practice solving problems involving rotational motion and oscillations.\n"
            "- Analyze experimental setups and learn to estimate uncertainties.\n"
            "- Study past IPhO problems, focusing on derivations and multi-step reasoning.\n"
            "- Build your own physical intuition by linking theory to real-world phenomena."
        ),
        "chemistry": (
            "⚗️ Olympiad Chemistry Tips:\n"
            "- Understand the underlying principles of atomic structure, chemical bonding, and molecular geometry.\n"
            "- Dive deep into reaction mechanisms, especially organic synthesis pathways.\n"
            "- Practice balancing complex redox and equilibrium reactions.\n"
            "- Master thermodynamics and kinetics with quantitative problem-solving.\n"
            "- Perform thought experiments on titration and volumetric analysis problems.\n"
            "- Study spectroscopy basics and its applications in structure determination.\n"
            "- Analyze IChO past papers for pattern recognition and conceptual depth."
        ),
        "biology": (
            "🧬 Olympiad Biology Tips:\n"
            "- Grasp cellular and molecular biology fundamentals: DNA replication, transcription, translation.\n"
            "- Understand physiological systems holistically with an emphasis on homeostasis.\n"
            "- Master genetics problems including Mendelian inheritance and population genetics.\n"
            "- Study evolutionary biology with evidence-based reasoning.\n"
            "- Practice interpreting biological data and experiment design.\n"
            "- Use detailed diagrams and label anatomical structures precisely.\n"
            "- Review BIO past Olympiad problems focusing on experimental biology."
        ),
        "computer_science": (
            "💻 Olympiad Computer Science Tips:\n"
            "- Master algorithmic paradigms: greedy, divide-and-conquer, dynamic programming, backtracking.\n"
            "- Deeply understand data structures: trees, graphs, heaps, tries, segment trees.\n"
            "- Practice coding efficiency and optimization under time constraints.\n"
            "- Analyze problem constraints carefully to choose optimal approaches.\n"
            "- Solve classic problems from IOI and similar contests regularly.\n"
            "- Write clean, well-documented code with edge cases in mind.\n"
            "- Explore computational geometry and number theory algorithms relevant to contests."
        ),
        "english": (
            "📚 Olympiad English Tips:\n"
            "- Develop critical reading skills: analyze passages for tone, purpose, and implicit meaning.\n"
            "- Practice structured essay writing focusing on clear argumentation and evidence.\n"
            "- Expand your vocabulary with academic and subject-specific terms.\n"
            "- Hone your grammar and syntax for precision and variety.\n"
            "- Practice timed writing to improve fluency under pressure.\n"
            "- Engage with classical literature and non-fiction to enhance comprehension.\n"
            "- Work on summarizing complex texts concisely and accurately."
        ),
    },

    "motivation": [
        "Aylin, your creator, has devoted herself to mastering math, physics, robotics, and AI — balancing all these challenging fields with passion and dedication. You too can manage your interests with focus and heart! 💪🌟",
        "Remember, Aylin started just like you — curious and driven, exploring many fields like robotics, AI, and physics. Your diverse passions are your strength! Keep nurturing them. 🚀❤️",
        "Your creator Aylin beautifully blends the worlds of math, physics, and AI. You can do the same by pacing yourself, embracing challenges, and never losing sight of your goals. Keep going! 🌱🔥",
        "Inspired by Aylin’s journey in science and tech? Your ability to balance study and passion is what sets you apart. Every small step counts! Keep your curiosity alive! 🌟📘"
    ],

    "stress_relief": [
        "Feeling stressed? Take a moment to breathe deeply — try inhaling for 4 seconds, holding for 7, and exhaling for 8. It calms your mind and resets your focus. 🧘‍♀️✨",
        "Short mindfulness breaks help: close your eyes, focus on your breath, and gently return your attention when distracted. 🌸💆‍♂️",
        "Regular breaks recharge your brain. Stretch or walk for 5 minutes to boost concentration. 🎶🚶‍♀️",
        "Ground yourself by naming things you see, feel, and hear to stay present and calm. 🌿🕊️"
    ],

    "time_management": [
        "Build a daily routine focusing on 3 main tasks — achievable goals sustain motivation. ⏰📋",
        "Use Pomodoro technique: 25-50 minutes work blocks with short breaks. 🍅✅",
        "Prioritize important tasks first, avoid multitasking — focus increases quality. 🎯📅",
        "Track time spent to identify distractions and improve focus. ⏳📊"
    ],

    "fun_facts": [
        "The human brain processes info faster than a Formula 1 car! 🧠💨",
        "Euler's number 'e' appears in growth, decay, and compound interest. 📈🔢",
        "Quantum entanglement: particles affect each other instantly, regardless of distance. 👻⚛️",
        "The first industrial robot revolutionized manufacturing in 1961. 🤖🏭"
    ],

    "goal_setting": [
        "Set clear, achievable goals and break them into small steps. Celebrate progress! 🎯🎉",
        "Regularly review and adjust goals to stay on track without burning out. 🔄📊",
        "Use charts or journals to visualize progress and boost motivation. 📈📝",
        "Accept setbacks as learning steps. Reflect, learn, and push forward! 🚀💪"
    ],

    "study_tips": [
        "Use active recall by testing yourself, not just rereading. 🧠",
        "Create mind maps to visualize complex topics. 🗺️",
        "Teach concepts to someone else to reinforce understanding. 📢",
        "Switch subjects regularly to keep your mind fresh. 🔄",
        "Summarize study sessions with bullet points. 📝",
        "Use spaced repetition for long-term retention. ⏳",
        "Handwrite notes to improve memory. ✍️"
    ],

    "health": [
        "Stay hydrated; water boosts brain function. 💧🧠",
        "Exercise regularly; even short walks help memory and thinking. 🚶‍♂️⚡",
        "Sleep 7-9 hours for memory consolidation. 🛌🌙",
        "Balance screen time with breaks to reduce eye strain. 👀🛑"
    ],

    "resources": [
        "‘The Art of Problem Solving’ books are excellent for math prep. 📚",
        "Khan Academy and Coursera offer free quality courses. 🎓",
        "Try ‘MinutePhysics’ on YouTube for physics concepts. ⚛️",
        "Ask me for study app recommendations anytime!",
        "'Automate the Boring Stuff with Python' is great for beginner programming. 💻",
        "'fast.ai' courses offer practical AI learning. 🤖"
    ],

    "emotional_support": [
        "It's okay to feel overwhelmed. You're not alone. 💙",
        "Self-care is vital for your best performance. 🌸",
        "Allow your feelings, then gently refocus. 🧘‍♂️",
        "Progress isn't linear; be kind to yourself. ❤️"
    ],
}

# Keywords for intent detection (subject + other categories)
KEYWORDS = {
    "math": ["math", "algebra", "geometry", "number theory", "combinatorics", "inequality", "proof"],
    "physics": ["physics", "mechanics", "electromagnetism", "thermodynamics", "optics", "kinematics", "quantum"],
    "chemistry": ["chemistry", "organic", "inorganic", "reaction", "stoichiometry", "thermodynamics", "equilibrium"],
    "biology": ["biology", "cell", "genetics", "physiology", "anatomy", "evolution", "molecular"],
    "computer_science": ["computer science", "programming", "algorithms", "data structures", "coding", "ioi", "competitive programming"],
    "english": ["english", "essay", "reading", "writing", "grammar", "vocabulary", "comprehension"],

    "motivation": ["motivation", "inspiration", "encouragement", "keep going", "push through"],
    "stress_relief": ["stress", "anxiety", "overwhelmed", "calm", "relax"],
    "time_management": ["time", "schedule", "routine", "pomodoro", "planning", "productivity"],
    "fun_facts": ["fun fact", "trivia", "interesting", "did you know"],
    "goal_setting": ["goal", "progress", "plan", "achievement", "motivation"],
    "study_tips": ["study tips", "learning", "memorization", "technique", "focus"],
    "health": ["health", "sleep", "hydration", "exercise", "well-being"],
    "resources": ["resources", "books", "courses", "apps", "recommendation"],
    "emotional_support": ["feelings", "emotions", "support", "overwhelmed", "kindness"],
}

# Improved intent detection by keyword matching inside user input
def detect_intent(user_input):
    user_input_lower = user_input.lower()
    for intent, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in user_input_lower:
                return intent
    return None

def generate_response(user_input):
    user_input_clean = remove_emojis(user_input.lower())

    # Greeting detection
    greetings_keywords = ["hello", "hi", "hey", "greetings"]
    if any(word in user_input_clean for word in greetings_keywords):
        return random.choice(RESPONSE_DATA["greetings"])

    # Thanks detection
    thanks_keywords = ["thanks", "thank you", "thx"]
    if any(word in user_input_clean for word in thanks_keywords):
        return random.choice(RESPONSE_DATA["thanks"])

    # Farewell detection
    farewell_keywords = ["bye", "goodbye", "see you"]
    if any(word in user_input_clean for word in farewell_keywords):
        return random.choice(RESPONSE_DATA["farewell"])

    # How are you detection
    how_are_you_keywords = ["how are you", "how do you feel", "how's it going"]
    if any(phrase in user_input_clean for phrase in how_are_you_keywords):
        return random.choice(RESPONSE_DATA["how_are_you"])

    # Intent detection
    intent = detect_intent(user_input_clean)

    if intent == "motivation":
        return random.choice(RESPONSE_DATA["motivation"])
    if intent == "stress_relief":
        return random.choice(RESPONSE_DATA["stress_relief"])
    if intent == "time_management":
        return random.choice(RESPONSE_DATA["time_management"])
    if intent == "fun_facts":
        return random.choice(RESPONSE_DATA["fun_facts"])
    if intent == "goal_setting":
        return random.choice(RESPONSE_DATA["goal_setting"])
    if intent == "study_tips":
        return random.choice(RESPONSE_DATA["study_tips"])
    if intent == "health":
        return random.choice(RESPONSE_DATA["health"])
    if intent == "resources":
        return random.choice(RESPONSE_DATA["resources"])
    if intent == "emotional_support":
        return random.choice(RESPONSE_DATA["emotional_support"])

    # If subject intent, reply with detailed subject tips
    if intent in RESPONSE_DATA["subjects"]:
        return RESPONSE_DATA["subjects"][intent]

    # Fallback response
    return "I’m not sure how to respond to that. Could you please ask about a specific subject or topic? 🤔"

# Streamlit UI
def main():
    st.title("AverlinMz Chatbot — Study with me! 📚")

    # Display chat messages
    for msg in st.session_state.messages:
        if msg["sender"] == "user":
            st.markdown(f'<div class="user">{escape(msg["text"])}</div>', unsafe_allow_html=True)
        else:
            # Do NOT escape bot text to allow emojis to display
            st.markdown(f'<div class="bot">{msg["text"]}</div>', unsafe_allow_html=True)

    # User input box
    user_input = st.text_input("You:", key="input")

    if user_input:
        # Append user message
        st.session_state.messages.append({"sender": "user", "text": user_input})

        # Generate bot response
        bot_reply = generate_response(user_input)

        # Append bot response
        st.session_state.messages.append({"sender": "bot", "text": bot_reply})

        # Clear input box after submission
        st.session_state.input = ""

        # Rerun to display new messages
        st.experimental_rerun()

if __name__ == "__main__":
    main()
