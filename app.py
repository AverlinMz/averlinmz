import streamlit as st
import random
import string
from html import escape

# Initialize session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_user_input" not in st.session_state:
        st.session_state.last_user_input = ""
    if "answered_intro" not in st.session_state:
        st.session_state.answered_intro = False
init_session()

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
@keyframes typing {
    0% { opacity: 0; }
    100% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

# RESPONSE DATA
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
        "Sorry to hear that. I’m always here if you want to talk or need a study boost. 💙",
        "Tough days happen — but you’ve got this. One step at a time. 🐾"
    ],
    "exam_prep": [
        "Start early, make a plan, and review consistently. 📚 You’re capable of great things!",
        "Break topics into chunks and take breaks in between. You’ll learn smarter! 💡",
        "Practice past papers under timed conditions — it really helps! 🕰️",
        "Don’t cram last minute. Get good sleep and eat well before the exam! 🛌🍎",
        "I’m still learning, but these are great tips that work for many students!"
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
        # If user asked before, no "Hello"
        "I'm AverlinMz, your study chatbot 🌱. My creator is Aylin Muzaffarli (b.2011, Azerbaijan). She loves music, programming, robotics, AI, physics, and more. Reach her at averlinmz.github.io!"
    ],
    "creator_info": [
        "I was created by Aylin Muzaffarli — a passionate student from Azerbaijan who codes, studies physics and AI, and inspires others! 💡",
        "My developer is Aylin Muzaffarli, born in 2011. She built me to support learners like you!"
    ],
    "contact_creator": [
        "You can reach my creator via GitHub: https://github.com/AverlinMz or her site: https://averlinmz.github.io ✨",
        "Visit https://averlinmz.github.io or https://github.com/AverlinMz to get in touch! 💬"
    ],
    "ack_creator": [
        "Yes, Aylin is super talented! 😄",
        "Absolutely! All credit goes to Aylin Muzaffarli! 🌟"
    ],
    "motivation": [
        "Keep pushing forward, every step counts! 🚀",
        "Remember why you started and keep your goals in sight! 🌟",
        "I’m here to support you whenever you feel stuck. You got this! 💪"
    ],
    "study_tips": [
        "Try to study in focused 25-minute sessions with 5-minute breaks (Pomodoro technique). ⏲️",
        "Make summaries of what you learn — writing helps memory. ✍️",
        "Use flashcards to memorize facts and formulas. 🃏"
    ],
    "time_management": [
        "Make a daily schedule and prioritize your tasks. 📅",
        "Avoid multitasking — focus on one thing at a time. 🎯",
        "Use timers to keep track of study and rest periods."
    ],
    "subjects": {
        "math": "Math is the language of patterns and logic. Practice problem-solving every day, focusing on understanding concepts deeply rather than memorizing formulas. ➕➗",
        "physics": "Physics explains how the universe works — from motion to energy. Start with classical mechanics and build intuition by doing experiments or simulations. 🚀",
        "chemistry": "Chemistry studies matter and its interactions. Learn about atoms, molecules, chemical reactions, and lab safety to build a strong foundation. 🔬",
        "biology": "Biology explores life in all forms — from cells to ecosystems. Focus on understanding systems and processes. 🧬",
        "english": "Improving English requires regular reading, writing, and speaking practice. Engage with stories, articles, and conversations to build fluency. 📖",
        "robotics": "Robotics combines hardware and software. Start with basics like sensors and microcontrollers, then try building simple robots to practice. 🤖",
        "ai": "Artificial Intelligence combines programming, math, and logic. Start with Python basics, then explore machine learning concepts. 🧠"
    },
    "fallback": [
        "Hmm, I’m not sure how to answer that — try rephrasing or asking something about study or motivation! 🤔 I'm still learning.",
        "I didn’t quite get that, but I’m here to help! Maybe ask about a subject or how you feel. 😊 I'm still learning."
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "greetings", "salam"],
    "how_are_you": ["how are you", "how's it going", "how do you feel"],
    "user_feeling_good": ["i'm fine", "i'm good", "great", "happy", "excellent"],
    "user_feeling_bad": ["i'm sad", "not good", "tired", "depressed", "bad"],
    "love": ["i love you", "you are cute", "like you"],
    "exam_prep": [
        "exam tips", "exam tip", "how to prepare", "study for test", "exam help",
        "give me advice", "advice for exam", "exam advice", "prepare for exam",
        "how to study", "study tips", "give me a tip", "give me tip",
        "tip for exam prep", "tips for exam prep", "advice on exam prep", "help with exam"
    ],
    "passed_exam": ["i passed", "got good mark", "i won"],
    "capabilities": ["what can you do", "your functions", "features"],
    "introduction": ["introduce", "who are you", "your name", "about you", "creator", "who made you"],
    "creator_info": ["who is aylin", "who made you", "your developer", "tell me about aylin", "about aylin"],
    "contact_creator": ["how to contact", "reach aylin", "contact you", "talk to aylin"],
    "ack_creator": ["aylin is cool", "thank aylin", "credit to aylin"],
    "motivation": ["motivate me", "encourage me", "need motivation", "inspire me"],
    "study_tips": ["study tips", "how to study", "study advice"],
    "time_management": ["time management", "manage time", "time planning"],
    "subjects": ["math", "physics", "chemistry", "biology", "english", "robotics", "ai"]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    cleaned = {cat: [clean_text(kw) for kw in kws] for cat, kws in KEYWORDS.items()}

    # Special handling for introduction to avoid repeating "Hello" every time
    if any(kw in msg for kw in cleaned.get('introduction', [])):
        if not st.session_state.answered_intro:
            st.session_state.answered_intro = True
            return RESPONSE_DATA['introduction'][0]
        else:
            return RESPONSE_DATA['introduction'][0].replace("Hello! ", "")

    # If user asks about Aylin explicitly, reply creator_info
    if any(kw in msg for kw in cleaned.get('creator_info', [])):
        return random.choice(RESPONSE_DATA['creator_info'])

    # Keywords matching
    for cat in [
        'user_feeling_good','user_feeling_bad','love','how_are_you','greetings',
        'exam_prep','capabilities','passed_exam','contact_creator','ack_creator',
        'motivation','study_tips','time_management'
    ]:
        if any(kw in msg for kw in cleaned.get(cat, [])):
            return random.choice(RESPONSE_DATA[cat])

    # Subjects
    for subj in cleaned.get('subjects', []):
        if subj in msg and subj in RESPONSE_DATA['subjects']:
            return RESPONSE_DATA['subjects'][subj]

    # Aylin keywords (also sometimes users say just 'Aylin' alone)
    if "aylin" in msg:
        return random.choice(RESPONSE_DATA['creator_info'])

    # No matches — fallback answer with encouragement to try again
    return random.choice(RESPONSE_DATA['fallback'])

# Chat form & display
with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        reply = get_bot_reply(user_input)
        st.session_state.messages.append({'role': 'bot', 'content': reply})
        st.session_state.last_user_input = user_input

# Render chat messages
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
msgs = st.session_state.messages
for i in range(len(msgs) - 2, -1, -2):
    user_msg = msgs[i]['content']
    bot_msg = msgs[i+1]['content'] if i+1 < len(msgs) else ''
    st.markdown(f'<div class="user">{escape(user_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot">{escape(bot_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# Sidebar tips
with st.sidebar:
    st.markdown("### 💡 Tips")
    st.info(
        "You can ask things like:\n"
        "- 'Give me study tips'\n"
        "- 'Tell me about physics'\n"
        "- 'How do I manage time?'\n"
        "- 'Motivate me please!'\n"
        "- 'Who created you?'\n"
    )
