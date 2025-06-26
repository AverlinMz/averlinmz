import streamlit as st
import random
import string
from html import escape
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
        "I’m AverlinMz, your study chatbot, created by Aylin Muzaffarli from Azerbaijan. 🇦🇿🤖",
        "Hello! I’m here to support your study journey. 🎓✨",
        "Created by Aylin, I help with study tips and motivation. 💡❤️",
        "Nice to meet you! Let’s learn and grow together. 🌱📘"
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
    "You can contact Aylin by filling out this [Google Form](https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit) 📋✨",
    "Reach out to Aylin anytime via this [Google Form](https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit) 📨🌟",
    "Feel free to send your feedback or questions through this [Google Form](https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit) 💬😊",
    "Aylin welcomes your messages! Use this [Google Form](https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit) 📬🤗"
],

    "subjects": {
        "math": "🧮 Math Tips: Practice regularly, focus on concepts, and solve diverse problems. 🔢📝",
        "physics": "🧪 Physics Tips: Understand fundamentals, draw diagrams, and apply formulas in problems. ⚛️📊",
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
    return None

def update_goals(user_input):
    msg = clean_text(user_input)
    if "goal" in msg or "aim" in msg or "plan" in msg:
        if user_input not in st.session_state.goals:
            st.session_state.goals.append(user_input)
            return "Got it! I've added that to your study goals."
        else:
            return "You already mentioned this goal."
    return None

def detect_sentiment(text):
    positive = ["good", "great", "awesome", "love", "happy", "fine", "well"]
    negative = ["bad", "sad", "tired", "depressed", "down", "exhausted"]
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
            # detect specific subject mentioned
            for subj in KEYWORDS["subjects"]:
                if subj in user_input.lower():
                    st.session_state.context_topic = subj
                    break
            return RESPONSE_DATA["subjects"].get(st.session_state.context_topic, random.choice(RESPONSE_DATA["fallback"]))
        else:
            st.session_state.context_topic = None
            return random.choice(RESPONSE_DATA[intent])

    if st.session_state.context_topic:
        subj = st.session_state.context_topic
        return RESPONSE_DATA["subjects"].get(subj, random.choice(RESPONSE_DATA["fallback"])) + "\n\n(You asked about this before!)"

    if sentiment == "positive":
        return "Glad to hear you’re feeling good! Keep it up! 🎉"
    elif sentiment == "negative":
        return "I noticed you’re feeling down. If you want, I can share some tips or just listen. 💙"

    return random.choice(RESPONSE_DATA["fallback"])

with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        bot_reply = get_bot_reply(user_input)
        st.session_state.messages.append({'role': 'bot', 'content': bot_reply})
        
        # Remove emojis before TTS so audio is clean
        clean_reply = remove_emojis(bot_reply)
        tts = gTTS(clean_reply, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tts_file:
            tts.save(tts_file.name)
            audio_bytes = open(tts_file.name, "rb").read()
        st.audio(audio_bytes, format="audio/mp3")
        os.unlink(tts_file.name)

st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
msgs = st.session_state.messages
# Display chat messages in reverse chronological order (newest at bottom)
for i in range(len(msgs) - 2, -1, -2):
    user_msg = msgs[i]['content']
    bot_msg = msgs[i+1]['content'] if i+1 < len(msgs) else ''
    st.markdown(f'<div class="user">{escape(user_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot">{escape(bot_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎯 Your Goals")
    if st.session_state.goals:
        for g in st.session_state.goals:
            st.write("- " + g)
    else:
        st.write("You haven't set any goals yet. Tell me your goals!")

    st.markdown("### 💡 Tips")
    st.info("Try asking things like:\n- 'Give me study tips'\n- 'Tell me about physics'\n- 'How do I manage time?'\n- Or just say 'bye' to end the chat!")

    st.markdown("### 🧠 Mini AI Assistant Mode")
    st.write("This bot tries to detect your intent and give focused advice or answers.")

filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
chat_history_text = "\n".join([f"{m['role'].upper()}: {m['content']}\n" for m in st.session_state.messages])
st.download_button("📥 Download Chat History", chat_history_text, file_name=filename)
