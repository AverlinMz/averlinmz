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

# ---------------- INITIALIZE SESSION ----------------
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

# ---------------- HELPER FUNCTIONS ----------------
def remove_emojis(text):
    emoji_pattern = re.compile("[\U0001F600-\U0001F64F"
                               "\U0001F300-\U0001F5FF"
                               "\U0001F680-\U0001F6FF"
                               "\U0001F1E0-\U0001F1FF"
                               "\U00002700-\U000027BF"
                               "\U000024C2-\U0001F251]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def clean_keyword_list(keywords_dict):
    cleaned = {}
    for intent, phrases in keywords_dict.items():
        cleaned[intent] = [p.lower().translate(str.maketrans('', '', string.punctuation)).strip() for p in phrases]
    return cleaned

# ---------------- RESPONSE & KEYWORDS ----------------
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
    "Nice to meet you! Let's learn and grow together. 🌱📘 Want to know more? <a href='https://aylinmuzaffarli.github.io/averlinmz-site/' target='_blank'>Click here</a> 🚀"
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
} # YOUR FULL RESPONSE_DATA GOES HERE (copy from your previous message)
KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "hiya", "greetings", "what's up", "howdy", "good morning", "good afternoon", "good evening", "sup", "yo"],
    "farewell": ["goodbye", "bye", "see you", "farewell", "later", "take care", "until next time", "signing off", "talk later", "catch you later", "peace out"],
    "how_are_you": ["how are you", "how's it going", "how do you do", "how have you been", "what's new", "how's life", "how's everything", "how're things"],
    "user_feeling_good": ["i'm good", "great", "happy", "doing well", "awesome", "fine", "fantastic", "wonderful", "excellent", "perfect", "super", "amazing", "terrific"],
    "user_feeling_bad": ["i'm sad", "not good", "tired", "depressed", "down", "exhausted", "stressed", "anxious", "overwhelmed", "frustrated", "awful", "terrible", "horrible"],
    "love": ["i love you", "love you", "luv you", "like you", "adore you", "you're amazing", "you're awesome", "you're great", "you're wonderful"],
    "exam_prep": ["exam tips", "study for test", "prepare for exam", "how to study", "exam advice", "test preparation", "studying help", "exam strategies", "test tips", "study techniques", "best way to study", "exam prep"],
    "passed_exam": ["i passed", "i did it", "exam success", "cleared the test", "exam results", "got good marks", "aced the exam", "passed with flying colors", "nailed the test", "killed the exam"],
    "capabilities": ["what can you do", "your abilities", "features", "help me", "what do you offer", "how can you help", "your functions", "what help", "your skills"],
    "introduction": ["introduce", "who are you", "about you", "yourself", "tell me about yourself", "what are you", "your purpose", "your identity"],
    "creator_info": ["who is aylin", "about aylin", "creator info", "who made you", "who created you", "who built you", "who programmed you", "who developed you"],
    "contact_creator": ["how can i contact aylin", "contact aylin", "how to contact", "reach aylin", "get in touch with creator", "aylin's contact", "aylin's info", "reach the maker"],
    "ack_creator": ["thank aylin", "thanks aylin", "thank you aylin", "appreciate aylin", "grateful to aylin", "kudos to aylin", "props to aylin"],
    "thanks": ["thank you", "thanks", "thx", "ty", "much appreciated", "many thanks", "grateful", "appreciate it", "thanks a lot", "thank you so much"],
    "subjects": ["math", "physics", "chemistry", "biology", "history", "language", "programming", "literature", "geography", "economics",
                "mathematics", "physic", "chem", "bio", "hist", "lang", "code", "lit", "geo", "econ",
                "algebra", "calculus", "trigonometry", "statistics", "quantum", "mechanics", "thermodynamics",
                "organic", "inorganic", "biochemistry", "genetics", "zoology", "botany", "anatomy",
                "world history", "ancient", "medieval", "modern", "political",
                "english", "spanish", "french", "german", "russian", "linguistics",
                "python", "java", "javascript", "c++", "coding", "web development",
                "poetry", "novel", "drama", "fiction", "shakespeare",
                "physical geography", "human geography", "cartography", "gis",
                "microeconomics", "macroeconomics", "finance", "business"]
}
       # YOUR FULL KEYWORDS GO HERE (copy from your previous message)

KEYWORDS_CLEANED = clean_keyword_list(KEYWORDS)

# ---------------- INTENT DETECTION ----------------
def detect_intent(text):
    msg = clean_text(text)

    # 1. Full message fuzzy match
    for intent, kws in KEYWORDS_CLEANED.items():
        match = get_close_matches(msg, kws, n=1, cutoff=0.65)
        if match:
            return intent

    # 2. Substring check
    for intent, kws in KEYWORDS_CLEANED.items():
        if any(kw in msg for kw in kws):
            return intent

    # 3. Word-level fuzzy match
    for word in msg.split():
        for intent, kws in KEYWORDS_CLEANED.items():
            match = get_close_matches(word, kws, n=1, cutoff=0.65)
            if match:
                return intent

    # 4. Subject check
    for subj in KEYWORDS["subjects"]:
        if subj in msg:
            return "subjects"

    return None

# ---------------- SENTIMENT & GOAL ----------------
def detect_sentiment(text):
    positive = ["good", "great", "awesome", "love", "happy", "fine", "well", "fantastic", "wonderful", "excellent", "perfect", "super", "amazing", "terrific"]
    negative = ["bad", "sad", "tired", "depressed", "down", "exhausted", "stressed", "anxious", "overwhelmed", "frustrated", "awful", "terrible", "horrible"]
    txt = clean_text(text)
    if any(word in txt for word in positive): return "positive"
    if any(word in txt for word in negative): return "negative"
    return "neutral"

def update_goals(user_input):
    msg = clean_text(user_input)
    goal_keywords = ["goal", "aim", "plan", "objective", "target", "resolution", "ambition", "purpose", "intention"]
    if any(kw in msg for kw in goal_keywords):
        if user_input not in st.session_state.goals:
            st.session_state.goals.append(user_input)
            return "Got it! I've added that to your study goals."
        else:
            return "You already mentioned this goal."
    return None

# ---------------- BOT REPLY ----------------
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
        return "Glad to hear you're feeling good! Keep it up! 🎉"
    elif sentiment == "negative":
        return "I noticed you're feeling down. If you want, I can share some tips or just listen. 💙 "

    possible_subjects = [subj for subj in KEYWORDS["subjects"] if subj in user_input.lower()]
    if possible_subjects:
        return f"I see you mentioned {possible_subjects[0]}. Here are some tips:\n\n{RESPONSE_DATA['subjects'].get(possible_subjects[0], '')}"

    return random.choice(RESPONSE_DATA["fallback"])

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="AverlinMz Chatbot", layout="wide")

with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        bot_reply = get_bot_reply(user_input)
        st.session_state.messages.append({'role': 'bot', 'content': bot_reply})

        # Generate TTS audio
        clean_reply = remove_emojis(bot_reply)
        tts = gTTS(clean_reply, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tts_file:
            tts.save(tts_file.name)
            audio_bytes = open(tts_file.name, "rb").read()
        st.audio(audio_bytes, format="audio/mp3")
        os.unlink(tts_file.name)

# ---------------- MESSAGE DISPLAY ----------------
st.markdown('<div style="max-width:800px;margin:auto">', unsafe_allow_html=True)
msgs = st.session_state.messages
for i in range(len(msgs) - 2, -1, -2):
    user_msg = msgs[i]['content']
    bot_msg = msgs[i+1]['content'] if i+1 < len(msgs) else ''
    st.markdown(f'<div class="user">{escape(user_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot">{bot_msg.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### 🌟 Your Goals")
    if st.session_state.goals:
        for g in st.session_state.goals:
            st.write("- " + g)
    else:
        st.write("You haven't set any goals yet. Tell me your goals!")

    st.markdown("### 💡 Tips")
    st.info("Try asking things like:\n- 'Give me study tips'\n- 'Tell me about physics'\n- 'How do I manage time?'\n- Or just say 'bye' to end the chat!")

    # Prepare chat history text for download button here
    filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    chat_history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])

    st.download_button("📅 Download Chat History", chat_history_text, file_name=filename)
