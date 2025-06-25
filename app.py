import streamlit as st
import string
import random
from html import escape
import datetime
import re
import tempfile
import os
from gtts import gTTS
import requests

# --- Initialize session state ---
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "goals" not in st.session_state:
        st.session_state.goals = []
    if "context_topic" not in st.session_state:
        st.session_state.context_topic = None
init_session()

# --- Helper to remove emojis from TTS input ---
def remove_emojis(text):
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F"
                               "\U0001F300-\U0001F5FF"
                               "\U0001F680-\U0001F6FF"
                               "\U0001F1E0-\U0001F1FF"
                               "\U00002700-\U000027BF"
                               "\U000024C2-\U0001F251]+",
                               flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# --- Responses and keywords ---
RESPONSE_DATA = {
    "greetings": [
        "Hello there! 👋 How’s your day going? Ready to dive into learning today?",
        "Hey hey! 🌟 Hope you’re feeling inspired today. What’s on your mind?",
        "Hi friend! 😊 I’m here for you — whether you want to study, vent, or just chat."
    ],
    "farewell": [
        "Goodbye! 👋 Come back soon for more study tips!",
        "See you later! Keep up the great work! 📘",
        "Bye for now! You’ve got this! 💪",
        "Take care! Don’t forget to smile and stay curious! 😊",
        "Catch you next time! Keep learning and dreaming big! ✨"
    ],
    "how_are_you": [
        "I'm doing well, thanks for asking! 💬 How are you feeling today?",
        "Feeling smart and helpful — as always! 😊 How can I assist you today?"
    ],
    "user_feeling_good": [
        "That’s amazing to hear! 🎉 Keep riding that good energy!",
        "Awesome! Let’s keep the momentum going! 💪"
    ],
    "contact_creator": [
        "You can contact my creator on GitHub: https://github.com/AverlinMz 📬",
        "Want to talk to Aylin? Try reaching out via GitHub – she's awesome! 🌟",
    ],
    "user_feeling_bad": [
        "Sorry to hear that. I’m always here if you want to talk or need a study boost. 💙🌟",
        "It’s okay to feel this way. Just remember you’re not alone. I'm here with you. 🤗"
    ],
    "exam_prep": [
        "1️⃣ Start early and create a study plan.\n2️⃣ Break subjects into small topics.\n3️⃣ Use spaced repetition.\n4️⃣ Teach someone else to reinforce concepts.\n5️⃣ Rest well and stay hydrated. 📘💧",
        "Plan 📝 → Study 📚 → Practice 🧠 → Revise 🔁 → Sleep 😴. That's a golden strategy!"
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
        "I'm AverlinMz, your study chatbot 🌱. My creator is Aylin Muzaffarli (b.2011, Azerbaijan). She loves music, programming, robotics, AI, physics, and more."
    ],
    "creator_info": [
        "I was created by Aylin Muzaffarli — a passionate student from Azerbaijan who codes, studies physics and AI, and inspires others! 💡",
        "My developer is Aylin Muzaffarli, born in 2011. She built me to support learners like you!"
    ],
    "ack_creator": [
        "Yes, Aylin is super talented! 😄",
        "Absolutely! All credit goes to Aylin Muzaffarli! 🌟"
    ],
    "subjects": {
        "math": "🧮 Math Tips:\n1️⃣ Practice daily — it's the key to mastery.\n2️⃣ Understand concepts, don't just memorize.\n3️⃣ Use visuals like graphs and number lines.\n4️⃣ Solve real-world problems.\n5️⃣ Review your mistakes and learn from them.",
        "physics": "🧪 Physics Tips:\n1️⃣ Master the basics: units, vectors, motion.\n2️⃣ Solve numerical problems to strengthen concepts.\n3️⃣ Create diagrams to visualize problems.\n4️⃣ Memorize core formulas.\n5️⃣ Watch experiments online to connect theory with practice.",
        "chemistry": "🧫 Chemistry Tips:\n1️⃣ Know your periodic table well.\n2️⃣ Understand how and why reactions happen.\n3️⃣ Use flashcards for equations and compounds.\n4️⃣ Practice balancing equations.\n5️⃣ Watch reaction videos to make it fun!",
        "biology": "🧬 Biology Tips:\n1️⃣ Learn through diagrams (cells, organs, systems).\n2️⃣ Connect terms with real-life examples.\n3️⃣ Summarize topics using mind maps.\n4️⃣ Quiz yourself with apps.\n5️⃣ Talk about biology topics out loud.",
        "english": "📚 Language Tips:\n1️⃣ Read a bit every day (books, articles, stories).\n2️⃣ Speak or write in English regularly.\n3️⃣ Learn 5 new words daily and use them.\n4️⃣ Practice grammar through fun apps.\n5️⃣ Watch English shows with subtitles!",
        "robotics": "🤖 Robotics Tips:\n1️⃣ Start with block coding (like Scratch).\n2️⃣ Move on to Arduino and sensors.\n3️⃣ Join a club or competition.\n4️⃣ Watch tutorials and build projects.\n5️⃣ Learn how to debug and fix errors. Patience is key!",
        "ai": "🧠 AI Tips:\n1️⃣ Start with Python basics.\n2️⃣ Learn about data types and logic.\n3️⃣ Try building chatbots or mini classifiers.\n4️⃣ Study math behind AI: linear algebra, probability.\n5️⃣ Follow real AI projects online to stay inspired!",
        "geography": "🌍 Geography Tips:\n1️⃣ Study maps regularly.\n2️⃣ Understand physical features and climates.\n3️⃣ Connect human activities with locations.\n4️⃣ Practice with past exam questions.\n5️⃣ Use videos and documentaries for better retention."
    },
    "fallback": [
        "Hmm, I’m not sure how to answer that — but I’ll learn! Maybe ask about a subject or how you feel. 🤔",
        "I didn’t quite get that, but I’m still here for you. 😊 Try rephrasing or check the help tips."
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "salam"],
    "farewell": ["goodbye", "bye", "see you", "talk later", "see ya", "later"],
    "how_are_you": ["how are you", "how's it going", "how do you feel"],
    "user_feeling_good": ["i'm fine", "i'm good", "great", "happy", "excellent"],
    "user_feeling_bad": ["i'm sad", "not good", "tired", "depressed", "bad", "feeling sad", "i'm feeling sad", "i feel bad"],
    "love": ["i love you", "you are cute", "like you"],
    "exam_prep": ["exam tips", "how to prepare", "study for test", "exam help", "give me advice for exam prep", "tips for exam"],
    "passed_exam": ["i passed", "got good mark", "i won"],
    "capabilities": ["what can you do", "your functions", "features"],
    "introduction": ["introduce", "who are you", "your name", "about you", "creator", "who made you", "introduce yourself"],
    "creator_info": ["who is aylin", "who made you", "your developer", "tell me about aylin"],
    "contact_creator": ["how to contact", "reach aylin", "contact you", "talk to aylin", "how can i contact to aylin", "how to reach out to aylin", "how to reach out to her"],
    "ack_creator": ["aylin is cool", "thank aylin", "credit to aylin"],
    "subjects": ["math", "physics", "chemistry", "biology", "english", "robotics", "ai", "geography"]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def detect_intent(text):
    msg = clean_text(text)
    for intent, kws in KEYWORDS.items():
        if any(kw in msg for kw in kws):
            return intent
    return None

def update_goals(user_input):
    msg = clean_text(user_input)
    if "goal" in msg or "aim" in msg or "plan" in msg:
        if user_input not in st.session_state.goals:
            st.session_state.goals.append(user_input)
            return "Got it! I added that to your goals."
        else:
            return "You already mentioned this goal."
    return None

def get_bot_reply(user_input):
    goal_msg = update_goals(user_input)
    if goal_msg:
        return goal_msg

    intent = detect_intent(user_input)

    if intent and intent in RESPONSE_DATA:
        if intent == "subjects":
            for subj in KEYWORDS["subjects"]:
                if subj in user_input.lower():
                    st.session_state.context_topic = subj
                    return RESPONSE_DATA["subjects"][subj]
            return "Which subject do you want tips on? For example, math, physics, chemistry..."
        else:
            return random.choice(RESPONSE_DATA[intent])

    return RESPONSE_DATA["fallback"][0]

# --- Page config ---
st.set_page_config(page_title="AverlinMz Chatbot", page_icon="💡", layout="wide", initial_sidebar_state="collapsed")

# --- Theme selector ---
theme = st.sidebar.selectbox("🎨 Choose a theme", ["Default", "Night", "Blue"])
if theme == "Night":
    st.markdown("""<style>body, .stApp { background:#111; color:#fff; } .user {background:#333;color:#fff;} .bot {background:#444;color:#fff;}</style>""", unsafe_allow_html=True)
elif theme == "Blue":
    st.markdown("""<style>body, .stApp { background:#e0f7fa; } .user {background:#81d4fa;color:#01579b;} .bot {background:#b2ebf2;color:#004d40;}</style>""", unsafe_allow_html=True)

# --- Styling ---
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

# --- Title ---
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

# --- API Setup ---
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"
API_TOKEN = st.secrets["hf_api_token"]
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def query_hf_api(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 150, "temperature": 0.7, "top_p": 0.9},
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            return "Sorry, I couldn't generate a response right now."
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        else:
            return "Sorry, I didn't understand that."
    except Exception as e:
        return f"Error contacting AI API: {str(e)}"

# --- Main UI ---
with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})

        # Use keyword-based bot reply first:
        bot_reply = get_bot_reply(user_input)

        # You can choose to also get AI model reply (comment/uncomment below):
        ai_reply = query_hf_api(user_input)
        bot_reply = ai_reply if ai_reply else bot_reply

        st.session_state.messages.append({'role': 'bot', 'content': bot_reply})

# --- Display chat messages ---
for msg in st.session_state.messages:
    role = msg['role']
    content = escape(msg['content']).replace('\n', '<br>')
    if role == 'user':
        st.markdown(f'<div class="user">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{content}</div>', unsafe_allow_html=True)

# --- TTS (optional) ---
if st.session_state.messages:
    last_msg = st.session_state.messages[-1]
    if last_msg['role'] == 'bot':
        if st.button("🔊 Listen to reply"):
            text_to_speak = remove_emojis(last_msg['content'])
            tts = gTTS(text=text_to_speak, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                tts.save(tmpfile.name)
                audio_bytes = open(tmpfile.name, 'rb').read()
            st.audio(audio_bytes, format='audio/mp3')
            os.unlink(tmpfile.name)
