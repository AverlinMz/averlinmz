import streamlit as st
import random
import string
from html import escape

# Initialize session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "introduced" not in st.session_state:
        st.session_state.introduced = False  # track if intro done
    if "last_user" not in st.session_state:
        st.session_state.last_user = ""
    if "last_bot" not in st.session_state:
        st.session_state.last_bot = ""
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
        "Make sure to get enough sleep before your exams — rest helps memory!",
        "Practice past papers to get familiar with the format and question types."
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
        "Believe in yourself! Every small step gets you closer to your goals. 🚀",
        "Keep pushing forward, even when it’s tough. Your effort will pay off! 💪",
        "Remember: failure is a part of learning. Don’t give up! 🌟"
    ],
    "study_tips": [
        "Set specific goals for each study session. It helps stay focused and productive.",
        "Use active recall and spaced repetition to remember better.",
        "Take short breaks every 25-30 minutes to keep your brain fresh."
    ],
    "time_management": [
        "Make a daily schedule and stick to it as much as possible.",
        "Prioritize your tasks by importance and deadline.",
        "Avoid multitasking — focus on one thing at a time for better results."
    ],
    "subjects": {
        "math": (
            "Mathematics is the study of numbers, shapes, and patterns. "
            "It helps develop logical thinking and problem-solving skills. "
            "Practicing regularly by solving problems enhances your understanding and confidence."
        ),
        "physics": (
            "Physics explores the laws of nature and how the universe behaves. "
            "It covers topics like motion, energy, and forces. "
            "Understanding physics helps explain everyday phenomena and supports technology development."
        ),
        "chemistry": (
            "Chemistry is the science of matter and how substances interact and change. "
            "It involves studying atoms, molecules, reactions, and materials. "
            "Learning chemistry helps understand everything from cooking to medicine."
        ),
        "biology": (
            "Biology is the study of living things, from tiny cells to whole ecosystems. "
            "It explains how organisms grow, function, and interact with their environment. "
            "Biology is essential for health, environment, and biotechnology."
        ),
        "english": (
            "Learning English improves communication skills in speaking, reading, writing, and listening. "
            "It opens opportunities for education and work worldwide. "
            "Practice daily by reading, speaking, and listening to different types of content."
        ),
        "robotics": (
            "Robotics combines engineering and programming to create machines that can perform tasks. "
            "It involves learning about hardware like sensors and motors, as well as software control. "
            "Robotics is key in automation, AI, and technology innovation."
        ),
        "ai": (
            "Artificial Intelligence (AI) is the field that enables machines to mimic human intelligence. "
            "It uses programming, math, and logic to build systems that learn and adapt. "
            "AI is shaping the future of technology and society."
        )
    },
    "fallback": [
        "Hmm, I’m not sure how to answer that — try rephrasing or asking something about study or motivation! 🤔",
        "I didn’t quite get that, but I’m here to help! Maybe ask about a subject or how you feel. 😊",
        "I'm still learning and improving every day! Feel free to ask me about studying or motivation."
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "greetings", "salam"],
    "how_are_you": ["how are you", "how's it going", "how do you feel"],
    "user_feeling_good": ["i'm fine", "i'm good", "great", "happy", "excellent"],
    "user_feeling_bad": ["i'm sad", "not good", "tired", "depressed", "bad"],
    "love": ["i love you", "you are cute", "like you"],
    "exam_prep": [
        "exam tips", "how to prepare", "study for test", "exam help",
        "give me advice", "advice for exam", "exam advice", "prepare for exam",
        "how to study", "study tips"
    ],
    "passed_exam": ["i passed", "got good mark", "i won"],
    "capabilities": ["what can you do", "your functions", "features"],
    "introduction": ["introduce", "who are you", "your name", "about you", "creator", "who made you"],
    "creator_info": ["who is aylin", "who made you", "your developer"],
    "contact_creator": ["how to contact", "reach aylin", "contact you", "talk to aylin"],
    "ack_creator": ["aylin is cool", "thank aylin", "credit to aylin"],
    "motivation": ["motivate me", "encourage me", "need motivation", "inspire me"],
    "study_tips": ["study tips", "how to study", "study advice"],
    "time_management": ["time management", "manage time", "time planning"],
    "subjects": ["math", "physics", "chemistry", "biology", "english", "robotics", "ai"]
}

# Text cleaner
def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

# Bot reply logic
def get_bot_reply(user_input):
    msg = clean_text(user_input)
    cleaned = {cat: [clean_text(kw) for kw in kws] for cat, kws in KEYWORDS.items()}

    # Special handling for introduction (avoid repeating "Hello!" every time)
    intro_keywords = cleaned.get('introduction', [])
    if any(kw in msg for kw in intro_keywords):
        if not st.session_state.introduced:
            st.session_state.introduced = True
            return random.choice(RESPONSE_DATA['introduction'])
        else:
            # Second time or more - shorter reply
            return "I'm your study chatbot, here to help you learn and stay motivated."

    # Check categories with direct keyword matching
    for cat in [
        'user_feeling_good','user_feeling_bad','love','how_are_you','greetings','exam_prep','capabilities',
        'passed_exam','creator_info','contact_creator','ack_creator','motivation','study_tips','time_management']:
        if any(kw in msg for kw in cleaned.get(cat, [])):
            return random.choice(RESPONSE_DATA[cat])

    # Subjects check (exact subject word in message)
    for subj in cleaned.get('subjects', []):
        if subj in msg and subj in RESPONSE_DATA['subjects']:
            return RESPONSE_DATA['subjects'][subj]

    # Catch-all for any other categories not caught above
    for cat, kws in cleaned.items():
        if cat in [
            'user_feeling_good','user_feeling_bad','love','how_are_you','greetings','exam_prep','capabilities',
            'subjects','passed_exam','introduction','creator_info','contact_creator','ack_creator',
            'motivation','study_tips','time_management']:
            continue
        if cat in RESPONSE_DATA and any(kw in msg for kw in kws):
            return random.choice(RESPONSE_DATA[cat])

    # If no match, fallback with learning message
    fallback_msg = random.choice(RESPONSE_DATA['fallback'])
    return fallback_msg + " I'm still learning."

# Chat form & display
with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        bot_response = get_bot_reply(user_input)
        st.session_state.messages.append({'role': 'bot', 'content': bot_response})

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
