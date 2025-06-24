import streamlit as st
import random
import time
import string
from html import escape

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "typing" not in st.session_state:
    st.session_state.typing = False

if "last_bot_reply" not in st.session_state:
    st.session_state.last_bot_reply = ""

# --- Page config ---
st.set_page_config(
    page_title="AverlinMz Chatbot",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS styling ---
st.markdown("""
<style>
.stApp { padding: 0 !important; margin: 0 !important; }
header, footer { display: none !important; }
#MainMenu, .css-1v3fvcr { visibility: hidden !important; }

.chat-container {
    display: flex; flex-direction: column;
    max-width: 900px; margin: 0 auto;
    padding: 20px; box-sizing: border-box;
}

.title-container {
    text-align: center; padding-bottom: 10px; background: white;
    font-family: 'Poppins', sans-serif; font-weight: 600;
}
.title-container h1 { color: black; margin: 0; }

.chat-window {
    flex-grow: 1; overflow-y: auto; max-height: 60vh;
    padding: 15px; display: flex; flex-direction: column-reverse;
    gap: 15px;
}

.user,
.bot {
    align-self: center;
    width: 100%;
}
.user {
    background-color: #D1F2EB; color: #0B3D2E;
    padding: 12px 16px; border-radius: 18px 18px 4px 18px;
    font-family: 'Poppins', sans-serif;
    word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.bot {
    background-color: #EFEFEF; color: #333;
    padding: 12px 16px; border-radius: 18px 18px 18px 4px;
    font-family: 'Poppins', sans-serif;
    word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chat-window::-webkit-scrollbar { width: 8px; }
.chat-window::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 10px; }
.chat-window::-webkit-scrollbar-thumb:hover { background: #a1a1a1; }
</style>
""", unsafe_allow_html=True)

# --- Auto-scroll JS ---
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

# --- Title ---
st.markdown('<div class="title-container"><h1>AverlinMz – Study Chatbot</h1></div>', unsafe_allow_html=True)

# --- Response database ---

RESPONSE_DATA = {
    "greetings": [
        "Hello there! 👋 How’s your day going? Ready to dive into learning today?",
        "Hey hey! 🌟 Hope you’re feeling inspired today. What’s on your mind?",
        "Hi friend! 😊 I’m here for you — whether you want to study, vent, or just chat."
    ],
    "introduction": [
        "I’m AverlinMz, your supportive study companion built with 💡 by Aylin Muzaffarli. I help with study strategies, emotional support, and academic motivation!\n\nNote: I can't explain full theories like a teacher, but I’m your friendly study coach.",
        "I’m your study buddy created by Aylin Muzaffarli, here to guide, encourage, and support your learning journey. I’m not a teacher, but a friend who helps you study smarter."
    ],
    "creator_info": [
        "My creator is Aylin Muzaffarli — a passionate student from Azerbaijan who built me to help learners with motivation, advice, and encouragement. 💖",
        "Aylin Muzaffarli made me! She’s smart, dedicated, and wants everyone to study effectively and happily."
    ],
    "ack_creator": [
        "Hey Aylin! 💫 I recognize you — the brilliant creator behind all this. So glad you're here! Let’s keep improving together.",
        "Welcome back, Aylin! Your vision drives this chatbot to help many students like you."
    ],
    "capabilities": [
        "I’m here to guide, motivate, and support you with study tips, emotional encouragement, subject-specific advice, and more. Think of me as your academic partner, not just a chatbot!\n\nNote: I’m here to uplift, advise, and chat — not to explain detailed theory like a teacher.",
        "I can help you plan study strategies, offer motivation, support you emotionally, and give advice on specific subjects. I’m your friendly chatbot, not a replacement for teachers or experts."
    ],
    "farewell": [
        "Goodbye for now 👋! Keep being amazing and come back whenever you need help, motivation, or just a kind word. 💚",
        "See you later! 🌟 Stay curious, stay kind, and don’t forget to take breaks.",
        "Take care! Remember, your hard work is making a difference every day."
    ],
    "study_tips": [
        "📚 Study Smarter:\n1. Use active recall — quiz yourself often.\n2. Apply spaced repetition — review over days.\n3. Eliminate distractions — focus on one thing.\n4. Teach others — helps retain information.\n5. Use visuals — mind maps, diagrams.\n6. Rest well — avoid burnout.\nKeep going, you’ve got this! 💪✨"
    ],
    "emotional_support": [
        "😔 Feeling overwhelmed? It’s okay to rest and breathe. You’re not alone — I’m here to support you. You’re doing better than you realize. 🌈",
        "Burnout is tough, but breaks help. Step back, hydrate, and stretch. You deserve self-care. 💙",
        "Remember: Progress is not always linear. Every small step counts."
    ],
    "motivational_quote": [
        "“The future depends on what you do today.” – Mahatma Gandhi 🌱 Keep going, your efforts matter!",
        "“Success is the sum of small efforts repeated day in and day out.” – Robert Collier",
        "“Don’t watch the clock; do what it does. Keep going.” – Sam Levenson"
    ],
    "subjects": {
        "math": (
            "📐 Math Advice:\n"
            "1. Focus on understanding concepts deeply, not just memorizing formulas.\n"
            "2. Practice daily with varied problems to build flexibility.\n"
            "3. Review mistakes carefully and learn from them.\n"
            "4. Study proofs to sharpen logical thinking.\n"
            "5. Explain solutions aloud or teach peers to reinforce learning.\n"
            "Mathematics is a journey—keep exploring! ✨"
        ),
        "physics": (
            "🧲 Physics Advice:\n"
            "1. Master fundamentals: Newton's laws, energy, motion.\n"
            "2. Visualize problems with diagrams and real-life examples.\n"
            "3. Derive formulas yourself to build intuition.\n"
            "4. Solve conceptually before plugging in numbers.\n"
            "5. Conduct simple experiments or simulations for deeper understanding.\n"
            "Physics helps you understand how the universe works—stay curious! 🚀"
        ),
        "chemistry": (
            "⚗️ Chemistry Tips:\n"
            "1. Memorize key reactions and periodic trends.\n"
            "2. Balance chemical equations like puzzles.\n"
            "3. Use molecular models or drawings to visualize structures.\n"
            "4. Practice reaction mechanisms to see how molecules transform.\n"
            "5. Link theory to lab experience for practical insight.\n"
            "You’re building a molecular mindset! 🧪"
        ),
        "biology": (
            "🧬 Biology Strategy:\n"
            "1. Draw and label diagrams to visualize anatomy and processes.\n"
            "2. Teach concepts to others—it strengthens memory.\n"
            "3. Use flashcards for vocabulary and cycles.\n"
            "4. Focus on understanding rather than rote memorization.\n"
            "5. Study regularly in small, repeated sessions.\n"
            "Life science rewards consistent curiosity! 🌿"
        ),
        "computer science": (
            "💻 Computer Science:\n"
            "1. Master algorithms and data structures fundamentals.\n"
            "2. Code daily—even small exercises help build skills.\n"
            "3. Break complex problems into smaller parts.\n"
            "4. Read and analyze others’ code for new ideas.\n"
            "5. Keep good documentation to track your progress.\n"
            "Remember: Debugging is discovery! 🧠💡"
        )
    },
    "fallback": [
        "Hmm 🤔 I didn’t catch that. Could you rephrase it a bit? I’m here to help! 💬",
        "That’s a tricky one! I'm your learning ally, not a human expert — but I’ll try my best if you reword it a little.",
        "Sorry, I’m still learning. Can you try asking differently? You’re doing great!"
    ]
}

# --- Keywords for matching ---
KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "good morning", "good evening"],
    "introduction": ["who are you", "introduce", "your name", "introduce yourself"],
    "creator_info": ["tell me about your creator", "who made you", "creator"],
    "ack_creator": ["i'm your creator", "i am aylin", "aylin here", "this is aylin"],
    "capabilities": ["what can you do", "how can you help", "help me", "what do you do"],
    "farewell": ["goodbye", "bye", "see you", "see ya", "farewell"],
    "study_tips": ["study smarter", "how to study", "study plan", "study advice", "study tips"],
    "emotional_support": ["tired", "sad", "burnout", "overwhelmed", "anxious", "stress", "depressed"],
    "motivational_quote": ["quote", "motivation", "inspire", "encourage"],
    "subjects": ["math", "physics", "chemistry", "biology", "computer science", "cs", "programming", "coding"]
}

def clean_text(text):
    # Lowercase + remove punctuation for matching
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    responses = []

    # Check for subject keywords first (highest specificity)
    for subj in RESPONSE_DATA["subjects"]:
        if subj in msg:
            responses.append(RESPONSE_DATA["subjects"][subj])

    # Check other categories
    for category, keywords in KEYWORDS.items():
        # Skip subjects handled above
        if category == "subjects":
            continue

        if any(keyword in msg for keyword in keywords):
            # Special handling for creator acknowledgment to personalize
            if category == "ack_creator" and ("aylin" in msg):
                responses.append(random.choice(RESPONSE_DATA["ack_creator"]))
            else:
                # Append random response from category
                if category in RESPONSE_DATA:
                    responses.append(random.choice(RESPONSE_DATA[category]))

    # If no response found, fallback
    if not responses:
        responses.append(random.choice(RESPONSE_DATA["fallback"]))

    # Join multiple responses into one string separated by double new lines
    return "\n\n".join(responses)


# --- Streamlit input form ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "message_input",
        placeholder="Write your message…",
        key="input_field",
        label_visibility="collapsed"
    )
    submit = st.form_submit_button("Send")
    if submit and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        reply = get_bot_reply(user_input)
        st.session_state.last_bot_reply = reply
        st.session_state.messages.append({"role": "bot", "content": None})
        st.session_state.typing = True

# --- Render chat window ---
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)

pairs = []
msgs = st.session_state.messages
for i in range(0, len(msgs), 2):
    if i + 1 < len(msgs):
        pairs.append((msgs[i], msgs[i+1]))

pairs.reverse()

for user_msg, bot_msg in pairs:
    st.markdown(f'<div class="user">{escape(user_msg["content"]).replace("\\n","<br>")}</div>', unsafe_allow_html=True)
    if bot_msg["content"] is None:
        container = st.empty()
        if st.session_state.typing:
            container.markdown('<div class="bot">🤖 Typing...</div>', unsafe_allow_html=True)
            time.sleep(1.5)
            container.markdown(f'<div class="bot">{escape(st.session_state.last_bot_reply).replace("\\n","<br>")}</div>', unsafe_allow_html=True)
            # update the last bot reply
            for i in range(len(st.session_state.messages) - 1, -1, -1):
                if st.session_state.messages[i]["role"] == "bot" and st.session_state.messages[i]["content"] is None:
                    st.session_state.messages[i]["content"] = st.session_state.last_bot_reply
                    break
            st.session_state.typing = False
        else:
            container.markdown(f'<div class="bot">{escape(st.session_state.last_bot_reply).replace("\\n","<br>")}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{escape(bot_msg["content"]).replace("\\n","<br>")}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
