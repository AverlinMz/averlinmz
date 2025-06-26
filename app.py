import streamlit as st
import random
import string
from html import escape
import datetime
import re
import tempfile
import os
from gtts import gTTS

# Hugging Face Inference Client
from huggingface_hub import InferenceClient

# Load your Hugging Face API token from Streamlit secrets
hf_token = st.secrets["HF_API_TOKEN"]

# Initialize Hugging Face client
client = InferenceClient(token=hf_token)

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
    "greetings": ["Hello there! 👋 How’s your day going? Ready to dive into learning today?"],
    "thanks": ["You’re very welcome! 😊"],
    "farewell": ["Goodbye! 👋 Come back soon for more study tips!"],
    "how_are_you": ["I'm doing well, thanks for asking! 💬 How are you feeling today?"],
    "user_feeling_good": ["That’s amazing to hear! 🎉 Keep riding that good energy!"],
    "contact_creator": ["You can contact Aylin Muzaffarli via email: aylin@example.com or through GitHub: https://github.com/aylinmuzaffarli"],
    "user_feeling_bad": ["Sorry to hear that. I’m always here if you want to talk or need a study boost. 💙🌟"],
    "exam_prep": ["Start early, revise often, rest well, and stay calm. You've got this! 💪"],
    "passed_exam": ["🎉 CONGRATULATIONS! That’s amazing news! I knew you could do it."],
    "love": ["Aww 💖 That's sweet! I'm just code, but I support you 100%!"],
    "capabilities": ["I give study tips, answer questions, track your goals, and cheer you on!"],
    "introduction": ["I'm AverlinMz, your study chatbot. My creator is Aylin Muzaffarli (2011, Azerbaijan)."],
    "creator_info": ["Created by Aylin — a student passionate about tech, science, and inspiring others."],
    "ack_creator": ["Absolutely! All credit goes to Aylin Muzaffarli! 🌟"],
    "subjects": {
        "math": "🧮 Math Tips: Practice daily. Understand concepts. Use visuals. Solve real problems. Review mistakes.",
        "physics": "🧪 Physics Tips: Learn the basics. Draw diagrams. Practice problems. Watch experiments. Memorize formulas.",
    },
    "fallback": ["Hmm, I’m not sure how to answer that — but I’ll learn! Try rephrasing. 😊"]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey"],
    "farewell": ["goodbye", "bye"],
    "how_are_you": ["how are you"],
    "user_feeling_good": ["i'm good", "great", "happy"],
    "user_feeling_bad": ["i'm sad", "not good", "tired"],
    "love": ["i love you"],
    "exam_prep": ["exam tips", "study for test"],
    "passed_exam": ["i passed"],
    "capabilities": ["what can you do"],
    "introduction": ["introduce", "who are you"],
    "creator_info": ["who is aylin"],
    "contact_creator": ["how can i contact aylin", "contact aylin", "how to contact"],
    "ack_creator": ["thank aylin"],
    "thanks": ["thank you"],
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

# Hugging Face AI call function
def get_ai_response(user_input):
    response = client.text_generation(
        model="mistralai/Mistral-Small-3.2-24B-Instruct-2506",
        inputs=user_input,
        parameters={"max_new_tokens": 100, "temperature": 0.7}
    )
    # The response format may vary, so check both options
    if hasattr(response, "generated_text"):
        return response.generated_text
    elif isinstance(response, list) and "generated_text" in response[0]:
        return response[0]["generated_text"]
    else:
        return "Sorry, I couldn't generate a response right now."

def get_bot_reply(user_input):
    intent = detect_intent(user_input)
    goal_msg = update_goals(user_input)
    if goal_msg:
        return goal_msg

    sentiment = detect_sentiment(user_input)
    st.session_state.last_sentiment = sentiment

    if intent and intent in RESPONSE_DATA:
        if intent == "subjects":
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
        return "I'm glad you're feeling good! Keep it up! 🎉"
    elif sentiment == "negative":
        return "You mentioned you're feeling down earlier. Want a tip to boost your mood or focus better? 💙"

    # Fallback to AI-generated reply when no intent matched
    return get_ai_response(user_input)

# Streamlit UI form for chat input and submission
with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        bot_reply = get_bot_reply(user_input)
        st.session_state.messages.append({'role': 'bot', 'content': bot_reply})
        clean_reply = remove_emojis(bot_reply)
        tts = gTTS(clean_reply, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tts_file:
            tts.save(tts_file.name)
            audio_bytes = open(tts_file.name, "rb").read()
        st.audio(audio_bytes, format="audio/mp3")
        os.unlink(tts_file.name)

# Display chat history in chat window
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
msgs = st.session_state.messages
for i in range(len(msgs) - 2, -1, -2):
    user_msg = msgs[i]['content']
    bot_msg = msgs[i+1]['content'] if i+1 < len(msgs) else ''
    st.markdown(f'<div class="user">{escape(user_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot">{escape(bot_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)

# Sidebar with goals, tips, and explanation
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

# Download chat history button
filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
chat_history_text = "\n".join([f"{m['role'].upper()}: {m['content']}\n" for m in st.session_state.messages])
st.download_button("📥 Download Chat History", chat_history_text, file_name=filename)
