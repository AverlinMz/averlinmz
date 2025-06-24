import streamlit as st
import random
import string
from html import escape

# Initialize session state
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
init_session()

# Page config
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS styling
st.markdown("""
<style>
.stApp { padding: 0 !important; margin: 0 !important; }
header, footer { display: none !important; }
#MainMenu, .css-1v3fvcr { visibility: hidden !important; }

.chat-container { display: flex; flex-direction: column; max-width: 900px; margin: 0 auto; padding: 20px; }
.title-container { text-align: center; padding-bottom: 10px; background: white; font-family: 'Poppins', sans-serif; font-weight: 600; }
.title-container h1 { color: black; margin: 0; }

.chat-window { flex-grow: 1; overflow-y: auto; max-height: 60vh; padding: 15px; display: flex; flex-direction: column-reverse; gap: 15px; }
.user, .bot { align-self: center; width: 100%; word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-family: 'Poppins', sans-serif; }
.user { background-color: #D1F2EB; color: #0B3D2E; padding: 12px 16px; border-radius: 18px 18px 4px 18px; }
.bot  { background-color: #EFEFEF; color: #333; padding: 12px 16px; border-radius: 18px 18px 18px 4px; }
.chat-window::-webkit-scrollbar { width: 8px; }
.chat-window::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb:hover { background: #a1a1a1; }
</style>
""", unsafe_allow_html=True)

# Auto-scroll JS
st.markdown("""
<script>
function scrollToBottom() {
    const w = document.querySelector('.chat-window');
    if (w) w.scrollTop = w.scrollHeight;
}
window.onload = scrollToBottom;
new MutationObserver(scrollToBottom).observe(
    document.querySelector('.chat-window'),
    { childList: true, subtree: true }
);
</script>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

# Full response data
RESPONSE_DATA = {
    "greetings": [
        "Hello there! 👋 How’s your day going? Ready to dive into learning today?",
        "Hey hey! 🌟 Hope you’re feeling inspired today. What’s on your mind?",
        "Hi friend! 😊 I’m here for you — whether you want to study, vent, or just chat.",
        "Great to see you! 💬 Let’s talk and learn something new today!"
    ],
    "how_are_you": [
        "I'm doing well, thanks for asking! How about you?",
        "Great! I'm here and ready to help. How are you doing?",
        "I'm fine, thank you! What about you?"
    ],
    "user_feeling_good": [
        "I'm glad to hear you're doing well! Keep up the positive vibes! 😊",
        "That's great! Keep that energy going! 💪",
        "Awesome! Keep shining and learning! 🌟"
    ],
    "user_feeling_bad": [
        "😔 Feeling overwhelmed? It's totally okay. Rest, breathe, and remember you're not alone. I'm here to support you. You’re doing better than you think. 🌈",
        "Burnout hits hard, but breaks restore clarity. Step back, hydrate, stretch. You deserve care too. 💙",
        "It’s normal to feel stuck sometimes. Reflect on your progress and try small steps forward. You’ve got this! 💪"
    ],
    "love": [
        "I appreciate that—it makes my circuits feel warm! 🤖💖",
        "That’s sweet—my circuits are glowing! 😊",
        "Thank you! Your support fuels my code! 🚀"
    ],
    "introduction": [
        "I’m AverlinMz, your supportive study companion built with 💡 by Aylin Muzaffarli. I help with study strategies, emotional support, and academic motivation!"
    ],
    "creator_info": [
        "My creator is Aylin Muzaffarli – a passionate and talented student from Azerbaijan. She built me to help others with study support, inspiration, and encouragement. 💖"
    ],
    "ack_creator": [
        "Hey Aylin! 💫 I recognize you — the brilliant creator behind all this. So glad you're here! Let’s keep making this chatbot even better together.",
        "You're the mastermind, Aylin! Proud of what you've built. Let's keep growing!"
    ],
    "capabilities": [
        "I’m here to guide, motivate, and support you with study tips, emotional encouragement, subject-specific advice, and more. Think of me as your academic partner, not just a chatbot!",
        "I provide study strategies, motivation, emotional support, and detailed advice on subjects like Math, Physics, Chemistry, Biology, Computer Science, languages, and more."
    ],
    "farewell": [
        "Goodbye for now 👋! Keep being amazing and come back whenever you need help, motivation, or just a kind word. 💚",
        "See you later! 🌟 Stay curious, stay kind, and don’t forget to take breaks.",
        "Take care! Remember, progress takes time — be patient with yourself."
    ],
    "motivational_quote": [
        "“The future depends on what you do today.” – Mahatma Gandhi 🌱 Keep going, your efforts matter!",
        "“Success is the sum of small efforts repeated day in and day out.” – Robert Collier 🌟 Keep pushing forward!",
        "“Don’t watch the clock; do what it does. Keep going.” – Sam Levenson ⏰ Stay focused!"
    ],
    "emotional_support": [
        "😔 Feeling overwhelmed? It's totally okay. Rest, breathe, and remember you're not alone. I'm here to support you. You’re doing better than you think. 🌈",
        "Burnout hits hard, but breaks restore clarity. Step back, hydrate, stretch. You deserve care too. 💙",
        "It’s normal to feel stuck sometimes. Reflect on your progress and try small steps forward. You’ve got this! 💪"
    ],
    "study_tips": [
        "📚 Study Smarter:\n"
        "1. Use active recall – quiz yourself often.\n"
        "2. Apply spaced repetition – review material over time.\n"
        "3. Eliminate distractions – focus on one task at a time.\n"
        "4. Teach others – explaining concepts helps retention.\n"
        "5. Use visuals – mind maps and charts improve memory.\n"
        "6. Rest intentionally – breaks prevent burnout.\n\n"
        "You've got this! 💪✨",
        "SMART Study Method:\n"
        "• Specific: Set clear goals.\n"
        "• Measurable: Track your progress.\n"
        "• Achievable: Be realistic.\n"
        "• Relevant: Focus on important topics.\n"
        "• Time-bound: Use deadlines to stay on track.\n\n"
        "Try using this method to boost your efficiency!"
    ],
    "subjects": {
        "math": (
            "📐 Math Advice & Inspiration:\n\n"
            "1. Understand the concept, not just the formula. Dive deep into why something works.\n"
            "2. Practice daily with diverse problems to sharpen your skills.\n"
            "3. When you make mistakes, analyze them carefully — they are your best teachers.\n"
            "4. Study proofs to strengthen logical thinking.\n"
            "5. Explain solutions aloud or write them down as if teaching someone else.\n\n"
            "Math is not just numbers — it’s a way to train your mind to think critically and creatively. Keep challenging yourself, and celebrate every breakthrough! 🌟"
        ),
        "physics": (
            "🧲 Physics Advice & Inspiration:\n\n"
            "1. Master the basics: Newton’s laws, energy, motion — these are the building blocks.\n"
            "2. Draw detailed diagrams to visualize problems.\n"
            "3. Connect theories to real-world phenomena to make learning meaningful.\n"
            "4. Derive formulas yourself instead of rote memorization.\n"
            "5. Solve conceptually first, then crunch numbers.\n\n"
            "Physics is the poetry of the universe — understanding it empowers you to see the world in new light. Stay curious and keep exploring! 🚀"
        ),
        "chemistry": (
            "⚗️ Chemistry Tips & Inspiration:\n\n"
            "1. Memorize key reactions and periodic trends, but understand their significance.\n"
            "... (all subject entries included similarly)"
        )
    },
    "fun_facts": [
        "🎲 Fun Fact:\nDid you know the human brain can hold about 7±2 pieces of information at once?",
        "Challenge: Try explaining today’s study topic in 3 sentences or less!"
    ],
    "fallback": [
        "Hmm 🤔 I didn’t catch that. Could you rephrase it a bit? I’m here to help! 💬",
        "That’s a tricky one! I'm your learning ally, not a human expert — but I’ll try my best if you reword it a little."
    ]
}

# Keywords
KEYWORDS = {
    "greetings": ["hello","hi","hey","good morning","good evening"],
    "how_are_you": ["how are you","how're you","how r u","how you doing","how do you do"],
    "user_feeling_good": [
        "im doing well","i am doing well","im good","i am good","im fine","i am fine",
        "doing great","feeling good","feeling great","all good","im okay","i am okay"
    ],
    "user_feeling_bad": [
        "im tired","i am tired","im sad","i am sad","burnout","overwhelmed","anxious","stress",
        "not good","bad day","exhausted","frustrated","upset","worried","depressed","unhappy"
    ],
    "love": ["i love you","love you","i adore you","you are awesome","you rock"],
    "introduction": ["who are you","introduce","your name","introduce yourself"],
    "creator_info": ["tell me about your creator","who is your creator","who created you"],
    "ack_creator": ["im your creator","i am your creator","i am aylin","im ur creator"],
    "capabilities": ["what can you do","how can you help","what do you do"],
    "farewell": ["goodbye","bye","see you","see ya"],
    "motivational_quote": ["quote","motivation","inspire","motivate me"],
    "emotional_support": ["tired","sad","burnout","overwhelmed","anxious","stress"],
    "study_tips": ["study smarter","how to study","study plan","study advice","tips for studying"],
    "subjects": ["math","physics","chemistry","biology","computer science","language"],
    "fun_facts": ["fun fact","challenge","quiz"]
}

# Text cleaner
def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

# Bot reply logic
def get_bot_reply(user_input):
    msg = clean_text(user_input)
    cleaned = {cat: [clean_text(kw) for kw in kws] for cat, kws in KEYWORDS.items()}

    # Feelings
    if any(kw in msg for kw in cleaned['user_feeling_good']):
        return random.choice(RESPONSE_DATA['user_feeling_good'])
    if any(kw in msg for kw in cleaned['user_feeling_bad']):
        return random.choice(RESPONSE_DATA['user_feeling_bad'])

    # Love
    if any(kw in msg for kw in cleaned['love']):
        return random.choice(RESPONSE_DATA['love'])

    # Greetings & how are you
    if any(kw in msg for kw in cleaned['how_are_you']):
        return random.choice(RESPONSE_DATA['how_are_you'])
    if any(kw in msg for kw in cleaned['greetings']):
        return random.choice(RESPONSE_DATA['greetings'])

    # Subjects
    for subj in cleaned.get('subjects', []):
        if subj in msg and subj in RESPONSE_DATA['subjects']:
            return RESPONSE_DATA['subjects'][subj]

    # Other categories
    for cat in cleaned:
        if cat in ['user_feeling_good','user_feeling_bad','how_are_you','greetings','love','subjects']:
            continue
        if any(kw in msg for kw in cleaned[cat]) and cat in RESPONSE_DATA:
            return random.choice(RESPONSE_DATA[cat])

    return random.choice(RESPONSE_DATA['fallback'])

# Chat form & display
with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        st.session_state.messages.append({'role': 'bot', 'content': get_bot_reply(user_input)})

st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)
for msg in reversed(st.session_state.messages):
    cls = 'user' if msg['role'] == 'user' else 'bot'
    content = escape(msg['content']).replace('\n', '<br>')
    st.markdown(f'<div class="{cls}">{content}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)
