import streamlit as st
import random
import string
import datetime
import re
import tempfile
import os
from html import escape
from gtts import gTTS
from hashlib import sha256

# --------------- AUTHENTICATION ----------------
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Simple in-memory user DB (not persistent)
USER_DB = {"aylin": hash_password("password123")}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.auth_error = None

def login_ui():
    st.sidebar.title("🔐 Login / Sign Up")
    mode = st.sidebar.radio("Mode", ["Login", "Sign Up"])
    user = st.sidebar.text_input("Username", key="auth_user")
    pwd = st.sidebar.text_input("Password", type="password", key="auth_pass")
    if st.sidebar.button("Submit"):
        hashed = hash_password(pwd)
        if mode == "Login":
            if user in USER_DB and USER_DB[user] == hashed:
                st.session_state.authenticated = True
                st.session_state.username = user
                st.session_state.auth_error = None
                st.experimental_rerun()
            else:
                st.session_state.auth_error = "❌ Invalid credentials"
        else:
            if not user or not pwd:
                st.session_state.auth_error = "⚠️ Enter username & password!"
            elif user in USER_DB:
                st.session_state.auth_error = "❌ Username exists"
            else:
                USER_DB[user] = hashed
                st.session_state.auth_error = "✅ Account created! Now log in."

if not st.session_state.authenticated:
    login_ui()
    if st.session_state.auth_error:
        st.sidebar.error(st.session_state.auth_error)
    st.stop()

# --------------- USER INFO & LOGOUT ----------------
st.sidebar.write(f"✅ Logged in as **{st.session_state.username}**")
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.experimental_rerun()

# --------------- SESSION STATE ----------------
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
    pat = re.compile(r"[\U0001F600-\U0001F64F"
                     r"\U0001F300-\U0001F5FF"
                     r"\U0001F680-\U0001F6FF"
                     r"\U0001F1E0-\U0001F1FF"
                     r"\U00002700-\U000027BF"
                     r"\U000024C2-\U0001F251]+", flags=re.UNICODE)
    return pat.sub(r"", text)

# --------------- CONFIG & STYLE ----------------
st.set_page_config(page_title="AverlinMz Chatbot", layout="wide")
theme = st.sidebar.selectbox("🎨 Theme", ["Default", "Night", "Blue"])
if theme == "Night":
    st.markdown("<style>body {background:#111;color:#fff;} .user{background:#333;color:#fff;} .bot{background:#444;color:#fff;}</style>", unsafe_allow_html=True)
elif theme == "Blue":
    st.markdown("<style>body {background:#e0f7fa;} .user{background:#81d4fa;color:#01579b;} .bot{background:#b2ebf2;color:#004d40;}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
.chat-container {max-width:900px;margin:0 auto;padding:20px;display:flex;flex-direction:column;}
.title-container {text-align:center;padding-bottom:10px;font-family:'Poppins';animation:slideUpFadeIn 1s;}
.chat-window {flex-grow:1;max-height:60vh;overflow-y:auto;padding:15px;display:flex;flex-direction:column;gap:15px;}
.user, .bot {width:100%;padding:12px 16px;border-radius:18px;word-wrap:break-word;}
.user{background:#D1F2EB;color:#0B3D2E;}
.bot{background:#EFEFEF;color:#333;animation:typing 1s;}
@keyframes typing {from {opacity:0;} to {opacity:1;}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-container">
  <img src="https://i.imgur.com/mJ1X49g_d.webp" width="120" style="border-radius:20px;" />
  <h1>AverlinMz – Study Chatbot</h1>
</div>
""", unsafe_allow_html=True)

# --------------- RESPONSE DATA & LOGIC ----------------
RESPONSE_DATA = {
    "greetings": [
        "Hey! 👋 How’s your day shaping up? Ready to tackle some study questions? 📚",
        "Hello! 😊 What topic shall we explore today? 🤔",
        "Hi there! Let’s make your study session productive! 💡",
        "Hey! I’m here to help — what’s on your mind? 💬"
    ],
    "thanks": [
        "You’re welcome! Glad I could help! 😊👍",
        "Anytime! Keep shining in your studies! ✨",
        "My pleasure! Let’s keep going! 🚀",
        "Happy to assist you! 🤝"
    ],
    "farewell": [
        "Goodbye! 👋 Keep up the great work and see you soon! 🌟",
        "Take care! Don’t forget to rest too! 🌙",
        "See you later! Stay curious and motivated! 🔥",
        "Bye! Keep pushing forward! 💪"
    ],
    "how_are_you": [
        "I'm doing well, thanks! How are you feeling today? 🙂",
        "All good here! How about you? 🤗",
        "Feeling ready to help! What about you? ⚡",
        "Doing great! How’s your mood? 🌈"
    ],
    "user_feeling_good": [
        "Awesome! Keep that positive energy flowing! 🎉🌟",
        "Great to hear that! Let’s keep this momentum going! 🏃‍♀️💨",
        "Love that! Let’s channel it into some productive study time! 📖✨",
        "Fantastic! What would you like to focus on next? 🎯"
    ],
    "user_feeling_bad": [
        "I’m sorry you’re feeling down. Remember, every day is a fresh start! 💙🌅",
        "Tough days happen — if you want, I can share some tips to lift your spirits. 🌻",
        "I’m here for you. Let’s try some quick focus or relaxation techniques. 🧘‍♂️",
        "Hang in there! Let’s work through this together. 🤝"
    ],
    "love": [
        "Thanks! Your support means a lot — I’m here to help you succeed! 💖🚀",
        "I appreciate that! Let’s keep learning together! 🤓📚",
        "Sending good vibes your way! 🤗✨",
        "Grateful for you! Let’s ace those studies! 🏆"
    ],
    "exam_prep": [
        "Start early, plan well, and take short breaks. You’ve got this! 💪📅",
        "Focus on understanding concepts, not just memorizing facts. 🧠🔍",
        "Practice with past papers to build confidence. 📝✅",
        "Stay calm and trust your preparation! 🧘‍♀️💡",
        "Remember to balance study and rest for best results. ⚖️😴"
    ],
    "passed_exam": [
        "🎉 Congratulations! Your hard work paid off! 🏅",
        "Well done! Time to celebrate your success! 🎊",
        "Amazing achievement! Keep aiming higher! 🚀",
        "You did great! Ready for the next challenge? 🔥"
    ],
    "capabilities": [
        "I offer study tips, answer questions, track your goals, and keep you motivated! 💡📈",
        "I’m here to support your learning with advice, encouragement, and goal tracking. 🤖✨",
        "Ask me about subjects, study strategies, or just chat! 💬📚",
        "Think of me as your personal study assistant. 🧑‍💻🤓"
    ],
    "introduction": [
        "I’m AverlinMz, your study chatbot, created by Aylin Muzaffarli from Azerbaijan. 🇦🇿🤖 Learn more: <a href='https://aylinmuzaffarli.github.io/averlinmz-site/' target='_blank'>official website</a> 🌐",
        "Hello! I’m here to support your study journey. 🎓✨ Visit my site: <a href='https://aylinmuzaffarli.github.io/averlinmz-site/' target='_blank'>AverlinMz Website</a> 💻",
        "Created by Aylin, I help with study tips and motivation. 💡❤️ Check this out: <a href='https://aylinmuzaffarli.github.io/averlinmz-site/' target='_blank'>Learn more</a> 📖",
        "Nice to meet you! Let’s learn and grow together. 🌱📘 Want to know more? <a href='https://aylinmuzaffarli.github.io/averlinmz-site/' target='_blank'>Click here</a> 🚀"
    ],
    "creator_info": [
        "Created by Aylin — passionate about science, tech, and helping others learn. 🔬💻",
        "Aylin’s dedication makes this chatbot your study buddy. 🎯✨",
        "Behind me is Aylin, focused on inspiring learners like you. 💡🌟",
        "Aylin designed me to help students reach their goals. 🚀📚"
    ],
    "ack_creator": [
        "All credit goes to Aylin Muzaffarli! 🌟🙌",
        "Proudly created by Aylin — thanks for noticing! 💙🎉",
        "A big shoutout to Aylin for this chatbot! 🎊🤖",
        "Aylin’s hard work made this possible. 👏🚀"
    ],
    "contact_creator": [
        "You can contact Aylin by filling out this <a href='https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit' target='_blank'>Google Form</a> 📋✨",
        "Reach out to Aylin anytime via this <a href='https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit' target='_blank'>Google Form</a> 📨🌟",
        "Feel free to send your feedback or questions through this <a href='https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit' target='_blank'>Google Form</a> 💬😊",
        "Aylin welcomes your messages! Use this <a href='https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit' target='_blank'>Google Form</a> 📬🤗"
    ],

    "subjects": {
        "math": "🧮 Math Tips: Practice regularly, focus on concepts, and solve diverse problems. 🔢📝",
        "physics": "🧪 Physics Tips: Understand fundamentals, draw diagrams, and apply formulas in problems. ⚛️📊",
        # add more subjects here if you want
    },
    "fallback": [
        "I’m not sure I understood that — could you try rephrasing? 🤔😊",
        "Sorry, I didn’t catch that. Want to try again? 🔄",
        "I’m learning every day! Could you ask differently? 📚✨",
        "That’s new to me! Care to explain? 🤖❓",
        "Oops, I didn’t get that. Let’s try another question! 💬"
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "hiya", "greetings"],
    "farewell": ["goodbye", "bye", "see you", "farewell", "later", "take care"],
    "how_are_you": ["how are you", "how's it going", "how do you do"],
    "user_feeling_good": ["i'm good", "great", "happy", "doing well", "awesome", "fine"],
    "user_feeling_bad": ["i'm sad", "not good", "tired", "depressed", "down", "exhausted"],
    "love": ["i love you", "love you", "luv you", "like you"],
    "exam_prep": ["exam tips", "study for test", "prepare for exam", "how to study", "exam advice", "test preparation"],
    "passed_exam": ["i passed", "i did it", "exam success", "cleared the test", "exam results"],
    "capabilities": ["what can you do", "your abilities", "features", "help me"],
    "introduction": ["introduce", "who are you", "about you", "yourself", "tell me about yourself"],
    "creator_info": ["who is aylin", "about aylin", "creator info", "who made you"],
    "contact_creator": ["how can i contact aylin", "contact aylin", "how to contact", "reach aylin"],
    "ack_creator": ["thank aylin", "thanks aylin", "thank you aylin", "appreciate aylin"],
    "thanks": ["thank you", "thanks", "thx", "ty"],
    "subjects": ["math", "physics"]
}

def clean_keyword_list(kws):
    return {intent: [p.lower().translate(str.maketrans("", "", string.punctuation)).strip() for p in phrases] for intent, phrases in kws.items()}
KEYWORDS_CLEANED = clean_keyword_list(KEYWORDS)

def clean_text(t): 
    return t.lower().translate(str.maketrans("", "", string.punctuation)).strip()

def detect_intent(text):
    msg = clean_text(text)
    for intent, kws in KEYWORDS_CLEANED.items():
        if any(kw in msg for kw in kws):
            return intent
    return None

def update_goals(inp):
    m = clean_text(inp)
    if any(w in m for w in ["goal", "aim", "plan"]):
        if inp not in st.session_state.goals:
            st.session_state.goals.append(inp)
            return "Got it! I've added that to your study goals."
        else:
            return "You already mentioned this goal."
    return None

def detect_sentiment(txt):
    pos = ["good", "great", "awesome", "love", "happy", "fine", "well"]
    neg = ["bad", "sad", "tired", "depressed", "down", "exhausted"]
    t = clean_text(txt)
    if any(w in t for w in pos): 
        return "positive"
    if any(w in t for w in neg): 
        return "negative"
    return "neutral"

def get_bot_reply(inp):
    intent = detect_intent(inp)
    gmsg = update_goals(inp)
    if gmsg:
        return gmsg
    sen = detect_sentiment(inp)
    st.session_state.last_sentiment = sen
    if intent and intent in RESPONSE_DATA:
        if intent == "subjects":
            for s in KEYWORDS["subjects"]:
                if s in inp.lower():
                    st.session_state.context_topic = s
                    break
            return RESPONSE_DATA["subjects"].get(st.session_state.context_topic, random.choice(RESPONSE_DATA["fallback"]))
        st.session_state.context_topic = None
        return random.choice(RESPONSE_DATA[intent])
    if st.session_state.context_topic:
        return RESPONSE_DATA["subjects"].get(st.session_state.context_topic, random.choice(RESPONSE_DATA["fallback"])) + "\n\n(You asked about this before!)"
    if sen == "positive":
        return "Glad you're feeling good! 🎉"
    if sen == "negative":
        return "I’m here to help if you need me. 💙"
    return random.choice(RESPONSE_DATA["fallback"])

def play_tts(text):
    clean = remove_emojis(text)
    tts = gTTS(clean, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        data = open(f.name, "rb").read()
    st.audio(data)
    os.unlink(f.name)

# --------------- CHAT UI ----------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Write your message…", key="input_field")
    submitted = st.form_submit_button("Send")
    if submitted:
        if user_input.strip():
            st.session_state.messages.append({"role":"user","content":user_input})
            resp = get_bot_reply(user_input)
            st.session_state.messages.append({"role":"bot","content":resp})
            play_tts(resp)

st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    cls = "user" if msg["role"]=="user" else "bot"
    st.markdown(f'<div class="{cls}">{escape(msg["content"]).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# --------------- SIDEBAR & HISTORY ----------------
with st.sidebar:
    st.markdown("### 🎯 Your Goals")
    if st.session_state.goals:
        for g in st.session_state.goals:
            st.write(f"- {g}")
    else:
        st.write("No goals yet. Add one by typing it in chat!")

    st.markdown("### 💡 Example Prompts")
    st.info("\n".join([
        "- Give me study tips",
        "- Tell me about physics",
        "- How do I manage time?",
        "- Or just say 'bye' to end the chat!"
    ]))

# Download history
fn = f"chat_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"
hist = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
st.download_button("📥 Download Chat History", hist, file_name=fn)
