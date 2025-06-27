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
      "how_are_you": [
        "I'm doing well, thanks! How are you feeling today? 🙂",
        "All good here! How about you? 🤗",
        "Feeling ready to help! What about you? ⚡",
        "Doing great! How's your mood? 🌈"
    ],
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
  
    "burnout": [
        "You're pushing hard — maybe too hard. A short break can recharge you more than another hour of stress. 🌱",
        "No shame in feeling tired. Real strength is knowing when to pause. Rest isn't quitting — it's strategy. 💡",
        "Even your brain has a battery. When it's drained, rest is productive. Let’s reset — you’ll come back stronger. 🔋",
        "Breaks aren’t wasted time. They're investments in your energy. Use them wisely. 💫"
    ],
    "exam_exhaustion": [
        "When exams take everything from you, give something back to yourself — like sleep, or joy, or a quiet moment. ☁️",
        "This exam won't define your life. Resting today might save your focus for tomorrow. 🧠✨",
        "Even high-achievers need off-switches. Your value isn’t based on how many hours you grind. ⏳",
        "Take care of you. Without that, no exam score will ever be worth it. 🤍"
    ],
    "health_tips": [
        "🩺 Health Tip: Your brain needs hydration, rest, and oxygen. That means water, sleep, and short walks. 🚶",
        "You can’t pour from an empty cup. Prioritize basic care: food, rest, breath. 🧘",
        "Sleep isn't a luxury. It's fuel for thinking. Power off to power up. 🔋",
        "Balance your inputs: good food, good music, good thoughts. What you feed yourself becomes your energy. 🧠💚"
    ],
    "study_balance": [
        "Study smart, not just long. Rest turns short-term memory into long-term gains. 🧠",
        "Rest is part of the strategy, not an excuse. Athletes rest to win — so should learners. 🏁",
        "If your head's foggy, maybe it's time to close the books and open a window. 🌬️",
        "Burnout isn’t proof of dedication — balance is. Keep your flame, don’t burn it out. 🔥🕯️"
    ],
    "night_stress": [
        "Late nights magnify worry. If it’s past midnight and your brain is spiraling, pause. Sleep is healing. 🌙",
        "2AM thoughts lie. Sleep now, and return when your mind is clearer. 🌅",
        "Working while exhausted is like writing in fog. You’ll spend more fixing than gaining. 💤",
        "Pause. You’re not giving up. You’re protecting your mind. That’s smart. 🧠💤"
    ],
    "perfectionism": [
        "Perfection is a cage. Progress is the key. Let yourself move forward. 🔓",
        "Nobody does it perfectly — they just keep showing up. That’s enough. 📈",
        "Your first draft won’t be flawless. That’s okay. Mastery is messy. ✍️",
        "You’re learning, not performing. Messy is normal. Beautiful even. 🎨"
    ],
    "self_doubt": [
        "Smart people doubt themselves. It’s a side effect of caring. Don’t stop because of it. 💭",
        "Feeling unsure doesn’t mean you’re not capable. It means you’re human. 🌍",
        "You don’t need proof of brilliance. You need patience with your growth. 🌱",
        "Self-doubt is a fog, not a wall. You *can* move through it. ☁️➡️🌤️"
    ],
    "resilience": [
        "Resilience isn’t toughness — it’s learning how to stand back up. You’re doing that. ✨",
        "You fell. You’re getting up. That’s the story. That’s the win. 🏆",
        "Each setback is data. You’re debugging life — and you’re improving. 👩‍💻",
        "Keep going. Not because it’s easy. But because you’re growing. 🌿"
    ],
    "emotion_checkin": [
        "Before we dive in — how are you *really* feeling? This is your space. 🌈",
        "Let's pause. What emotion’s loudest right now? You can tell me. 🤍",
        "Even one word is enough. Tired? Excited? Meh? I'm here for all of it. ✍️",
        "Your emotions matter. Not just your progress. Let’s hold both. 🧠❤️"
    ],
    "daily_review": [
        "Reflect time: What’s one thing you did today that you’re glad about? Even tiny wins matter. ✨",
        "Today’s done. What did you try? What worked? What’s worth repeating? 🔄",
        "You survived today. That’s already something. Be kind to yourself. 🌙",
        "Journal moment: What challenged you today — and what did you learn from it? 📓"
    ],
    "set_goal": [
        "What’s one small goal we can aim for today? Keep it real. Keep it doable. 🎯",
        "Start with a target: Finish 3 questions? Read 2 pages? Let’s define it. 🗂️",
        "Clarity makes action easier. What’s the one thing you want to complete today? 🧭",
        "Name your goal — and let’s make your future self proud. 🚀"
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
        "Hello! I'm here to support your study journey. ✨ Visit my site: <a href='https://aylinmuzaffarli.github.io/averlinmz-site/' target='_blank'>AverlinMz Website</a> 💻",
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
    "emotional_support": [
        "It's okay to feel overwhelmed. You're not alone in this — let’s take it one step at a time. 🤗",
        "Your feelings are valid. Taking care of your mind is just as important as your studies. 🧠❤️",
        "When the load feels too heavy, remember: small steps forward still move you ahead. 🌿",
        "You’re stronger than you think. Together, we’ll find ways to cope and keep going. 💪"
    ],
    "growth_mindset": [
        "Mistakes are proof you're trying. Every error is a step towards mastery. 📈",
        "Curiosity is your best study partner — ask questions, explore, and grow! 🌱",
        "Challenges shape you — they’re not roadblocks but stepping stones. Keep climbing! 🧗",
        "Growth isn’t linear. Be patient with yourself and celebrate progress, no matter how small. 🎉"
    ],
    "smart_study": [
        "Active recall beats passive reading — test yourself often! 🧠",
        "Switch subjects to keep your brain fresh and focused. Variety helps retention. 🔄",
        "Set specific, achievable goals to avoid overwhelm. Clarity fuels action. 🎯",
        "Teach what you learn — explaining concepts deepens understanding. 👩‍🏫"
    ],
    "fun_curiosity": [
        "Did you know? The brain’s neurons can make a thousand new connections every second! 🤯",
        "Here's a fun fact: The word 'quiz' started as a bet! Want to know more quirky study trivia? 🤓",
        "Taking a short laugh break boosts memory retention. Ready for a study joke? 🃏",
        "Curiosity sparks dopamine — the brain’s reward chemical. Learning is literally addictive! 🎉"
    ],
    "user_reflection": [
        "What’s one thing you learned today that surprised you? 🤔",
        "How did you feel during your study session? Tracking emotions helps improve focus. 📊",
        "What’s a small win you can celebrate today? Recognition fuels motivation! 🏆",
        "Are your study goals still relevant? Adjusting plans is a sign of wisdom, not weakness. 🔧"
    ],
    "fallback": [
        "Sorry, I didn't understand that. Can you try asking differently? 🤔",
        "Hmm, I’m not sure how to respond to that yet. Let’s keep the focus on studies! 📚",
        "I didn’t quite get that. Could you rephrase or ask something else? 💡"
    ]
}

KEYWORDS = {
    "greetings": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings", "yo"],
    "thanks": ["thanks", "thank you", "thx", "thankful", "appreciate"],
    "farewell": ["bye", "goodbye", "see you", "farewell", "later", "catch you", "take care"],
    "how_are_you": ["how are you", "how do you feel", "how's it going", "how you doing", "how are things"],
    "burnout": ["burnout", "exhausted", "tired", "overwhelmed", "fatigue", "drained"],
    "exam_exhaustion": ["exams", "exam stress", "exam tired", "study exhaustion", "test fatigue", "exam anxiety"],
    "health_tips": ["health", "wellbeing", "well-being", "self-care", "rest", "hydrate", "sleep", "exercise"],
    "study_balance": ["balance", "study rest", "take break", "overstudy", "study too much", "burned out"],
    "night_stress": ["night", "late night", "insomnia", "can't sleep", "anxiety night", "stress at night"],
    "perfectionism": ["perfect", "perfectionism", "too perfect", "can't finish", "always wrong", "perfect is hard"],
    "self_doubt": ["self doubt", "doubt myself", "not sure", "uncertain", "confidence", "insecure"],
    "resilience": ["resilience", "keep going", "bounce back", "don't give up", "push through", "keep fighting"],
    "emotion_checkin": ["feelings", "emotions", "mood", "emotion check", "how do I feel"],
    "daily_review": ["today", "daily review", "reflection", "how was today", "what did I do"],
    "set_goal": ["goal", "set goal", "target", "aim", "objective", "plan for today"],
    "user_feeling_good": ["good", "great", "happy", "awesome", "excited", "fine", "well"],
    "user_feeling_bad": ["bad", "sad", "tired", "down", "unhappy", "stressed", "anxious", "worried"],
    "love": ["love you", "thanks", "appreciate you", "like you", "grateful"],
    "exam_prep": ["exam prep", "study for exams", "test prep", "preparing for exam", "exam tips"],
    "passed_exam": ["passed exam", "exam result", "exam success", "I passed", "got good grade", "success"],
    "capabilities": ["what can you do", "capabilities", "help", "assist", "features", "what are you"],
    "introduction": ["who are you", "introduce yourself", "about you", "your name", "creator"],
    "creator_info": ["creator", "who made you", "author", "developer", "owner"],
    "ack_creator": ["credit", "acknowledge", "thanks to", "creator credit"],
    "contact_creator": ["contact", "reach", "feedback", "message", "form"],
    "subjects": [
        "math", "physics", "chemistry", "biology", "history", "language",
        "programming", "literature", "geography", "economics"
    ],
    "emotional_support": ["overwhelmed", "stress", "sad", "anxious", "frustrated", "upset"],
    "growth_mindset": ["mistakes", "fail", "failure", "try again", "learning", "progress", "growth"],
    "smart_study": ["study tips", "study advice", "learn better", "study smarter", "study strategy"],
    "fun_curiosity": ["fun fact", "did you know", "curious", "interesting", "trivia", "joke"],
    "user_reflection": ["reflect", "reflection", "learned today", "feelings about study", "goals progress"],
    "fallback": []  # Usually triggered when none of the above matches
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
    
    # First check for exact matches
    for intent, kws in KEYWORDS_CLEANED.items():
        if any(kw in msg for kw in kws):
            return intent
    
    # Then check for similar words using fuzzy matching
    words = msg.split()
    for word in words:
        for intent, kws in KEYWORDS_CLEANED.items():
            # Find close matches with 65% similarity threshold (lowered for broader matching)
            matches = get_close_matches(word, kws, n=1, cutoff=0.65)
            if matches:
                return intent
    
    # Special case for subject detection with partial matching
    for subj in KEYWORDS["subjects"]:
        if subj in msg:
            return "subjects"
    
    return None

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

def detect_sentiment(text):
    positive = ["good", "great", "awesome", "love", "happy", "fine", "well", "fantastic", "wonderful", "excellent", "perfect", "super", "amazing", "terrific"]
    negative = ["bad", "sad", "tired", "depressed", "down", "exhausted", "stressed", "anxious", "overwhelmed", "frustrated", "awful", "terrible", "horrible"]
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
        return "Glad to hear you're feeling good! Keep it up! 🎉"
    elif sentiment == "negative":
        return "I noticed you're feeling down. If you want, I can share some tips or just listen. 💙"

    # Enhanced fallback that tries to extract possible subjects
    possible_subjects = [subj for subj in KEYWORDS["subjects"] if subj in user_input.lower()]
    if possible_subjects:
        return f"I see you mentioned {possible_subjects[0]}. Here are some tips:\n\n{RESPONSE_DATA['subjects'].get(possible_subjects[0], '')}"

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
    # Use markdown with unsafe_allow_html=True so links work
    st.markdown(f'<div class="user">{escape(user_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bot">{bot_msg.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
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


