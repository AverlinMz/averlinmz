import streamlit as st
import random
import string
from html import escape
import datetime
import re
import tempfile
import os
from gtts import gTTS
from difflib import get_close_matches

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

# Theme selection and CSS
theme = st.sidebar.selectbox("🎨 Choose a theme", ["Default", "Night", "Blue"])
if theme == "Night":
    st.markdown("""<style>body, .stApp { background:#111; color:#fff; } .user {background:#333;color:#fff;} .bot {background:#444;color:#fff;}</style>""", unsafe_allow_html=True)
elif theme == "Blue":
    st.markdown("""<style>body, .stApp { background:#e0f7fa; } .user {background:#81d4fa;color:#01579b;} .bot {background:#b2ebf2;color:#004d40;}</style>""", unsafe_allow_html=True)

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

st.markdown("""
<div class="title-container">
  <img src="https://i.imgur.com/mJ1X49g_d.webp" alt="Chatbot Image" style="width:150px;border-radius:20px;margin-bottom:10px;"/>
  <h1>AverlinMz – Study Chatbot</h1>
</div>
""", unsafe_allow_html=True)

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

    "emotional_support": [
        "It's okay to feel overwhelmed. You're not alone. 💙",
        "Self-care is vital for your best performance. 🌸",
        "Allow your feelings, then gently refocus. 🧘‍♂️",
        "Progress isn't linear; be kind to yourself. ❤️"
    ],
}

FALLBACK_RESPONSES = [
    "I’m still learning and don’t know the answer right now. Maybe try rephrasing your question or searching online.",
    "Sorry, I’m still learning and can’t answer that at the moment. You might find better info by checking other resources.",
    "I don’t know the answer right now because I’m still learning. Try searching the web or asking other platforms.",
    "I’m still learning, so I don’t have an answer right now. You might want to explore other chats or do a quick internet search.",
    "That’s beyond my current knowledge as I’m still learning. Trying other places or searching online might help.",
    "I’m still learning and can’t help with that now. Maybe rephrase your question or use a search engine for more info."
]

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

def clean_keyword_list(keywords_dict):
    cleaned = {}
    for intent, phrases in keywords_dict.items():
        cleaned[intent] = [p.lower().translate(str.maketrans('', '', string.punctuation)).strip() for p in phrases]
    return cleaned

KEYWORDS_CLEANED = clean_keyword_list(KEYWORDS)

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def detect_intent(text):
    msg = clean_text(text)
    for intent, kws in KEYWORDS_CLEANED.items():
        if any(kw in msg for kw in kws):
            return intent
    words = msg.split()
    for word in words:
        for intent, kws in KEYWORDS_CLEANED.items():
            matches = get_close_matches(word, kws, n=1, cutoff=0.65)
            if matches:
                return intent
    for subj in RESPONSE_DATA["subjects"].keys():
        if subj in msg:
            return "subjects"
    return None

def update_goals(user_input):
    msg = clean_text(user_input)
    goal_keywords = ["goal", "aim", "plan", "objective", "target", "resolution", "ambition", "purpose", "intention"]
    if any(kw in msg for kw in goal_keywords):
        if user_input not in st.session_state.goals:
            st.session_state.goals.append(user_input)
            return "Got it! I've added that to your study goals."
        else:
            return "You already mentioned this goal."
    return None

def detect_sentiment(text):
    positive = ["good", "great", "awesome", "love", "happy", "fine", "well", "fantastic", "wonderful", "excellent", "perfect", "super", "amazing", "terrific"]
    negative = ["bad", "sad", "tired", "depressed", "down", "exhausted", "stressed", "anxious", "overwhelmed", "frustrated", "awful", "terrible", "horrible"]
    txt = clean_text(text)
    if any(word in txt for word in positive): return "positive"
    if any(word in txt for word in negative): return "negative"
    return "neutral"

def get_bot_reply(user_input):
    intent = detect_intent(user_input)
    goal_msg = update_goals(user_input)
    if goal_msg:
        return goal_msg

    sentiment = detect_sentiment(user_input)
    st.session_state.last_sentiment = sentiment

    if intent and intent in RESPONSE_DATA:
        if intent == "subjects":
            for subj in RESPONSE_DATA["subjects"].keys():
                if subj in user_input.lower():
                    st.session_state.context_topic = subj
                    break
            return RESPONSE_DATA["subjects"].get(st.session_state.context_topic, random.choice(FALLBACK_RESPONSES))
        else:
            return random.choice(RESPONSE_DATA[intent])

    # If context topic is set and user input relates to that subject
    if st.session_state.context_topic:
        subj = st.session_state.context_topic
        if subj in RESPONSE_DATA["subjects"]:
            # Provide detailed tips again if user asks something else about the subject
            if "more" in user_input.lower() or "again" in user_input.lower():
                return RESPONSE_DATA["subjects"][subj]
            # fallback to fallback response if user input is unrelated
            if any(word in user_input.lower() for word in ["thanks", "thank you", "bye", "goodbye", "exit"]):
                st.session_state.context_topic = None
                return random.choice(RESPONSE_DATA["farewell"])
            return RESPONSE_DATA["subjects"][subj]

    # Handle greetings and farewells explicitly
    if any(greet in user_input.lower() for greet in ["hello", "hi", "hey", "good morning", "good evening"]):
        return random.choice(RESPONSE_DATA["greetings"])
    if any(farewell in user_input.lower() for farewell in ["bye", "goodbye", "see you", "later", "exit"]):
        st.session_state.context_topic = None
        return random.choice(RESPONSE_DATA["farewell"])

    return random.choice(FALLBACK_RESPONSES)

def generate_audio_response(text):
    tts = gTTS(text=text, lang="en", slow=False)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)
    return tmp_file.name

def main():
    st.title("AverlinMz Study Chatbot 📚")
    st.markdown("Ask me about Olympiad subjects, study tips, motivation, stress relief, or anything to help your preparation!")

    user_input = st.text_input("You:", key="user_input")
    if user_input:
        user_input_clean = remove_emojis(user_input)
        st.session_state.messages.append({"user": user_input_clean})
        bot_reply = get_bot_reply(user_input_clean)
        st.session_state.messages.append({"bot": bot_reply})

    if st.session_state.messages:
        for i in range(len(st.session_state.messages)):
            msg = st.session_state.messages[i]
            if "user" in msg:
                st.markdown(f'<div class="user"><b>You:</b> {escape(msg["user"])}</div>', unsafe_allow_html=True)
            elif "bot" in msg:
                st.markdown(f'<div class="bot"><b>AverlinMz:</b> {escape(msg["bot"])}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
