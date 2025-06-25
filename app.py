import streamlit as st
import random
import string
from html import escape
import datetime
import re
import io
import base64

from gtts import gTTS

from streamlit_webrtc import webrtc_streamer
import av
import speech_recognition as sr

# -------- Initialize session state --------
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "goals" not in st.session_state:
        st.session_state.goals = []
    if "context_topic" not in st.session_state:
        st.session_state.context_topic = None
    if "recognized_text" not in st.session_state:
        st.session_state.recognized_text = ""
init_session()

# -------- Remove emojis for TTS --------
def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# -------- Text to Speech (TTS) --------
def tts_audio(text):
    text_clean = remove_emojis(text)
    tts = gTTS(text=text_clean, lang='en')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

def play_audio(audio_bytes):
    audio_bytes.seek(0)
    audio_b64 = base64.b64encode(audio_bytes.read()).decode()
    audio_html = f"""
    <audio autoplay controls>
    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    Your browser does not support the audio element.
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# -------- Data --------
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
    "contact_creator": [
        "You can contact my creator on GitHub: https://github.com/AverlinMz 📬",
        "Want to talk to Aylin? Try reaching out via GitHub – she's awesome! 🌟"
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
        "geography": "🌍 Geography Tips:\n1️⃣ Learn maps and locations frequently.\n2️⃣ Understand climate and environment basics.\n3️⃣ Use visuals like atlases and diagrams.\n4️⃣ Relate geography to current events.\n5️⃣ Practice with quizzes and flashcards."
    },
    "fallback": [
        "Hmm, I’m not sure how to answer that — but I’ll learn! Maybe ask about a subject or how you feel. 🤔",
        "I didn’t quite get that, but I’m still here for you. 😊 Try rephrasing or check the help tips."
    ]
}

# Keywords for intent detection
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
    "contact_creator": ["how to contact", "reach aylin", "contact you", "talk to aylin", "how can i contact to aylin"],
    "ack_creator": ["aylin is cool", "thank aylin", "credit to aylin"],
    "subjects": ["math", "physics", "chemistry", "biology", "english", "robotics", "ai", "geography"]
}

# -------- Clean and normalize input text --------
def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

# -------- Detect intent --------
def detect_intent(text):
    msg = clean_text(text)
    for intent, kws in KEYWORDS.items():
        if any(kw in msg for kw in kws):
            return intent
    return None

# -------- Update goals --------
def update_goals(user_input):
    msg = clean_text(user_input)
    if "goal" in msg or "aim" in msg or "plan" in msg:
        if user_input not in st.session_state.goals:
            st.session_state.goals.append(user_input)
            return "Got it! I added that to your goals."
        else:
            return "You already mentioned this goal."
    return None

# -------- Detect simple sentiment --------
def detect_sentiment(text):
    positive = ["good", "great", "awesome", "love", "happy", "well", "fine"]
    negative = ["bad", "sad", "tired", "depressed", "angry", "upset", "not good"]
    txt = clean_text(text)
    if any(word in txt for word in positive):
        return "positive"
    if any(word in txt for word in negative):
        return "negative"
    return "neutral"

# -------- Bot reply logic --------
def get_bot_reply(user_input):
    intent = detect_intent(user_input)
    goal_msg = update_goals(user_input)

    if goal_msg:
        return goal_msg

    if intent and intent in RESPONSE_DATA:
        reply = random.choice(RESPONSE_DATA[intent])
        # Save context topic if subject
        if intent == "subjects":
            for subj in KEYWORDS["subjects"]:
                if subj in user_input.lower():
                    st.session_state.context_topic = subj
                    break
        else:
            st.session_state.context_topic = None
        return reply

    # Use context topic if no direct intent match
    if st.session_state.context_topic:
        subj = st.session_state.context_topic
        if subj in RESPONSE_DATA["subjects"]:
            return RESPONSE_DATA["subjects"][subj] + "\n\n(You asked about this before!)"

    sentiment = detect_sentiment(user_input)
    if sentiment == "positive":
        return "I'm glad you're feeling good! Keep it up! 🎉"
    elif sentiment == "negative":
        return "I'm sorry you're feeling that way. I'm here if you want to talk. 💙"

    return random.choice(RESPONSE_DATA["fallback"])

# -------- UI --------
st.title("AverlinMz – Study Chatbot")

# Sidebar voice input toggle
voice_input = st.sidebar.checkbox("🎤 Enable Voice Input")

# Voice input processing with streamlit-webrtc
if voice_input:
    recognizer = sr.Recognizer()

    def audio_frame_callback(frame: av.AudioFrame):
        audio = frame.to_ndarray(format="s16", layout="mono")
        audio_data = sr.AudioData(audio.tobytes(), 16000, 2)
        try:
            text = recognizer.recognize_google(audio_data, language="en-US")
            st.session_state.recognized_text = text
        except sr.UnknownValueError:
            pass
        except Exception:
            pass
        return frame

    webrtc_streamer(key="speech-input", audio_frame_callback=audio_frame_callback)

    if st.session_state.recognized_text:
        st.text_area("Recognized Speech Text:", st.session_state.recognized_text, height=100)
        if st.button("Send Voice Input"):
            user_input = st.session_state.recognized_text
            st.session_state.messages.append({'role': 'user', 'content': user_input})
            bot_reply = get_bot_reply(user_input)
            st.session_state.messages.append({'role': 'bot', 'content': bot_reply})
            st.session_state.recognized_text = ""

else:
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Write your message…", key="input_text")
        if st.form_submit_button("Send") and user_input.strip():
            st.session_state.messages.append({'role': 'user', 'content': user_input})
            bot_reply = get_bot_reply(user_input)
            st.session_state.messages.append({'role': 'bot', 'content': bot_reply})

# Show chat messages with read aloud button for bots only
for i, msg in enumerate(st.session_state.messages):
    role = msg['role']
    content = msg['content']
    if role == 'user':
        st.markdown(f"**You:** {escape(content)}")
    else:
        st.markdown(f"**Bot:** {escape(content)}")
        # Read aloud button
        if st.button(f"🔊 Read aloud (message #{i})", key=f"tts_button_{i}"):
            audio_fp = tts_audio(content)
            play_audio(audio_fp)

# Show goals
if st.session_state.goals:
    st.markdown("### Your Goals:")
    for g in st.session_state.goals:
        st.write(f"- {g}")

# Download chat history
def get_chat_history_text():
    lines = []
    for m in st.session_state.messages:
        lines.append(f"{m['role'].upper()}: {m['content']}")
    return "\n".join(lines)

filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
st.download_button(
    label="💾 Download Chat History",
    data=get_chat_history_text(),
    file_name=filename,
    mime="text/plain"
)
