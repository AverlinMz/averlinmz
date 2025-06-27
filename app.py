import streamlit as st
import random
import string
from html import escape
import datetime
import re
import tempfile
import os
from gtts import gTTS
from fuzzywuzzy import fuzz, process
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

# Text preprocessing with common text speak conversions
def preprocess_text(text):
    text = text.lower().strip()
    # Common text speak substitutions
    substitutions = {
        ' u ': ' you ',
        ' r ': ' are ',
        ' ur ': ' your ',
        ' hw ': ' how ',
        ' wat ': ' what ',
        ' wen ': ' when ',
        ' wher ': ' where ',
        ' y ': ' why ',
        ' pls ': ' please ',
        ' thx ': ' thanks ',
        ' tysm ': ' thank you so much ',
        ' ty ': ' thank you ',
        ' rly ': ' really ',
        ' btw ': ' by the way ',
        ' tho ': ' though ',
        ' afaik ': ' as far as i know ',
        ' ik ': ' i know ',
        ' idk ': ' i dont know ',
    }
    
    for wrong, right in substitutions.items():
        text = text.replace(wrong, right)
    
    # Remove repeated characters (like 'sooo' -> 'soo')
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    
    return text

def clean_text(text):
    text = preprocess_text(text)
    return text.translate(str.maketrans('', '', string.punctuation))

# Enhanced fuzzy intent detection
def detect_intent(text):
    msg = clean_text(text)
    
    # First check for exact matches for efficiency
    for intent, kws in KEYWORDS_CLEANED.items():
        if any(kw in msg for kw in kws):
            return intent
    
    # Then use fuzzy matching
    best_match = None
    highest_score = 0
    
    # Check the full message first
    for intent, kws in KEYWORDS_CLEANED.items():
        # Find best match in this keyword list using partial ratio
        match, score = process.extractOne(msg, kws, scorer=fuzz.partial_ratio)
        if score > 80 and score > highest_score:  # 80% similarity threshold
            highest_score = score
            best_match = intent
    
    # If no good match found, check individual words
    if not best_match:
        words = msg.split()
        for word in words:
            for intent, kws in KEYWORDS_CLEANED.items():
                match, score = process.extractOne(word, kws, scorer=fuzz.ratio)
                if score > 85 and score > highest_score:
                    highest_score = score
                    best_match = intent
    
    # Special case for subject detection
    for subj in KEYWORDS["subjects"]:
        if subj in msg:
            return "subjects"
    
    return best_match

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

# Response data and keywords
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
    "I'm not sure I have a good answer to that — I'm still learning, just like you. 🌱  \
    But that doesn't mean your question isn't valuable. Sometimes, asking the right question *is* the first step to learning. \
    You might try rephrasing it, or explore with tools like web search, books, or even other AIs. Either way, I'm here to support you, not pretend I know everything. Let's figure it out together. 🤝"
]

}

KEYWORDS = {
    "smart_study": [
    "study smart", "study tips", "effective study", "study strategies",
    "meta learning", "learning how to learn", "smart studying", "study hacks",
    "how to study smart and not hard", "give me some study hacks"
],
    "greetings": ["hello", "hi", "hey", "hiya", "greetings", "what's up", "howdy", "good morning", "good afternoon", "good evening", "sup", "yo"],
    "thanks": ["thank you", "thanks", "thx", "ty", "much appreciated", "many thanks", "grateful", "appreciate it", "thanks a lot", "thank you so much"],
    "farewell": ["goodbye", "bye", "see you", "farewell", "later", "take care", "until next time", "signing off", "talk later", "catch you later", "peace out"],
    "how_are_you": ["how are you", "how's it going", "how do you do", "how have you been", "what's new", "how's life", "how's everything", "how're things"],
    "burnout": ["i'm tired", "burnt out", "no energy", "exhausted", "need a break", "i can't do this anymore", "mentally drained", "burnout", "overwhelmed"],
    "exam_exhaustion": ["studying all day", "study burnout", "exam stress", "too much studying", "i'm done with exams", "no strength left", "exam tired", "exam exhaustion", "exams tiring me"],
    "health_tips": ["health tips", "how to be healthy", "stay fit", "tips for health", "physical health", "mental health", "healthy mind", "health advice"],
    "study_balance": ["study and rest", "study balance", "study too much", "rest time", "overstudying", "balance studying", "study stress", "study fatigue"],
    "night_stress": ["2am", "late night study", "can’t focus", "i'm stuck", "midnight study", "overthinking at night", "late night stress", "can't sleep"],
    "perfectionism": ["perfect", "must be perfect", "i failed", "can’t mess up", "no mistakes allowed", "it has to be right", "perfectionism", "fear of failure"],
    "self_doubt": ["i'm not smart", "i can't do this", "maybe not for me", "not good enough", "i'll fail", "self doubt", "imposter syndrome"],
    "resilience": ["i'll try again", "i will not give up", "i failed but", "bounce back", "resilient", "keep going", "don't give up", "stay strong"],
    "emotion_checkin": ["how do i feel", "check my mood", "emotion check", "status check", "i feel weird", "how am i feeling", "mood check"],
    "daily_review": ["daily review", "today summary", "end of day", "what i did today", "check today", "reflection", "journal", "review day"],
    "set_goal": ["my goal is", "i plan to", "today i want", "i aim to", "goal setting", "set goal", "goal for today"],
    "user_feeling_good": ["i'm good", "great", "happy", "doing well", "awesome", "fine", "fantastic", "wonderful", "excellent", "perfect", "super", "amazing", "terrific"],
    "user_feeling_bad": ["i'm sad", "not good", "tired", "depressed", "down", "exhausted", "stressed", "anxious", "overwhelmed", "frustrated", "awful", "terrible", "horrible", "bad mood"],
    "love": ["i love you", "love you", "luv you", "like you", "adore you", "you're amazing", "you're awesome", "you're great", "you're wonderful", "thanks for being here"],
    "exam_prep": ["exam tips", "study for test", "prepare for exam", "how to study", "exam advice", "test preparation", "studying help", "exam strategies", "test tips", "study techniques", "best way to study", "exam prep"],
    "passed_exam": ["i passed", "i did it", "exam success", "cleared the test", "exam results", "got good marks", "aced the exam", "passed with flying colors", "nailed the test", "killed the exam"],
    "capabilities": ["what can you do", "your abilities", "features", "help me", "what do you offer", "your functions", "what help", "your skills"],
    "introduction": ["introduce", "who are you", "about you", "yourself", "tell me about yourself", "what are you", "your purpose", "your identity"],
    "creator_info": ["who is aylin", "about aylin", "creator info", "who made you", "who created you", "who built you", "who programmed you", "who developed you"],
    "contact_creator": ["how can i contact aylin", "contact aylin", "how to contact", "reach aylin", "get in touch with creator", "aylin's contact", "aylin's info", "reach the maker"],
    "ack_creator": ["thank aylin", "thanks aylin", "thank you aylin", "appreciate aylin", "grateful to aylin", "kudos to aylin", "props to aylin"],
    "subjects": ["math", "physics", "chemistry", "biology", "history", "language", "programming", "literature", "geography", "economics",
                "mathematics", "physic", "chem", "bio", "hist", "lang", "code", "lit", "geo", "econ",
                "algebra", "calculus", "trigonometry", "statistics", "quantum", "mechanics", "thermodynamics",
                "organic", "inorganic", "biochemistry", "genetics", "zoology", "botany", "anatomy",
                "world history", "ancient", "medieval", "modern", "political",
                "english", "spanish", "french", "german", "russian", "linguistics",
                "python", "java", "javascript", "c++", "coding", "web development",
                "poetry", "novel", "drama", "fiction", "shakespeare",
                "physical geography", "human geography", "cartography", "gis",
                "microeconomics", "macroeconomics", "finance", "business"],
    "emotional_support": ["feeling overwhelmed", "need support", "mental health", "emotional help", "feeling stressed", "anxiety", "depression", "emotional support", "feeling down"],
    "growth_mindset": ["growth mindset", "learning from mistakes", "keep growing", "improve myself", "challenge myself", "curious", "embrace failure", "growth", "mindset"],
    "smart_study": ["study smart", "study tips", "effective study", "study strategies", "meta learning", "learning how to learn", "smart studying", "study hacks"],
    "fun_curiosity": ["fun fact", "study joke", "interesting fact", "did you know", "fun trivia", "curiosity", "learning fun", "fun study"],
    "user_reflection": ["reflect", "self reflection", "what did i learn", "how do i feel", "track progress", "self tracking", "reflection", "journal"]

}

def clean_keyword_list(keywords_dict):
    cleaned = {}
    for intent, phrases in keywords_dict.items():
        cleaned[intent] = [p.lower().translate(str.maketrans('', '', string.punctuation)).strip() for p in phrases]
    return cleaned

KEYWORDS_CLEANED = clean_keyword_list(KEYWORDS)

# Streamlit UI
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
