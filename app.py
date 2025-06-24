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
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot 💡📚</h1></div>', unsafe_allow_html=True)

# RESPONSE DATA
RESPONSE_DATA = {
    "greetings": [
        "Hello there! 👋 How’s your day going? Ready to dive into learning today? 📖",
        "Hey hey! 🌟 Hope you’re feeling inspired today. What’s on your mind? 🤔",
        "Hi friend! 😊 I’m here for you — whether you want to study, vent, or just chat. 💬"
    ],
    "how_are_you": [
        "I'm doing well, thanks for asking! 💬 How are you feeling today? 😊",
        "Feeling smart and helpful — as always! 😎 How can I assist you today? 🤓"
    ],
    "user_feeling_good": [
        "That’s amazing to hear! 🎉 Keep riding that good energy! 🚀",
        "Awesome! Let’s keep the momentum going! 💪✨"
    ],
    "user_feeling_bad": [
        "Sorry to hear that. I’m always here if you want to talk or need a study boost. 💙🌈",
        "Tough days happen — but you’ve got this. One step at a time. 🐾🌟"
    ],
    "exam_prep": [
        "Start early, make a plan, and review consistently. 📚 You’re capable of great things! 💫",
        "Break topics into chunks and take breaks in between. You’ll learn smarter! 💡🧠",
        "Practice past papers under timed conditions — it really helps! ⏰📝",
        "Don’t cram last minute. Get good sleep and eat well before the exam! 😴🍎",
        "I’m still learning, but these tips work wonders for many students! 🌟"
    ],
    "passed_exam": [
        "🎉 CONGRATULATIONS! That’s amazing news! I knew you could do it. 🏆",
        "Woohoo! So proud of you! 🥳 What’s next on your journey? 🌍"
    ],
    "love": [
        "Aww 💖 That's sweet! I'm just code, but I support you 100%! 🤗",
        "Sending you virtual hugs and happy vibes 💕✨"
    ],
    "capabilities": [
        "I can give study tips, answer basic academic questions, track your mood, and motivate you. 🤓📚",
        "I'm designed to help students stay focused and positive. Ask me anything about learning! 💬🌱"
    ],
    "introduction": [
        "I'm AverlinMz, your study chatbot 🌱. My creator is Aylin Muzaffarli (b.2011, Azerbaijan). She loves music, programming, robotics, AI, physics, and more. Reach her at averlinmz.github.io! 🌐"
    ],
    "creator_info": [
        "I was created by Aylin Muzaffarli — a passionate student from Azerbaijan who codes, studies physics and AI, and inspires others! 💡💻",
        "My developer is Aylin Muzaffarli, born in 2011. She built me to support learners like you! 🎓✨"
    ],
    "contact_creator": [
        "You can reach my creator via GitHub: https://github.com/AverlinMz or her site: https://averlinmz.github.io ✨📬",
        "Visit https://averlinmz.github.io or https://github.com/AverlinMz to get in touch! 💬🌟"
    ],
    "ack_creator": [
        "Yes, Aylin is super talented! 😄🌟",
        "Absolutely! All credit goes to Aylin Muzaffarli! 🎉💖"
    ],
    "motivation": [
        "Keep pushing forward, every step counts! 🚀🌈",
        "Remember why you started and keep your goals in sight! 🎯✨",
        "I’m here to support you whenever you feel stuck. You got this! 💪💙"
    ],
    "study_tips": [
        "Try to study in focused 25-minute sessions with 5-minute breaks (Pomodoro technique). ⏲️📚",
        "Make summaries of what you learn — writing helps memory. ✍️🧠",
        "Use flashcards to memorize facts and formulas. 🃏🎯"
    ],
    "time_management": [
        "Make a daily schedule and prioritize your tasks. 📅✅",
        "Avoid multitasking — focus on one thing at a time. 🎯📌",
        "Use timers to keep track of study and rest periods. ⏰✨"
    ],
    "subjects": {
        "math": (
            "Math is the language of patterns and logic. Here are some tips:\n"
            "1️⃣ Practice problem-solving daily to build strong skills. 🧮\n"
            "2️⃣ Understand concepts, don’t just memorize formulas. 🧠\n"
            "3️⃣ Work on past exam problems to get familiar with question types. 📚\n"
            "4️⃣ Use visual aids like graphs and diagrams when possible. 📊\n"
            "5️⃣ Study in groups to explain and clarify topics with peers. 🤝"
        ),
        "physics": (
            "Physics explains how the universe works. Try these steps:\n"
            "1️⃣ Start with core concepts like motion and forces. 🚀\n"
            "2️⃣ Solve practical problems and run simple experiments. 🔬\n"
            "3️⃣ Use simulations or videos to visualize difficult topics. 🎥\n"
            "4️⃣ Review formulas regularly but focus on understanding their meaning. 📐\n"
            "5️⃣ Relate concepts to real-world applications to stay motivated. 🌍"
        ),
        "chemistry": (
            "Chemistry is the study of matter and reactions. Tips:\n"
            "1️⃣ Learn the periodic table and element properties. 🧪\n"
            "2️⃣ Practice writing and balancing chemical equations. ⚖️\n"
            "3️⃣ Understand reaction types and mechanisms. 🔥\n"
            "4️⃣ Perform lab exercises carefully and note observations. 🧴\n"
            "5️⃣ Use mnemonic devices to remember groups and formulas. 🧠"
        ),
        "biology": (
            "Biology explores life from cells to ecosystems. Study advice:\n"
            "1️⃣ Memorize key terms but focus on understanding processes. 🧬\n"
            "2️⃣ Use diagrams for anatomy, cell structure, and food chains. 🌿\n"
            "3️⃣ Relate concepts like photosynthesis or respiration to daily life. ☀️\n"
            "4️⃣ Practice with quizzes to test your knowledge. ✅\n"
            "5️⃣ Study regularly to retain lots of detailed information. 📖"
        ),
        "english": (
            "Improving English takes practice. Here’s how:\n"
            "1️⃣ Read a variety of texts — stories, articles, and essays. 📚\n"
            "2️⃣ Write summaries or journal entries regularly. 📝\n"
            "3️⃣ Practice speaking with friends or language partners. 🗣️\n"
            "4️⃣ Learn new vocabulary in context rather than isolation. 🧠\n"
            "5️⃣ Listen to podcasts or watch shows in English to improve comprehension. 🎧"
        ),
        "robotics": (
            "Robotics combines coding and hardware. Tips:\n"
            "1️⃣ Start learning basic programming languages like Python or C++. 💻\n"
            "2️⃣ Understand hardware components — sensors, motors, microcontrollers. 🤖\n"
            "3️⃣ Build small projects to apply what you learn practically. 🛠️\n"
            "4️⃣ Participate in robotics clubs or competitions. 🏆\n"
            "5️⃣ Study electronics fundamentals alongside coding. ⚡"
        ),
        "ai": (
            "Artificial Intelligence is a growing field. Here’s a start:\n"
            "1️⃣ Learn Python programming and math basics (linear algebra, calculus). 🧮\n"
            "2️⃣ Study machine learning concepts like supervised and unsupervised learning. 🤖\n"
            "3️⃣ Practice with projects like image recognition or chatbots. 💬\n"
            "4️⃣ Explore AI ethics and real-world applications. ⚖️\n"
            "5️⃣ Keep updated with new research and tools in AI. 📡"
        ),
        "computer science": (
            "Computer Science focuses on algorithms and software. Tips:\n"
            "1️⃣ Master programming basics (variables, loops, functions). 💻\n"
            "2️⃣ Study data structures and algorithms thoroughly. 📊\n"
            "3️⃣ Practice coding problems regularly on platforms like Codeforces. 🕹️\n"
            "4️⃣ Work on small projects to apply concepts. 🛠️\n"
            "5️⃣ Learn about computer systems, networking, and databases. 🌐"
        ),
        "art": (
            "Art is about creativity and technique. Here are some tips:\n"
            "1️⃣ Practice sketching daily to improve your hand skills. ✏️\n"
            "2️⃣ Study color theory and composition. 🎨\n"
            "3️⃣ Experiment with different mediums and styles. 🖌️\n"
            "4️⃣ Analyze works of famous artists for inspiration. 🖼️\n"
            "5️⃣ Join art communities to get feedback and grow. 👩‍🎨"
        ),
        "language": (
            "Learning a new language requires practice and patience:\n"
            "1️⃣ Immerse yourself by listening and speaking daily. 🗣️\n"
            "2️⃣ Learn grammar basics and build vocabulary gradually. 📚\n"
            "3️⃣ Use language apps and flashcards for memorization. 📱\n"
            "4️⃣ Practice writing short texts and conversations. ✍️\n"
            "5️⃣ Engage with native speakers or language exchange partners. 🌍"
        )
    },
    "fallback": [
        "Hmm, I’m not sure how to answer that — try rephrasing or asking something about study or motivation! 🤔 I'm still learning. 📚",
        "I didn’t quite get that, but I’m here to help! Maybe ask about a subject or how you feel. 😊 I'm still learning! 💡"
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "greetings", "salam"],
    "how_are_you": ["how are you", "how's it going", "how do you feel"],
    "user_feeling_good": ["i'm fine", "i'm good", "great", "happy", "excellent"],
    "user_feeling_bad": ["i'm sad", "not good", "tired", "depressed", "bad"],
    "love": ["i love you", "you are cute", "like you"],
    "exam_prep": ["exam tips", "how to prepare", "study for test", "exam help", "give me tip for exam prep", "advise for exam"],
    "passed_exam": ["i passed", "got good mark", "i won"],
    "capabilities": ["what can you do", "your functions", "features"],
    "introduction": ["introduce", "who are you", "your name", "about you", "creator", "who made you"],
    "creator_info": ["who is aylin", "who made you", "your developer", "tell me about aylin"],
    "contact_creator": ["how to contact", "reach aylin", "contact you", "talk to aylin"],
    "ack_creator": ["aylin is cool", "thank aylin", "credit to aylin"],
    "motivation": ["motivate me", "inspire me", "encourage me"],
    "study_tips": ["study tips", "tips to study", "how to study", "studying advice"],
    "time_management": ["time management", "manage time", "schedule study"],
    "subjects": ["math", "physics", "chemistry", "biology", "english", "robotics", "ai", "computer science", "art", "language"]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    cleaned = {cat: [clean_text(kw) for kw in kws] for cat, kws in KEYWORDS.items()}

    # Greetings
    if any(kw in msg for kw in cleaned.get('greetings', [])):
        return random.choice(RESPONSE_DATA['greetings'])

    # How are you
    if any(kw in msg for kw in cleaned.get('how_are_you', [])):
        return random.choice(RESPONSE_DATA['how_are_you'])

    # User feeling good
    if any(kw in msg for kw in cleaned.get('user_feeling_good', [])):
        return random.choice(RESPONSE_DATA['user_feeling_good'])

    # User feeling bad
    if any(kw in msg for kw in cleaned.get('user_feeling_bad', [])):
        return random.choice(RESPONSE_DATA['user_feeling_bad'])

    # Love
    if any(kw in msg for kw in cleaned.get('love', [])):
        return random.choice(RESPONSE_DATA['love'])

    # Introduction: special case to avoid repeated hello
    if any(kw in msg for kw in cleaned.get('introduction', [])):
        if not st.session_state.answered_intro:
            st.session_state.answered_intro = True
            return random.choice(RESPONSE_DATA['introduction'])
        else:
            return "I’m AverlinMz, your study chatbot created by Aylin Muzaffarli. Ask me anything about learning! 🌱"

    # Creator info
    if any(kw in msg for kw in cleaned.get('creator_info', [])):
        return random.choice(RESPONSE_DATA['creator_info'])

    # Contact creator
    if any(kw in msg for kw in cleaned.get('contact_creator', [])):
        return random.choice(RESPONSE_DATA['contact_creator'])

    # Motivation
    if any(kw in msg for kw in cleaned.get('motivation', [])):
        return random.choice(RESPONSE_DATA['motivation'])

    # Study tips
    if any(kw in msg for kw in cleaned.get('study_tips', [])):
        return random.choice(RESPONSE_DATA['study_tips'])

    # Time management
    if any(kw in msg for kw in cleaned.get('time_management', [])):
        return random.choice(RESPONSE_DATA['time_management'])

    # Passed exam
    if any(kw in msg for kw in cleaned.get('passed_exam', [])):
        return random.choice(RESPONSE_DATA['passed_exam'])

    # Capabilities
    if any(kw in msg for kw in cleaned.get('capabilities', [])):
        return random.choice(RESPONSE_DATA['capabilities'])

    # Subjects detailed answers
    for subj in cleaned.get('subjects', []):
        if subj in msg and subj in RESPONSE_DATA['subjects']:
            return RESPONSE_DATA['subjects'][subj]

    # Exam prep catch all
    if any(kw in msg for kw in cleaned.get('exam_prep', [])):
        return random.choice(RESPONSE_DATA['exam_prep'])

    # Fallback with extra info
    return random.choice(RESPONSE_DATA['fallback'])

# Chat form & display
with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        st.session_state.messages.append({'role': 'bot', 'content': get_bot_reply(user_input)})
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
        "- 'Give me study tips' 📚\n"
        "- 'Tell me about physics' 🚀\n"
        "- 'How do I manage time?' ⏳\n"
        "- 'Motivate me please!' 💪\n"
        "- 'Who created you?' 👩‍💻\n"
        "- 'Give me advice for exam prep' 📝\n"
        "- 'Tell me about Aylin' 🌟\n"
    )
