import streamlit as st
import random
import string
from html import escape
import re
from gtts import gTTS
import tempfile
import os
import difflib

# Initialize session state to store chat history and context
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

# Function to remove emojis from user input for easier matching
def remove_emojis(text):
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F"
                               "\U0001F300-\U0001F5FF"
                               "\U0001F680-\U0001F6FF"
                               "\U0001F1E0-\U0001F1FF"
                               "\U00002700-\U000027BF"
                               "\U000024C2-\U0001F251]+",
                               flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# Set page config and title/icon
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="https://i.imgur.com/mJ1X49g_d.webp",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Theme selector with styles
theme = st.sidebar.selectbox("🎨 Choose a theme", ["Default", "Night", "Blue"])
if theme == "Night":
    st.markdown("""<style>body, .stApp { background:#111; color:#fff; } .user {background:#333;color:#fff;} .bot {background:#444;color:#fff;}</style>""", unsafe_allow_html=True)
elif theme == "Blue":
    st.markdown("""<style>body, .stApp { background:#e0f7fa; } .user {background:#81d4fa;color:#01579b;} .bot {background:#b2ebf2;color:#004d40;}</style>""", unsafe_allow_html=True)

# CSS for chat layout and styling
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

# Title and logo
st.markdown("""
<div class="title-container">
  <img src="https://i.imgur.com/mJ1X49g_d.webp" alt="Chatbot Image" style="width:150px;border-radius:20px;margin-bottom:10px;"/>
  <h1>AverlinMz – Study Chatbot</h1>
</div>
""", unsafe_allow_html=True)

# Response data for intents and subjects
RESPONSE_DATA = {
    "greetings": [
        "Hello there! 👋 How’s your day going?",
        "Hi! 😊 Ready to crush some study goals?",
        "Hey hey! What shall we dive into today?",
        "Welcome! 🎒 Let’s learn something new!",
    ],
    "thanks": [
        "You’re very welcome! 😊",
        "No problem at all! Always here to help!",
        "Happy to help anytime! 🌟",
    ],
    "farewell": [
        "Goodbye! 👋 Come back soon for more study tips!",
        "Take care! 📚 Stay curious!",
        "See you next time! Keep going strong!",
    ],
    "how_are_you": [
        "I'm doing well, thanks for asking! 💬 How are you feeling today?",
        "Feeling energetic and ready to help! How are you?",
        "Buzzing with knowledge! 😄 You?",
    ],
    "user_feeling_good": [
        "That’s amazing to hear! 🎉 Keep riding that good energy!",
        "Glad to hear you’re feeling great! Let’s keep it up!",
        "Awesome! Positive vibes make learning easier!",
    ],
    "user_feeling_bad": [
        "Sorry to hear that. I’m here if you need support. 💙",
        "Tough days happen. Want to try a small productivity win?",
        "Sending you good vibes 💫 Let’s find one thing to feel proud of today.",
    ],
    "contact_creator": [
        "You can contact Aylin by filling this form: https://docs.google.com/forms/d/1hYk968UCuX0iqsJujVNFGVkBaJUIhA67SXJKe0xWeuM/edit",
    ],
    "exam_prep": [
        "Start early, revise often, rest well. You've got this! 💪",
        "Break topics into small parts, use spaced repetition, stay hydrated!",
        "Practice past questions, and don’t forget breaks. 🧠💧",
    ],
    "passed_exam": [
        "🎉 CONGRATULATIONS! That’s amazing news!",
        "Proud of you! You worked hard and it paid off!",
        "Knew you could do it! What’s next on your learning journey?",
    ],
    "love": [
        "Aww 💖 That's sweet! I’m just a bot, but I support you fully!",
        "Virtual hug incoming! 🤗",
        "You’re the best! Thanks for making my code smile! 😄",
    ],
    "capabilities": [
        "I give study tips, answer questions, track goals, and keep you motivated! 💪",
        "I’m your learning buddy! Ask about subjects, exams, moods, or set goals!",
        "I help with study hacks, reminders, advice, and cheerful support!",
    ],
    "introduction": [
        "I'm AverlinMz, your study chatbot! Built by Aylin Muzaffarli to help students shine. ✨",
        "I’m your AI sidekick in the learning world, powered by Aylin’s vision. 🌍",
    ],
    "creator_info": [
        "Created by Aylin — student, coder, physicist in training, and all-around knowledge adventurer! 🌟",
        "Aylin Muzaffarli built me to help students love learning and grow smarter every day.",
    ],
    "ack_creator": [
        "Aylin deserves all the credit! 👏👏",
        "Absolutely — she’s brilliant and dedicated. 🧠❤️",
    ],
    "subjects": {
        "math": "🧮 Math Tips: Practice daily. Understand concepts. Use visuals. Solve real problems. Review mistakes.",
        "math_more": "Try solving with peers, teach someone else, and focus on weak topics. Use Khan Academy or AoPS too!",
        "physics": "🧪 Physics Tips: Learn the basics. Draw diagrams. Practice problems. Watch experiments. Memorize formulas.",
        "physics_more": "Use simulations, revise past questions, and understand units and real-world applications.",
        "chemistry": "⚗️ Chemistry Tips: Balance equations. Understand reactions. Memorize key formulas. Use flashcards.",
        "chemistry_more": "Use mind maps, mnemonic devices for groups, and do visual experiments online.",
        "biology": "🧬 Biology Tips: Learn diagrams. Understand processes. Use mnemonics. Relate to real life.",
        "biology_more": "Quiz yourself regularly, make storylines out of biological cycles, and practice with diagrams.",
        "computer science": "💻 CS Tips: Practice coding daily. Understand algorithms. Solve problems. Learn data structures.",
        "computer science_more": "Try small projects, join code clubs, and study from real open-source repos!",
        "english": "📚 English Tips: Read daily. Practice writing. Expand vocabulary. Listen to native speakers.",
        "english_more": "Use grammar tools, write a journal, and discuss books or podcasts.",
    },
    "fallback": [
        "Hmm, I’m not sure how to answer that — but I’ll learn! 😊 Try rephrasing?",
        "Sorry, I didn’t catch that. Can you ask it another way?",
        "Interesting... but I don’t know what to say! Maybe ask about a subject?",
    ]
}

# Keywords to detect intent
KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "yo", "greetings", "good morning", "good evening"],
    "farewell": ["goodbye", "bye", "see you", "later", "farewell"],
    "how_are_you": ["how are you", "how do you feel", "you okay"],
    "user_feeling_good": ["i'm good", "i'm great", "i feel amazing", "i’m happy"],
    "user_feeling_bad": ["i'm sad", "i’m tired", "not good", "i feel bad", "i’m stressed"],
    "love": ["i love you", "love you bot", "you’re cute"],
    "exam_prep": ["exam tips", "how to study", "help with test", "study advice"],
    "passed_exam": ["i passed", "i succeeded", "i got good grades"],
    "capabilities": ["what can you do", "how can you help", "what do you do"],
    "introduction": ["introduce yourself", "who are you", "what’s your name"],
    "creator_info": ["who is aylin", "who made you", "creator of this bot"],
    "contact_creator": ["how can i contact aylin", "contact aylin", "how to reach aylin"],
    "ack_creator": ["thank aylin", "credit aylin", "who deserves thanks"],
    "thanks": ["thank you", "thanks a lot", "appreciate it"],
    "subjects": ["math", "physics", "chemistry", "biology", "computer science", "english", "science", "cs", "bio", "chem"],
    "more_request": ["more", "give more", "additional", "more advice", "tell me more"]
}

# Find user intent from input text using keywords
def find_intent(user_text):
    user_text_lower = user_text.lower()
    for intent, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in user_text_lower:
                return intent
    return None

# Find best matching subject using fuzzy matching
def get_best_subject_match(user_text):
    subjects = RESPONSE_DATA["subjects"].keys()
    user_text_lower = user_text.lower()
    best_match = None
    highest_ratio = 0
    for subject in subjects:
        ratio = difflib.SequenceMatcher(None, subject, user_text_lower).ratio()
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = subject
    if highest_ratio > 0.6:
        return best_match
    return None

# Generate chatbot response based on user input and context
def generate_response(user_text):
    text = remove_emojis(user_text).lower().strip()

    # If user asks for more info
    if any(phrase in text for phrase in KEYWORDS["more_request"]):
        topic = st.session_state.context_topic
        if topic and topic + "_more" in RESPONSE_DATA["subjects"]:
            return RESPONSE_DATA["subjects"][topic + "_more"]
        else:
            return "Could you please specify the subject you want more info on? For example, type 'math', 'physics', or 'chemistry'."

    intent = find_intent(text)

    # If intent is about subjects
    if intent == "subjects" or text in KEYWORDS["subjects"]:
        subj = None
        for s in KEYWORDS["subjects"]:
            if s in text:
                subj = s
                break
        if subj:
            st.session_state.context_topic = subj
            return RESPONSE_DATA["subjects"].get(subj, "Sorry, I don't have tips for that subject yet.")

    # For other intents
    if intent and intent in RESPONSE_DATA:
        # Save context if subject
        if intent == "subjects":
            st.session_state.context_topic = text
        return random.choice(RESPONSE_DATA[intent])

    # Try fuzzy subject match if no intent found
    subj = get_best_subject_match(text)
    if subj:
        st.session_state.context_topic = subj
        return RESPONSE_DATA["subjects"][subj]

    # Default fallback responses
    return random.choice(RESPONSE_DATA["fallback"])

# Generate speech audio from text using gTTS
def synthesize_speech(text):
    try:
        tts = gTTS(text=text, lang='en')
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp_file.name)
        return tmp_file.name
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

# Display chat messages on the screen
def display_chat():
    st.markdown('<div class="chat-window">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        role = message["role"]
        content = escape(message["content"])
        css_class = "user" if role == "user" else "bot"
        st.markdown(f'<div class="{css_class}">{content}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.title("AverlinMz Chatbot")

    # Display previous messages only once at the start
    display_chat()

    # Use a form with text input and send button
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("Your message:")
        submitted = st.form_submit_button("Send")

        if submitted and user_input.strip():
            # Add user's message
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Generate bot response
            response = generate_response(user_input)
            st.session_state.messages.append({"role": "bot", "content": response})

            # Display updated chat (only once after new messages)
            display_chat()

            # Generate and play audio
            audio_file = synthesize_speech(response)
            if audio_file:
                audio_bytes = open(audio_file, "rb").read()
                st.audio(audio_bytes, format="audio/mp3")
                os.remove(audio_file)

if __name__ == "__main__":
    main()
