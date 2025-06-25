import streamlit as st
import random
import string
import datetime
import re
import io
import base64
from html import escape
from gtts import gTTS
from pydub import AudioSegment

# Initialize session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "goals" not in st.session_state:
        st.session_state.goals = []
    if "context_topic" not in st.session_state:
        st.session_state.context_topic = None
init_session()

# Remove emojis helper
def remove_emojis(text):
    emoji_pattern = re.compile("["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# Text-to-speech -> audio bytes
def tts_audio(text):
    clean = remove_emojis(text)
    tts = gTTS(clean, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# Play audio in Streamlit
def play_audio(fp):
    data = fp.read()
    b64 = base64.b64encode(data).decode()
    st.markdown(f"""
    <audio autoplay controls>
      <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)

# Page and theme
theme = st.sidebar.selectbox("Theme", ["Default","Night","Blue"])
if theme=="Night": st.markdown("<style>body{background:#111;color:#eee;}.user{background:#333;color:#fff;}.bot{background:#444;color:#fff;}</style>",unsafe_allow_html=True)
elif theme=="Blue": st.markdown("<style>body{background:#e0f7fa}.user{background:#81d4fa;color:#01579b}.bot{background:#b2ebf2;color:#004d40}</style>",unsafe_allow_html=True)

st.set_page_config(page_title="AverlinMz Chatbot",layout="wide")
st.markdown("# AverlinMz – Study Chatbot")

# Data
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
    "user_feeling_bad": [
        "Sorry to hear that. I’m always here if you want to talk or need a study boost. 💙🌟",
        "It’s okay to feel this way. Just remember you’re not alone. I'm here with you. 🤗"
    ],
    "exam_prep": [
        "1️⃣ Start early and create a study plan.
2️⃣ Break subjects into small topics.
3️⃣ Use spaced repetition.
4️⃣ Teach someone else to reinforce concepts.
5️⃣ Rest well and stay hydrated. 📘💧",
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
    "contact_creator": [
        "You can contact my creator on GitHub: https://github.com/AverlinMz 📬",
        "Want to talk to Aylin? Try reaching out via GitHub – she's awesome! 🌟"
    ],
    "ack_creator": [
        "Yes, Aylin is super talented! 😄",
        "Absolutely! All credit goes to Aylin Muzaffarli! 🌟"
    ],
    "subjects": {
        "math": "🧮 Math Tips:
1️⃣ Practice daily — it's the key to mastery.
2️⃣ Understand concepts, don't just memorize.
3️⃣ Use visuals like graphs and number lines.
4️⃣ Solve real-world problems.
5️⃣ Review your mistakes and learn from them.",
        "physics": "🧪 Physics Tips:
1️⃣ Master the basics: units, vectors, motion.
2️⃣ Solve numerical problems to strengthen concepts.
3️⃣ Create diagrams to visualize problems.
4️⃣ Memorize core formulas.
5️⃣ Watch experiments online to connect theory with practice.",
        "chemistry": "🧫 Chemistry Tips:
1️⃣ Know your periodic table well.
2️⃣ Understand how and why reactions happen.
3️⃣ Use flashcards for equations and compounds.
4️⃣ Practice balancing equations.
5️⃣ Watch reaction videos to make it fun!",
        "biology": "🧬 Biology Tips:
1️⃣ Learn through diagrams (cells, organs, systems).
2️⃣ Connect terms with real-life examples.
3️⃣ Summarize topics using mind maps.
4️⃣ Quiz yourself with apps.
5️⃣ Talk about biology topics out loud.",
        "english": "📚 Language Tips:
1️⃣ Read a bit every day (books, articles, stories).
2️⃣ Speak or write in English regularly.
3️⃣ Learn 5 new words daily and use them.
4️⃣ Practice grammar through fun apps.
5️⃣ Watch English shows with subtitles!",
        "robotics": "🤖 Robotics Tips:
1️⃣ Start with block coding (like Scratch).
2️⃣ Move on to Arduino and sensors.
3️⃣ Join a club or competition.
4️⃣ Watch tutorials and build projects.
5️⃣ Learn how to debug and fix errors. Patience is key!",
        "ai": "🧠 AI Tips:
1️⃣ Start with Python basics.
2️⃣ Learn about data types and logic.
3️⃣ Try building chatbots or mini classifiers.
4️⃣ Study math behind AI: linear algebra, probability.
5️⃣ Follow real AI projects online to stay inspired!",
        "geography": "🌍 Geography Tips:
1️⃣ Learn maps and locations frequently.
2️⃣ Understand climate and environment basics.
3️⃣ Use visuals like atlases and diagrams.
4️⃣ Relate geography to current events.
5️⃣ Practice with quizzes and flashcards."
    },
    "fallback": [
        "Hmm, I’m not sure how to answer that — but I’ll learn! Maybe ask about a subject or how you feel. 🤔",
        "I didn’t quite get that, but I’m still here for you. 😊 Try rephrasing or check the help tips."
    ]
}
KEYWORDS={ ... }

# Helpers
def clean_text(text): return text.lower().translate(str.maketrans('','',string.punctuation)).strip()
def detect_intent(text):
    msg=clean_text(text)
    for intent,kws in KEYWORDS.items():
        if any(kw in msg for kw in kws): return intent
    return None

def update_goals(user_input):
    msg=clean_text(user_input)
    if any(w in msg for w in ["goal","aim","plan"]):
        if user_input not in st.session_state.goals:
            st.session_state.goals.append(user_input); return "Added to goals!"
        else: return "Goal exists."
    return None

def detect_sentiment(text):
    pos=["good","great","awesome","happy","fine"]
    neg=["sad","bad","tired","depressed"]
    t=clean_text(text)
    if any(w in t for w in pos): return "positive"
    if any(w in t for w in neg): return "negative"
    return "neutral"

def get_bot_reply(user_input):
    if (gm:=update_goals(user_input)): return gm
    intent=detect_intent(user_input)
    if intent in RESPONSE_DATA: reply=random.choice(RESPONSE_DATA[intent]);
    elif st.session_state.context_topic:
        reply=RESPONSE_DATA['subjects'].get(st.session_state.context_topic,random.choice(RESPONSE_DATA['fallback']))+"\n(continued...)"
    else: reply=random.choice(RESPONSE_DATA['fallback'])
    # track context
    if intent=='subjects':
        for sub in KEYWORDS['subjects']:
            if sub in user_input.lower(): st.session_state.context_topic=sub; break
    return reply

# Audio input via upload
st.sidebar.markdown("### Audio Input (upload .wav/.mp3)")
audio_file=st.sidebar.file_uploader("Upload audio",type=["wav","mp3"])
if audio_file:
    import speech_recognition as sr
    r=sr.Recognizer()
    with sr.AudioFile(audio_file) as src:
        data=r.record(src)
        try: txt=r.recognize_google(data); st.sidebar.success(f"You said: {txt}")
        except: txt=None
    if txt:
        st.session_state.messages.append({'role':'user','content':txt})
        bot=get_bot_reply(txt); st.session_state.messages.append({'role':'bot','content':bot})

# Chat form
with st.form('cf',clear_on_submit=True):
    ui=st.text_input('Your message')
    if st.form_submit_button('Send') and ui:
        st.session_state.messages.append({'role':'user','content':ui})
        bot=get_bot_reply(ui)
        st.session_state.messages.append({'role':'bot','content':bot})

# Display chat
for i,m in enumerate(st.session_state.messages):
    if m['role']=='user': st.markdown(f"**You:** {escape(m['content'])}")
    else:
        st.markdown(f"**Bot:** {escape(m['content'])}")
        if st.button(f"🔊 Read aloud #{i}",key=i):
            fp=tts_audio(m['content']); play_audio(fp)

# Goals
if st.session_state.goals:
    st.markdown("### Goals:")
    for g in st.session_state.goals: st.write(f"- {g}")

# Download history
def hist(): return '\n'.join(f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages)
st.download_button("Download Chat",data=hist(),file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Note: Replace RESPONSE_DATA and KEYWORDS placeholders with full dicts from above.
