import streamlit as st
import random
import string
import os
from html import escape
import datetime

# ✅ NEW: Local GPT-2 support
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# Load GPT-2 once
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Initialize session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "goals" not in st.session_state:
        st.session_state.goals = []
    if "context_topic" not in st.session_state:
        st.session_state.context_topic = None
init_session()

# Page config
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Theme Customizer
theme = st.sidebar.selectbox("🎨 Choose a theme", ["Default", "Night", "Blue"])
if theme == "Night":
    st.markdown("""
    <style>
    body, .stApp { background-color: #111111; color: white; }
    .user { background-color: #333333; color: white; }
    .bot { background-color: #444444; color: white; }
    </style>
    """, unsafe_allow_html=True)
elif theme == "Blue":
    st.markdown("""
    <style>
    body, .stApp { background-color: #e0f7fa; }
    .user { background-color: #81d4fa; color: #01579b; }
    .bot { background-color: #b2ebf2; color: #004d40; }
    </style>
    """, unsafe_allow_html=True)

# CSS Styling
st.markdown("""
<style>
.chat-container { display: flex; flex-direction: column; max-width: 900px; margin: 0 auto; padding: 20px; }
.title-container { text-align: center; padding-bottom: 10px; font-family: 'Poppins', sans-serif; font-weight: 600; animation: fadeInUp 1s ease forwards; opacity: 0; }
.title-container h1 { margin: 0; }
.chat-window { flex-grow: 1; overflow-y: auto; max-height: 60vh; padding: 15px; display: flex; flex-direction: column; gap: 15px; }
.user, .bot { align-self: center; width: 100%; word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-family: 'Poppins', sans-serif; }
.user { background-color: #D1F2EB; color: #0B3D2E; padding: 12px 16px; border-radius: 18px 18px 4px 18px; }
.bot  { background-color: #EFEFEF; color: #333; padding: 12px 16px; border-radius: 18px 18px 18px 4px; animation: typing 1s ease-in-out; }
.chat-window::-webkit-scrollbar { width: 8px; }
.chat-window::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb:hover { background: #a1a1a1; }
@keyframes typing { 0% { opacity: 0; } 100% { opacity: 1; } }
@keyframes fadeInUp {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

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
    "contact_creator": ["how to contact", "reach aylin", "contact you", "talk to aylin", "how can i contact to aylin"],
    "ack_creator": ["aylin is cool", "thank aylin", "credit to aylin"],
    "subjects": ["math", "physics", "chemistry", "biology", "english", "robotics", "ai"]
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

def detect_sentiment(text):
    positive = ["good", "great", "awesome", "love", "happy", "well", "fine"]
    negative = ["bad", "sad", "tired", "depressed", "angry", "upset", "not good"]
    txt = clean_text(text)
    if any(word in txt for word in positive):
        return "positive"
    if any(word in txt for word in negative):
        return "negative"
    return "neutral"

# ✅ Local GPT-2 generation
def generate_gpt2_response(prompt, max_length=150):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(
        inputs,
        max_length=max_length,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7,
        no_repeat_ngram_size=2,
        num_return_sequences=1
    )
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response_text[len(prompt):].strip()

def get_bot_reply(user_input):
    intent = detect_intent(user_input)
    goal_msg = update_goals(user_input)

    if goal_msg:
        return goal_msg

    if intent and intent in RESPONSE_DATA:
        reply = random.choice(RESPONSE_DATA[intent])
        if intent == "subjects":
            for subj in KEYWORDS["subjects"]:
                if subj in user_input.lower():
                    st.session_state.context_topic = subj
                    break
        else:
            st.session_state.context_topic = None
        return reply

    if st.session_state.context_topic:
        subj = st.session_state.context_topic
        if subj in RESPONSE_DATA.get("subjects", {}):
            return RESPONSE_DATA["subjects"][subj] + "\n\n(You asked about this before!)"

    sentiment = detect_sentiment(user_input)
    if sentiment == "positive":
        return "I'm glad you're feeling good! Keep it up! 🎉"
    elif sentiment == "negative":
        return "I'm sorry you're feeling that way. I'm here if you want to talk. 💙"

    return generate_gpt2_response(user_input)

with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        bot_reply = get_bot_reply(user_input)
        st.session_state.messages.append({'role': 'bot', 'content': bot_reply})

st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
msgs = st.session_state.messages
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
    st.info(
        "Try asking things like:\n"
        "- 'Give me study tips'\n"
        "- 'Tell me about physics'\n"
        "- 'How do I manage time?'\n"
        "- 'Motivate me please!'\n"
        "- 'Who created you?'\n"
        "- Or just say 'bye' to end the chat!"
    )

    st.markdown("### 🧠 Mini AI Assistant Mode")
    st.write("This bot tries to detect your intent and give focused advice or answers.")

def get_chat_history_text():
    lines = []
    for m in st.session_state.messages:
        role = m['role'].upper()
        content = m['content']
        lines.append(f"{role}: {content}\n")
    return "\n".join(lines)

filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
chat_history_text = get_chat_history_text()

st.download_button(
    label="💾 Download Chat History",
    data=chat_history_text,
    file_name=filename,
    mime="text/plain"
)
