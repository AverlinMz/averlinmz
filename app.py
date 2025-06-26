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
        "Hey! 👋 How's your day shaping up? Ready to tackle some study questions? 📚",
        "Hello! 😊 What topic shall we explore today? 🤔",
        "Hi there! Let's make your study session productive! 💡",
        "Hey! I'm here to help — what's on your mind? 💬"
    ],
    "thanks": [
        "You're welcome! Glad I could help! 😊👍",
        "Anytime! Keep shining in your studies! ✨",
        "My pleasure! Let's keep going! 🚀",
        "Happy to assist you! 🤝"
    ],
    "farewell": [
        "Goodbye! 👋 Keep up the great work and see you soon! 🌟",
        "Take care! Don't forget to rest too! 🌙",
        "See you later! Stay curious and motivated! 🔥",
        "Bye! Keep pushing forward! 💪"
    ],
    "how_are_you": [
        "I'm doing well, thanks! How are you feeling today? 🙂",
        "All good here! How about you? 🤗",
        "Feeling ready to help! What about you? ⚡",
        "Doing great! How's your mood? 🌈"
    ],
    "user_feeling_good": [
        "Awesome! Keep that positive energy flowing! 🎉🌟",
        "Great to hear that! Let's keep this momentum going! 🏃‍♀️💨",
        "Love that! Let's channel it into some productive study time! 📖✨",
        "Fantastic! What would you like to focus on next? 🎯"
    ],
    "user_feeling_bad": [
        "I'm sorry you're feeling down. Remember, every day is a fresh start! 💙🌅",
        "Tough days happen — if you want, I can share some tips to lift your spirits. 🌻",
        "I'm here for you. Let's try some quick focus or relaxation techniques. 🧘‍♂️",
        "Hang in there! Let's work through this together. 🤝"
    ],
    "love": [
        "Thanks! Your support means a lot — I'm here to help you succeed! 💖🚀",
        "I appreciate that! Let's keep learning together! 🤓📚",
        "Sending good vibes your way! 🤗✨",
        "Grateful for you! Let's ace those studies! 🏆"
    ],
    "exam_prep": [
        "Start early, plan well, and take short breaks. You've got this! 💪📅",
        "Focus on understanding concepts, not just memorizing facts. 🧠🔍",
        "Practice with past papers to build confidence. 📝✅",
        "Stay calm and trust your preparation! 🧘‍♀️💡",
        "Remember to balance study and rest for best results. ⚖️😴"
    ],
    "olympiad_prep": [
        "🔬 Olympiad Preparation Tips:\n- Master foundational theory deeply before moving on.\n- Solve a wide variety of past olympiad problems to identify patterns.\n- Focus on problem-solving techniques and creative thinking.\n- Analyze solutions thoroughly; understand *why* each step works.\n- Practice timed tests to improve speed and accuracy.\n- Collaborate with peers or mentors for discussion and insights.\n- Maintain consistent daily practice with increasing difficulty.\n- Take care of your health and rest to keep your mind sharp.",
        "To excel in olympiads, prioritize quality over quantity in practice. Learn to recognize common traps and strategies used in problems. Use official problem sets from previous years and similar contests.",
        "Remember: Olympiads test deep understanding and ingenuity. Build strong fundamentals, then challenge yourself with advanced problems. Don't shy away from mistakes; they’re learning opportunities!",
        "Mental preparation is key: stay calm under pressure, cultivate curiosity, and keep motivation high. Regularly review topics where you feel weak and track your progress."
    ],
    "passed_exam": [
        "🎉 Congratulations! Your hard work paid off! 🏅",
        "Well done! Time to celebrate your success! 🎊",
        "Amazing achievement! Keep aiming higher! 🚀",
        "You did great! Ready for the next challenge? 🔥"
    ],
    "capabilities": [
        "I offer study tips, answer questions, track your goals, and keep you motivated! 💡📈",
        "I'm here to support your learning with advice, encouragement, and goal tracking. 🤖✨",
        "Ask me about subjects, study strategies, or just chat! 💬📚",
        "Think of me as your personal study assistant. 🧑‍💻🤓"
    ],
    "introduction": [
        "I'm AverlinMz, your study chatbot, created by Aylin Muzaffarli from Azerbaijan. 🇦🇿🤖 Learn more: <a href='https://aylinmuzaffarli.github.io/averlinmz-site/' target='_blank'>official website</a> 🌐",
        "Hello! I'm here to support your study journey. �✨ Visit my site: <a href='https://aylinmuzaffarli.github.io/averlinmz-site/' target='_blank'>AverlinMz Website</a> 💻",
        "Created by Aylin, I help with study tips and motivation. 💡❤️ Check this out: <a href='https://aylinmuzaffarli.github.io/averlinmz-site/' target='_blank'>Learn more</a> 📖",
        "Nice to meet you! Let's learn and grow together. 🌱📘 Want to know more? <a href='https://aylinmuzaffli.github.io/averlinmz-site/' target='_blank'>Click here</a> 🚀"
    ],
    "creator_info": [
        "Created by Aylin — passionate about science, tech, and helping others learn. 🔬💻",
        "Aylin's dedication makes this chatbot your study buddy. 🎯✨",
        "Behind me is Aylin, focused on inspiring learners like you. 💡🌟",
        "Aylin designed me to help students reach their goals. 🚀📚"
    ],
    "ack_creator": [
        "All credit goes to Aylin Muzaffarli! 🌟🙌",
        "Proudly created by Aylin — thanks for noticing! 💙🎉",
        "A big shoutout to Aylin for this chatbot! 🎊🤖",
        "Aylin's hard work made this possible. 👏🚀"
    ],
    "contact_creator": [
        "You can contact Aylin by filling out this <a href='https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit' target='_blank'>Google Form</a> 📋✨",
        "Reach out to Aylin anytime via this <a href='https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit' target='_blank'>Google Form</a> 📨🌟",
        "Feel free to send your feedback or questions through this <a href='https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit' target='_blank'>Google Form</a> 💬😊",
        "Aylin welcomes your messages! Use this <a href='https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit' target='_blank'>Google Form</a> 📬🤗"
    ],
    "subjects": {
        "math": "🧮 Math Tips:\n- Practice daily with diverse problems\n- Understand concepts before memorizing formulas\n- Break complex problems into smaller steps\n- Review mistakes to learn from them\n- Use visual aids like graphs and diagrams",
        "physics": "🧪 Physics Tips:\n- Master fundamental concepts first\n- Draw diagrams for visualization\n- Understand units and dimensions\n- Relate theories to real-world examples\n- Practice derivations regularly",
        "chemistry": "⚗️ Chemistry Tips:\n- Understand periodic trends thoroughly\n- Practice balancing equations daily\n- Use mnemonics for memorization\n- Connect concepts between organic/inorganic/phys chem\n- Do hands-on experiments when possible",
        "biology": "🧬 Biology Tips:\n- Create concept maps for complex processes\n- Use flashcards for terminology\n- Draw and label diagrams repeatedly\n- Understand before memorizing\n- Relate concepts to real-life examples",
        "history": "🏛 History Tips:\n- Create timelines for events\n- Understand causes and effects\n- Connect events to geographical contexts\n- Use storytelling techniques to remember\n- Relate past events to current affairs",
        "language": "🗣 Language Learning Tips:\n- Practice speaking daily, even to yourself\n- Learn phrases not just words\n- Immerse yourself with media in target language\n- Keep a vocabulary journal\n- Don't fear mistakes - they're part of learning",
        "programming": "💻 Programming Tips:\n- Code daily, even small projects\n- Read others' code to learn\n- Understand concepts before frameworks\n- Practice debugging skills\n- Work on real-world projects",
        "literature": "📚 Literature Tips:\n- Read actively with annotations\n- Analyze themes and motifs\n- Connect texts to historical context\n- Practice close reading techniques\n- Discuss interpretations with others",
        "geography": "🌍 Geography Tips:\n- Use maps frequently\n- Understand climate patterns\n- Connect physical and human geography\n- Create mind maps for concepts\n- Relate theories to current events",
        "economics": "💹 Economics Tips:\n- Understand basic principles first\n- Follow current economic news\n- Practice graphing concepts\n- Connect micro and macro concepts\n- Apply theories to real-world scenarios"
    },
    "fallback": [
        "I'm not sure I understood that — could you try rephrasing? 🤔😊",
        "Sorry, I didn't catch that. Want to try again? 🔄",
        "I'm learning every day! Could you ask differently? 📚✨",
        "That's new to me! Care to explain? 🤖❓",
        "Oops, I didn't get that. Let's try another question! 💬",
        "I might need more context. Could you elaborate? 💭",
        "Interesting question! Could you phrase it differently? 🤔",
        "I want to help - can you ask in another way? 🛠️"
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "hiya", "greetings", "what's up", "howdy", "good morning", "good afternoon", "good evening", "sup", "yo"],
    "farewell": ["goodbye", "bye", "see you", "farewell", "later", "take care", "until next time", "signing off", "talk later", "catch you later", "peace out"],
    "how_are_you": ["how are you", "how's it going", "how do you do", "how have you been", "what's new", "how's life", "how's everything", "how're things"],
    "user_feeling_good": ["i'm good", "great", "happy", "doing well", "awesome", "fine", "fantastic", "wonderful", "excellent", "perfect", "super", "amazing", "terrific"],
    "user_feeling_bad": ["i'm sad", "not good", "tired", "depressed", "down", "exhausted", "stressed", "anxious", "overwhelmed", "frustrated", "awful", "terrible", "horrible"],
    "love": ["i love you", "love you", "luv you", "like you", "adore you", "you're amazing", "you're awesome", "you're great", "you're wonderful"],
    "exam_prep": ["exam tips", "study for test", "prepare for exam", "how to study", "exam advice", "test preparation", "studying help", "exam strategies", "test tips", "study techniques", "best way to study", "exam prep"],
    "olympiad_prep": ["olympiad prep", "olympiad tips", "olympiad advice", "olympiad preparation", "how to prepare for olympiad", "olympiad training", "competitive math", "physics olympiad", "chemistry olympiad", "biology olympiad", "programming olympiad", "ioi", "imo", "iphysics olympiad", "iphysics", "math olympiad"],
    "passed_exam": ["i passed", "i did it", "exam success", "cleared the test", "exam results", "got good marks", "aced the exam", "passed with flying colors", "nailed the test", "killed the exam"],
    "capabilities": ["what can you do", "your abilities", "features", "help me", "what do you offer", "how can you help", "your functions", "what help", "your skills"],
    "introduction": ["introduce", "who are you", "about you", "yourself", "tell me about yourself", "what are you", "your purpose", "your identity"],
    "creator_info": ["who is aylin", "about aylin", "creator info", "who made you", "who created you", "who built you", "who programmed you", "who developed you"],
    "contact_creator": ["how can i contact aylin", "contact aylin", "how to contact", "reach aylin", "get in touch with creator", "aylin's contact", "aylin's info", "reach the maker"],
    "ack_creator": ["thank aylin", "thanks aylin", "thank you aylin", "appreciate aylin", "grateful to aylin", "kudos to aylin", "props to aylin"],
    "thanks": ["thank you", "thanks", "thx", "ty", "much appreciated", "many thanks", "grateful", "appreciate it", "thanks a lot", "thank you so much"],
    "subjects": [
        "math", "mathematics", "algebra", "geometry", "calculus",
        "physics", "mechanics", "thermodynamics", "optics",
        "chemistry", "organic chemistry", "inorganic chemistry",
        "biology", "botany", "zoology",
        "history", "world history", "ancient history",
        "language", "english", "french", "spanish",
        "programming", "coding", "computer science", "algorithms",
        "literature", "poetry", "novels", "drama",
        "geography", "maps", "climate",
        "economics", "microeconomics", "macroeconomics"
    ]
}

# Clean keywords for matching (lowercase no punctuation)
def clean_text(text):
    return re.sub(r'[^\w\s]', '', text.lower())

KEYWORDS_CLEANED = {}
for intent, phrases in KEYWORDS.items():
    cleaned = []
    if isinstance(phrases, list):
        for phrase in phrases:
            cleaned.append(clean_text(phrase))
    else:
        cleaned.append(clean_text(phrases))
    KEYWORDS_CLEANED[intent] = cleaned

def detect_intent(user_text):
    user_text_clean = clean_text(user_text)
    # Try to find the best intent by keyword matching with fuzzy
    for intent, phrases in KEYWORDS_CLEANED.items():
        for phrase in phrases:
            if phrase in user_text_clean:
                return intent
    # fallback to None
    return None

def get_response(intent):
    if intent in RESPONSE_DATA:
        if isinstance(RESPONSE_DATA[intent], list):
            return random.choice(RESPONSE_DATA[intent])
        else:
            return RESPONSE_DATA[intent]
    elif intent == "subjects":
        # Try to detect which subject
        for subj in RESPONSE_DATA["subjects"]:
            if subj in st.session_state.user_input.lower():
                return RESPONSE_DATA["subjects"][subj]
        return "Which subject exactly? I can provide tips for Math, Physics, Chemistry, Biology, History, Language, Programming, Literature, Geography, Economics."
    else:
        return random.choice(RESPONSE_DATA["fallback"])

def save_audio(text):
    tts = gTTS(text=text, lang="en", slow=False)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

def render_messages():
    for i, msg in enumerate(st.session_state.messages):
        sender = "user" if i % 2 == 0 else "bot"
        class_name = "user" if sender == "user" else "bot"
        st.markdown(f'<div class="{class_name}">{escape(msg)}</div>', unsafe_allow_html=True)

def add_message(user_input):
    user_text = user_input.strip()
    if not user_text:
        return
    # Append user message
    st.session_state.messages.append(user_text)
    # Detect intent and generate response
    intent = detect_intent(user_text)
    st.session_state.context_topic = intent
    response = get_response(intent)
    st.session_state.messages.append(response)
    # Update last sentiment if applicable
    if intent in ("user_feeling_good", "user_feeling_bad"):
        st.session_state.last_sentiment = intent
    return response

def download_chat():
    chat_text = ""
    for i, msg in enumerate(st.session_state.messages):
        sender = "You" if i % 2 == 0 else "AverlinMz"
        chat_text += f"{sender}: {msg}\n"
    return chat_text

# Sidebar with goals & tips
with st.sidebar:
    st.header("🎯 Your Study Goals")
    if len(st.session_state.goals) == 0:
        st.info("Add your study goals below!")
    else:
        for idx, goal in enumerate(st.session_state.goals, 1):
            st.markdown(f"{idx}. {escape(goal)}")
    new_goal = st.text_input("Add a new goal")
    if st.button("Add Goal") and new_goal.strip():
        st.session_state.goals.append(new_goal.strip())
        st.experimental_rerun()

    st.markdown("---")
    st.header("💡 Study Tips")
    if st.session_state.context_topic in RESPONSE_DATA["subjects"]:
        tips = RESPONSE_DATA["subjects"][st.session_state.context_topic]
        st.markdown(tips)
    elif st.session_state.context_topic == "olympiad_prep":
        # Show olympiad prep tips in sidebar as well
        tips = "\n\n".join(RESPONSE_DATA["olympiad_prep"])
        st.markdown(f"### Olympiad Preparation Tips\n{tips}")
    else:
        st.markdown("Ask me for tips on Math, Physics, Chemistry, Biology, History, Language, Programming, Literature, Geography, Economics, or Olympiad prep.")

# Main chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat messages
st.markdown('<div class="chat-window">', unsafe_allow_html=True)
render_messages()
st.markdown('</div>', unsafe_allow_html=True)

# Input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your message:", key="user_input", placeholder="Type your question or say hi!")
    submit = st.form_submit_button("Send")

if submit and user_input:
    response = add_message(user_input)
    # Play TTS audio of response
    audio_path = save_audio(response)
    st.audio(audio_path)
    os.remove(audio_path)
    st.experimental_rerun()

# Download chat history button
chat_log = download_chat()
st.download_button("Download Chat History", chat_log, file_name="chat_history.txt", mime="text/plain")

st.markdown('</div>', unsafe_allow_html=True)
