import streamlit as st
import random
import string
from html import escape
import datetime
import re
import tempfile
import os
from gtts import gTTS
import difflib  # For fuzzy intent matching

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

# Theme selector
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
        "Hello there! 👋 How’s your day going? Ready to dive into learning today?",
        "Hey! How is it going? 😊",
        "Hi! What are you studying today?",
        "Hello! Ready to get smarter together?",
        "Hey there! Need some study tips?",
        "Hiya! Let's make today productive! 💪"
    ],
    "thanks": [
        "You’re very welcome! 😊",
        "No problem, happy to help!",
        "Glad I could assist!",
        "Anytime! Keep up the good work!",
        "My pleasure!",
        "You got it!"
    ],
    "farewell": [
        "Goodbye! 👋 Come back soon for more study tips!",
        "See you later! Keep studying hard!",
        "Take care! Don’t forget to rest too!",
        "Bye! Stay curious!",
        "Catch you later! 📚",
        "Farewell! Keep that brain sharp!"
    ],
    "how_are_you": [
        "I'm doing well, thanks for asking! 💬 How are you feeling today?",
        "Pretty good! How about you?",
        "Doing great! Ready to tackle some questions?",
        "Feeling good and ready to chat. You?",
        "I'm fine! What's on your mind?",
        "All systems go! How about you?"
    ],
    "user_feeling_good": [
        "That’s amazing to hear! 🎉 Keep riding that good energy!",
        "Awesome! Keep up the positivity!",
        "Great! Let’s use that energy to learn more!",
        "Happy to hear that! What’s next on your agenda?",
        "Fantastic! Let’s keep the momentum!",
        "Love that! Keep shining!"
    ],
    "user_feeling_bad": [
        "Sorry to hear that. I’m always here if you want to talk or need a study boost. 💙🌟",
        "That’s tough. Want some tips to improve your mood?",
        "I’m here to help if you want to vent or study distraction-free.",
        "Bad days happen. Let’s try a quick breathing exercise?",
        "I understand. Remember, every day is a fresh start!",
        "Stay strong. I believe in you!"
    ],
    "love": [
        "Aww 💖 That's sweet! I'm just code, but I support you 100%!",
        "I appreciate the love! You're awesome too!",
        "Sending virtual hugs back! 🤗",
        "I'm here to support your study journey with all my heart!",
        "Love makes the world go round — and learning too!",
        "Thanks for the love! Keep being amazing!"
    ],
    "exam_prep": [
        "Start early, revise often, rest well, and stay calm. You've got this! 💪",
        "Remember, understanding beats memorization. Focus on concepts.",
        "Practice past papers and time yourself to simulate exam conditions.",
        "Stay positive, eat well, and take short breaks during study sessions.",
        "Don't cram last minute—plan your study schedule in advance.",
        "Keep your confidence high and avoid distractions!"
    ],
    "passed_exam": [
        "🎉 CONGRATULATIONS! That’s amazing news! I knew you could do it.",
        "Well done! All your hard work paid off!",
        "You should be proud! Time to celebrate a little!",
        "Awesome achievement! Keep aiming higher!",
        "Fantastic! Ready for the next challenge?",
        "Success suits you well! Keep going!"
    ],
    "capabilities": [
        "I give study tips, answer questions, track your goals, and cheer you on!",
        "I can help with study advice, goal tracking, and motivation.",
        "Ask me about subjects, study techniques, or just chat!",
        "I'm here to support your learning journey in many ways.",
        "From tips to encouragement, I’m your study buddy.",
        "Think of me as your personal study assistant."
    ],
    "introduction": [
        "I'm AverlinMz, your study chatbot. My creator is Aylin Muzaffarli (2011, Azerbaijan).",
        "Hello! I'm AverlinMz, designed to help you study better.",
        "I’m here to help you with study tips and encouragement.",
        "Created by Aylin, I’m your friendly study companion.",
        "Nice to meet you! Let’s learn together.",
        "Your study chatbot friend, AverlinMz, at your service!"
    ],
    "creator_info": [
        "Created by Aylin — a student passionate about tech, science, and inspiring others.",
        "Aylin is the brilliant mind behind me, focused on tech and education.",
        "My creator, Aylin, loves science, programming, and helping others learn.",
        "Aylin developed me to assist with studying and motivation.",
        "Aylin’s passion for tech and science made this chatbot possible.",
        "Behind the scenes, Aylin works hard to improve your study experience."
    ],
    "ack_creator": [
        "Absolutely! All credit goes to Aylin Muzaffarli! 🌟",
        "I’m proud to be created by Aylin!",
        "Thanks for recognizing Aylin’s work!",
        "Aylin deserves all the applause for this chatbot!",
        "Big shoutout to Aylin for making me possible!",
        "Aylin’s creativity shines through me!"
    ],
    "subjects": {
        "math": [
            "🧮 Math Tips: Practice daily. Understand concepts. Use visuals. Solve real problems. Review mistakes.",
            "Try breaking down problems into smaller parts and solving step-by-step.",
            "Use online resources like Khan Academy for extra help.",
            "Focus on understanding formulas and why they work, not just memorizing.",
            "Practice problem-solving with past Olympiad questions.",
            "Make math fun by applying it to real-life scenarios."
        ],
        "physics": [
            "🧪 Physics Tips: Learn the basics. Draw diagrams. Practice problems. Watch experiments. Memorize formulas.",
            "Visualize problems by drawing free-body diagrams.",
            "Understand the concepts before jumping into calculations.",
            "Watch YouTube channels like Physics Girl for fun explanations.",
            "Do hands-on experiments to reinforce theory.",
            "Practice applying formulas in different scenarios."
        ],
        "chemistry": [
            "⚗️ Chemistry Tips: Balance equations. Understand reactions. Memorize key formulas. Use flashcards.",
            "Relate chemical reactions to real-world examples.",
            "Practice naming compounds and writing equations.",
            "Use mnemonic devices to remember groups and series.",
            "Review periodic table trends regularly.",
            "Conduct simple experiments at home if possible."
        ],
        "biology": [
            "🧬 Biology Tips: Learn diagrams. Understand processes. Use mnemonics. Relate to real life.",
            "Focus on cell structure and functions first.",
            "Use flashcards for vocabulary and processes.",
            "Connect biological concepts to your daily life.",
            "Draw and label diagrams repeatedly.",
            "Watch documentaries to deepen understanding."
        ],
        "computer science": [
            "💻 CS Tips: Practice coding daily. Understand algorithms. Solve problems. Learn data structures.",
            "Break coding problems into smaller tasks.",
            "Read others’ code to learn new techniques.",
            "Use online judges like Codeforces and LeetCode.",
            "Learn complexity analysis to write efficient code.",
            "Work on small projects to apply concepts."
        ],
        "english": [
            "📚 English Tips: Read daily. Practice writing. Expand vocabulary. Listen to native speakers.",
            "Try reading short stories and summarizing them.",
            "Write a daily journal in English.",
            "Learn new words and use them in sentences.",
            "Listen to English podcasts and mimic pronunciation.",
            "Watch movies with subtitles to improve understanding."
        ]
    },
    "fallback": [
        "Hmm, I’m not sure how to answer that — but I’ll learn! Try rephrasing. 😊",
        "Sorry, I didn't quite get that. Could you say it differently?",
        "I’m still learning. Can you try asking in another way?",
        "That’s a new one for me! Want to teach me?",
        "Oops, I don’t understand that yet. Try another question!",
        "I’m here to help once I understand better. Could you clarify?"
    ],
    "more_info": [
        "Sure! Here's another tip for you:",
        "Absolutely! Let's add one more tip:",
        "Here’s something else you might find useful:",
        "Another tip coming right up:",
        "Let me share one more tip with you:",
        "Here’s an extra piece of advice:"
    ]
}

KEYWORDS = {
    "greetings": [
        "hello", "hi", "hey", "hiya", "good morning", "good afternoon", "how is it going", "what's up"
    ],
    "farewell": [
        "goodbye", "bye", "see you", "later", "farewell", "take care", "catch you later"
    ],
    "how_are_you": [
        "how are you", "how's it going", "how do you do", "what's up", "how are you feeling"
    ],
    "user_feeling_good": [
        "i'm good", "great", "happy", "doing well", "feeling good", "awesome", "doing fine"
    ],
    "user_feeling_bad": [
        "i'm sad", "not good", "tired", "depressed", "down", "feeling bad", "exhausted"
    ],
    "love": [
        "i love you", "love you", "luv you", "i like you"
    ],
    "exam_prep": [
        "exam tips", "study for test", "prepare for exam", "how to study", "exam advice", "test preparation"
    ],
    "passed_exam": [
        "i passed", "i did it", "exam success", "i cleared the test", "exam results"
    ],
    "capabilities": [
        "what can you do", "your abilities", "features", "what are you", "help me"
    ],
    "introduction": [
        "introduce", "who are you", "about you", "yourself", "tell me about yourself"
    ],
    "creator_info": [
        "who is aylin", "about aylin", "creator info", "who made you"
    ],
    "contact_creator": [
        "how can i contact aylin", "contact aylin", "how to contact", "aylin contact", "reach aylin"
    ],
    "ack_creator": [
        "thank aylin", "thanks aylin", "thank you aylin", "appreciate aylin"
    ],
    "thanks": [
        "thank you", "thanks", "thx", "ty", "thank you very much"
    ],
    "subjects": [
        "math", "physics", "chemistry", "biology", "computer science", "english", "cs", "bio", "chem", "phys"
    ],
    "more_info": [
        "give me more tips", "more advice", "tell me more", "can you add more", "another tip",
        "more please", "more info", "more details", "keep going", "more", "tell me something else"
    ]
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
    all_phrases = []
    phrase_to_intent = {}

    for intent, phrases in KEYWORDS_CLEANED.items():
        for phrase in phrases:
            all_phrases.append(phrase)
            phrase_to_intent[phrase] = intent

    closest = difflib.get_close_matches(msg, all_phrases, n=1, cutoff=0.4)
    if closest:
        return phrase_to_intent[closest[0]]
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
    positive = ["good", "great", "awesome", "love", "happy"]
    negative = ["bad", "sad", "tired", "depressed"]
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

    # Handle subject keywords separately to set context
    if intent in KEYWORDS["subjects"]:
        st.session_state.context_topic = intent
        return random.choice(RESPONSE_DATA["subjects"].get(intent, RESPONSE_DATA["fallback"]))

    if intent == "more_info":
        if st.session_state.context_topic and st.session_state.context_topic in RESPONSE_DATA["subjects"]:
            tips = RESPONSE_DATA["subjects"][st.session_state.context_topic]
            tip = random.choice(tips)
            prefix = random.choice(RESPONSE_DATA["more_info"])
            return f"{prefix}\n{tip}"
        else:
            return "Could you please tell me which subject or topic you'd like more tips on?"

    if intent and intent in RESPONSE_DATA:
        st.session_state.context_topic = None
        return random.choice(RESPONSE_DATA[intent])

    if st.session_state.context_topic:
        subj = st.session_state.context_topic
        return "\n".join(RESPONSE_DATA["subjects"].get(subj, random.choice(RESPONSE_DATA["fallback"]))) + "\n\n(You asked about this before!)"

    if sentiment == "positive":
        return "I'm glad you're feeling good! Keep it up! 🎉"
    elif sentiment == "negative":
        return "You mentioned you're feeling down earlier. Want a tip to boost your mood or focus better? 💙"

    return random.choice(RESPONSE_DATA["fallback"])


with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        bot_reply = get_bot_reply(user_input)
        st.session_state.messages.append({'role': 'bot', 'content': bot_reply})

# Display chat messages in chronological order
if st.session_state.messages:
    for i in range(0, len(st.session_state.messages), 2):
        user_msg = st.session_state.messages[i]['content']
        bot_msg = st.session_state.messages[i+1]['content'] if i + 1 < len(st.session_state.messages) else ''
        st.markdown(f'<div class="user">{escape(user_msg)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bot">{escape(bot_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

# Generate audio of last bot reply
if st.session_state.messages and st.session_state.messages[-1]['role'] == 'bot':
    last_bot_msg = st.session_state.messages[-1]['content']
    try:
        tts = gTTS(text=last_bot_msg, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            audio_file = tmp_file.name
        st.audio(audio_file, format='audio/mp3')
        # Remove the temp file after playing
        os.unlink(audio_file)
    except Exception as e:
        st.warning("Sorry, audio playback failed.")

# Button to download chat history
def download_chat():
    chat_text = ""
    for msg in st.session_state.messages:
        role = "You" if msg['role'] == 'user' else "AverlinMz"
        chat_text += f"{role}: {msg['content']}\n"
    return chat_text

st.download_button(
    label="📥 Download Chat History",
    data=download_chat(),
    file_name=f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
    mime="text/plain"
)

# Show current goals
if st.session_state.goals:
    st.markdown("### 🎯 Your Study Goals:")
    for g in st.session_state.goals:
        st.markdown(f"- {escape(g)}")

