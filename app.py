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
    if "last_bot_reply" not in st.session_state:
        st.session_state.last_bot_reply = ""
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

# RESPONSE DATA with exam prep tips & updated contact info
RESPONSE_DATA = {
    "greetings": [
        "Hello there! 👋 How’s your day going? Ready to dive into learning today? 😊",
        "Hey hey! 🌟 Hope you’re feeling inspired today. What’s on your mind? 🤔",
        "Hi friend! 😊 I’m here for you — whether you want to study, vent, or just chat. 💬"
    ],
    "how_are_you": [
        "I'm doing well, thanks for asking! 💬 How are you feeling today? 🙂",
        "Feeling smart and helpful — as always! 😊 How can I assist you today? 🧠"
    ],
    "user_feeling_good": [
        "That’s amazing to hear! 🎉 Keep riding that good energy! 🌈",
        "Awesome! Let’s keep the momentum going! 💪🚀"
    ],
    "user_feeling_bad": [
        "Sorry to hear that. I’m always here if you want to talk or need a study boost. 💙🌟",
        "Tough days happen — but you’ve got this. One step at a time. 🐾✨"
    ],
    "exam_prep": [
        "1️⃣ Start your preparation early and make a study plan. 📅",
        "2️⃣ Break topics into manageable chunks and take regular breaks. 🧩",
        "3️⃣ Practice past exam papers to get familiar with the format. 📝",
        "4️⃣ Get enough sleep and stay hydrated to keep your brain sharp. 🛌💧",
        "You’re capable of great things! Keep pushing! 📚💡"
    ],
    "passed_exam": [
        "🎉 CONGRATULATIONS! That’s amazing news! I knew you could do it. 🎊",
        "Woohoo! So proud of you! 🥳 What’s next on your journey? 🌟"
    ],
    "love": [
        "Aww 💖 That's sweet! I'm just code, but I support you 100%! 🤖💕",
        "Sending you virtual hugs and happy vibes 💕🤗"
    ],
    "capabilities": [
        "I can give study tips, answer basic academic questions, track your mood, and motivate you. 🤓📚",
        "I'm designed to help students stay focused and positive. Ask me anything about learning! 💬✨"
    ],
    "introduction": [
        "I'm AverlinMz, your study chatbot 🌱. My creator is Aylin Muzaffarli (b.2011, Azerbaijan). She loves music, programming, robotics, AI, physics, and more. 🌟"
    ],
    "creator_info": [
        "I was created by Aylin Muzaffarli — a passionate student from Azerbaijan who codes, studies physics and AI, and inspires others! 💡",
        "My developer is Aylin Muzaffarli, born in 2011. She built me to support learners like you! 🚀"
    ],
    "contact_creator": [
        "You can reach my creator via GitHub: https://github.com/AverlinMz ✨",
        "To contact Aylin, visit her GitHub profile at https://github.com/AverlinMz 💬"
    ],
    "ack_creator": [
        "Yes, Aylin is super talented! 😄🎉",
        "Absolutely! All credit goes to Aylin Muzaffarli! 🌟👏"
    ],
    "subjects": {
        "math": "Math is about patterns and practice. 1️⃣ Practice problems daily. 2️⃣ Focus on understanding concepts, not memorizing. 3️⃣ Use visual aids like graphs. ➕➗📐",
        "physics": "Physics explains how the universe works. 1️⃣ Start with basics like mechanics. 2️⃣ Use diagrams to visualize. 3️⃣ Solve lots of problems. 🚀⚙️",
        "chemistry": "Chemistry is about matter and reactions. 1️⃣ Learn the periodic table. 2️⃣ Understand bonding and reactions. 3️⃣ Do lab exercises if possible. 🔬⚗️",
        "biology": "Biology studies life. 1️⃣ Memorize key terms. 2️⃣ Understand processes like photosynthesis. 3️⃣ Use charts and diagrams. 🧬🌱",
        "english": "English learning is fun! 1️⃣ Read books and articles daily. 2️⃣ Practice speaking with friends or online. 3️⃣ Write short essays or journals. 📖🗣️",
        "robotics": "Robotics combines hardware and coding. 1️⃣ Start with microcontrollers like Arduino. 2️⃣ Learn basic programming. 3️⃣ Build simple projects. 🤖💻",
        "ai": "AI is a growing field. 1️⃣ Learn Python programming. 2️⃣ Study math fundamentals (algebra, calculus). 3️⃣ Explore machine learning basics. 🧠🤖",
        "computer science": "CS is about algorithms and coding. 1️⃣ Practice coding daily. 2️⃣ Understand data structures. 3️⃣ Solve problems on coding sites. 💻🖥️",
        "art": "Art helps creativity. 1️⃣ Draw/sketch regularly. 2️⃣ Study art history. 3️⃣ Experiment with different mediums. 🎨🖌️",
        "languages": "Learning languages takes practice. 1️⃣ Immerse yourself daily. 2️⃣ Use apps for vocab and grammar. 3️⃣ Practice speaking and listening. 🌍🗣️"
    },
    "fallback": [
        "Hmm, I’m not sure how to answer that — try rephrasing or asking something about study or motivation! 🤔 I'm still learning. 📚",
        "I didn’t quite get that, but I’m here to help! Maybe ask about a subject or how you feel. 😊 I'm still learning. 🤖"
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "greetings", "salam"],
    "how_are_you": ["how are you", "how's it going", "how do you feel"],
    "user_feeling_good": ["i'm fine", "i'm good", "great", "happy", "excellent"],
    "user_feeling_bad": ["i'm sad", "not good", "tired", "depressed", "bad"],
    "love": ["i love you", "you are cute", "like you"],
    "exam_prep": ["exam tips", "how to prepare", "study for test", "exam help", "give me advice for exam prep", "give me tip for exam prep"],
    "passed_exam": ["i passed", "got good mark", "i won", "i succeeded"],
    "capabilities": ["what can you do", "your functions", "features", "what do you do"],
    "introduction": ["introduce", "who are you", "your name", "about you", "creator", "who made you"],
    "creator_info": ["who is aylin", "who made you", "your developer", "tell me about aylin"],
    "contact_creator": [
        "how to contact", "how can i contact", "how can i contact to", "reach aylin", "contact you", "talk to aylin"
    ],
    "ack_creator": ["aylin is cool", "thank aylin", "credit to aylin"],
    "subjects": ["math", "physics", "chemistry", "biology", "english", "robotics", "ai", "computer science", "art", "languages"]
}

# Text cleaner
def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

# Bot reply logic with memory and better "who are you?" handling
def get_bot_reply(user_input):
    msg = clean_text(user_input)
    cleaned = {cat: [clean_text(kw) for kw in kws] for cat, kws in KEYWORDS.items()}

    # Special handling for first-time introduction (do not repeat "Hello" after first)
    if any(kw in msg for kw in cleaned['introduction']):
        if st.session_state.last_bot_reply == "":
            reply = random.choice(RESPONSE_DATA['introduction'])
        else:
            # Avoid repeating full intro greeting
            reply = "I'm AverlinMz, your friendly study chatbot 🌱. Ask me about studying, exams, or motivation! 😊"
        st.session_state.last_user_input = user_input
        st.session_state.last_bot_reply = reply
        return reply

    # Check keyword categories in priority order
    for cat in [
        'user_feeling_good','user_feeling_bad','love','how_are_you','greetings',
        'exam_prep','capabilities','passed_exam','creator_info','contact_creator','ack_creator'
    ]:
        if any(kw in msg for kw in cleaned.get(cat, [])):
            reply = random.choice(RESPONSE_DATA[cat])
            st.session_state.last_user_input = user_input
            st.session_state.last_bot_reply = reply
            return reply

    # Subject handling
    for subj in cleaned.get('subjects', []):
        if subj in msg and subj in RESPONSE_DATA['subjects']:
            reply = RESPONSE_DATA['subjects'][subj]
            st.session_state.last_user_input = user_input
            st.session_state.last_bot_reply = reply
            return reply

    # Catch-all keyword check (any other categories)
    for cat, kws in cleaned.items():
        if cat in ['user_feeling_good','user_feeling_bad','love','how_are_you','greetings',
                   'exam_prep','capabilities','subjects','passed_exam','introduction',
                   'creator_info','contact_creator','ack_creator']:
            continue
        if cat in RESPONSE_DATA and any(kw in msg for kw in kws):
            reply = random.choice(RESPONSE_DATA[cat])
            st.session_state.last_user_input = user_input
            st.session_state.last_bot_reply = reply
            return reply

    # If user asked something but bot doesn't know:
    fallback_reply = random.choice(RESPONSE_DATA['fallback'])
    st.session_state.last_user_input = user_input
    st.session_state.last_bot_reply = fallback_reply
    return fallback_reply

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
    st.info("You can ask things like:\n- 'Give me study tips'\n- 'Tell me about physics'\n- 'How do I manage time?'\n- 'Motivate me please!'\n- 'Who created you?'\n- 'How can I contact Aylin?'\n- 'Give me advice for exam prep'\n")
