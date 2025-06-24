import streamlit as st
import random
import string
from html import escape

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

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

RESPONSE_DATA = {
    "greetings":[
        "Hello there! 👋 How’s your day going? Ready to dive into learning today?",
        "Hey hey! 🌟 Hope you’re feeling inspired today. What’s on your mind?",
        "Hi friend! 😊 I’m here for you — whether you want to study, vent, or just chat."
    ],
    "how_are_you":[
        "I'm doing well, thanks for asking! How about you?",
        "Great! I'm here and ready to help. How are you doing?",
        "I'm fine, thank you! What about you?"
    ],
    "user_feeling_good":[
        "I'm glad to hear you're doing well! Keep up the positive vibes! 😊",
        "That's great! Keep that energy going! 💪",
        "Awesome! Keep shining and learning! 🌟"
    ],
    "user_feeling_bad":[
        "😔 Feeling overwhelmed? It's totally okay. Rest, breathe, and remember you're not alone. I'm here to support you. You’re doing better than you think. 🌈",
        "Burnout hits hard, but breaks restore clarity. Step back, hydrate, stretch. You deserve care too. 💙",
        "It’s normal to feel stuck sometimes. Reflect on your progress and try small steps forward. You’ve got this! 💪"
    ],
    "introduction":[
        "I’m AverlinMz, your supportive study companion built with 💡 by Aylin Muzaffarli. I help with study strategies, emotional support, and academic motivation!\n\nNote: I can't explain full theories like a teacher, but I’ll always be your friendly study coach."
    ],
    "creator_info":[
        "My creator is Aylin Muzaffarli – a passionate and talented student from Azerbaijan. She built me to help others with study support, inspiration, and encouragement. 💖"
    ],
    "ack_creator":[
        "Hey Aylin! 💫 I recognize you — the brilliant creator behind all this. So glad you're here! Let’s keep making this chatbot even better together.",
        "You're the mastermind, Aylin! Proud of what you've built. Let's keep growing!"
    ],
    "capabilities":[
        "I’m here to guide, motivate, and support you with study tips, emotional encouragement, subject-specific advice, and more. Think of me as your academic partner, not just a chatbot!\n\nNote: I can’t fully replace a teacher — I’m here to uplift, advise, and chat with you as a friend.",
        "I provide study strategies, motivation, emotional support, and detailed advice on subjects like Math, Physics, Chemistry, Biology, Computer Science, languages, and more."
    ],
    "farewell":[
        "Goodbye for now 👋! Keep being amazing and come back whenever you need help, motivation, or just a kind word. 💚",
        "See you later! 🌟 Stay curious, stay kind, and don’t forget to take breaks.",
        "Take care! Remember, progress takes time — be patient with yourself."
    ],
    "motivational_quote":[
        "“The future depends on what you do today.” – Mahatma Gandhi 🌱 Keep going, your efforts matter!",
        "“Success is the sum of small efforts repeated day in and day out.” – Robert Collier 🌟 Keep pushing forward!",
        "“Don’t watch the clock; do what it does. Keep going.” – Sam Levenson ⏰ Stay focused!"
    ],
    "emotional_support":[
        "😔 Feeling overwhelmed? It's totally okay. Rest, breathe, and remember you're not alone. I'm here to support you. You’re doing better than you think. 🌈",
        "Burnout hits hard, but breaks restore clarity. Step back, hydrate, stretch. You deserve care too. 💙",
        "It’s normal to feel stuck sometimes. Reflect on your progress and try small steps forward. You’ve got this! 💪"
    ],
    "study_tips":[
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
    "subjects":{
        "math":(
            "📐 Math Advice & Inspiration:\n\n"
            "1. Understand the concept, not just the formula. Dive deep into why something works.\n"
            "2. Practice daily with diverse problems to sharpen your skills.\n"
            "3. When you make mistakes, analyze them carefully — they are your best teachers.\n"
            "4. Study proofs to strengthen logical thinking.\n"
            "5. Explain solutions aloud or write them down as if teaching someone else.\n\n"
            "Math is not just numbers — it’s a way to train your mind to think critically and creatively. Keep challenging yourself, and celebrate every breakthrough! 🌟"
        ),
        "physics":(
            "🧲 Physics Advice & Inspiration:\n\n"
            "1. Master the basics: Newton’s laws, energy, motion — these are the building blocks.\n"
            "2. Draw detailed diagrams to visualize problems.\n"
            "3. Connect theories to real-world phenomena to make learning meaningful.\n"
            "4. Derive formulas yourself instead of rote memorization.\n"
            "5. Solve conceptually first, then crunch numbers.\n\n"
            "Physics is the poetry of the universe — understanding it empowers you to see the world in new light. Stay curious and keep exploring! 🚀"
        ),
        "chemistry":(
            "⚗️ Chemistry Tips & Inspiration:\n\n"
            "1. Memorize key reactions and periodic trends, but understand their significance.\n"
            "2. Balance chemical equations carefully like solving puzzles.\n"
            "3. Use molecular models or drawings to visualize structures.\n"
            "4. Practice reaction mechanisms for deeper insight.\n"
            "5. Link theory with lab experiments to grasp practical applications.\n\n"
            "Chemistry is the science of change — every molecule tells a story. Embrace the adventure of discovery! 🧪"
        ),
        "biology":(
            "🧬 Biology Strategy & Inspiration:\n\n"
            "1. Draw and label diagrams for better recall.\n"
            "2. Teach concepts to others — it solidifies your understanding.\n"
            "3. Use flashcards for vocabulary, cycles, and processes.\n"
            "4. Prioritize understanding over rote memorization.\n"
            "5. Study regularly in small, consistent sessions.\n\n"
            "Biology reveals the story of life — appreciating it deepens your respect for nature and science. Keep your wonder alive! 🌿"
        ),
        "computer science":(
            "💻 Computer Science Guidance & Inspiration:\n\n"
            "1. Master algorithms and data structures — these are your tools.\n"
            "2. Code daily, even small exercises help build muscle memory.\n"
            "3. Break problems into smaller parts to solve step-by-step.\n"
            "4. Read and analyze others’ code for new ideas.\n"
            "5. Document your learning journey and review often.\n\n"
            "Programming teaches problem-solving and creativity — every line of code is a step toward building the future. Keep coding and innovating! 🧠💡"
        ),
        "language":(
            "📝 Language Learning Tips & Inspiration:\n\n"
            "1. Practice speaking regularly — don’t fear mistakes.\n"
            "2. Expand vocabulary daily with flashcards or apps.\n"
            "3. Listen to native speakers and mimic intonation.\n"
            "4. Read varied texts: stories, articles, dialogues.\n"
            "5. Write short paragraphs and get feedback.\n\n"
            "Language opens doors to cultures and new worlds — persistence turns effort into fluency. You can do it! 🌍"
        )
    },
    "study_plan":[
        "🗓️ Customizable Study Plans:\n"
        "Set realistic goals for each day or week.\n"
        "Include breaks and variety to stay motivated.\n"
        "Review and adjust your plan as you learn more about your pace.\n\n"
        "Planning your study helps you avoid last-minute stress and builds steady progress."
    ],
    "stress_management":[
        "🧘 Stress Management Tips:\n"
        "• Take deep breaths and practice mindfulness.\n"
        "• Break tasks into smaller chunks.\n"
        "• Exercise or stretch to release tension.\n"
        "• Keep a balanced diet and sleep well.\n"
        "Remember, your health is your greatest asset."
    ],
    "self_assessment":[
        "✅ Self-Assessment Tips:\n"
        "Quiz yourself regularly to check understanding.\n"
        "Reflect on what you’ve learned and where you need more work.\n"
        "Celebrate small victories to stay motivated."
    ],
    "progress_praise":[
        "🎉 Great job on your progress! Every step forward counts.\nKeep up the amazing work!",
        "🌟 I’m proud of your effort. Remember, consistency beats perfection."
    ],
    "resources":[
        "📚 Helpful Resources:\n"
        "- Khan Academy for many subjects.\n"
        "- Quizlet for flashcards.\n"
        "- Coursera and edX for free courses.\n"
        "- Brilliant.org for STEM challenges."
    ],
    "time_management":[
        "⏰ Time Management:\n"
        "Use techniques like Pomodoro (25 min work + 5 min break).\n"
        "Prioritize important tasks first.\n"
        "Avoid multitasking to boost focus."
    ],
    "learning_styles":[
        "🎨 Learning Style Tips:\n"
        "- Visual learners: use diagrams and colors.\n"
        "- Auditory learners: listen to recordings.\n"
        "- Kinesthetic learners: practice hands-on."
    ],
    "exam_prep":[
        "📖 Exam Preparation Strategies:\n"
        "Start early and review regularly.\n"
        "Practice past exam papers under timed conditions.\n"
        "Focus on weak areas without neglecting strengths."
    ],
    "reflection_questions":[
        "🤔 Reflective Question:\n"
        "What part of today’s study challenged you the most, and why?",
        "How can you apply what you learned to real life?",
        "What one small change can improve your study routine?"
    ],
    "fun_facts":[
        "🎲 Fun Fact:\n"
        "Did you know the human brain can hold about 7±2 pieces of information at once?",
        "Challenge: Try explaining today’s study topic in 3 sentences or less!"
    ],
    "fallback":[
        "Hmm 🤔 I didn’t catch that. Could you rephrase it a bit? I’m here to help! 💬",
        "That’s a tricky one! I'm your learning ally, not a human expert — but I’ll try my best if you reword it a little."
    ]
}

KEYWORDS = {
    "greetings":["hello","hi","hey","good morning","good evening"],
    "how_are_you":["how are you","how're you","how r u","how you doing","how do you do"],
    "user_feeling_good":[
        "i'm doing well", "i am doing well", "im doing well", "i'm good", "i am good", "im good",
        "i'm fine", "i am fine", "im fine", "doing great", "feeling good", "feeling great", "all good",
        "i'm okay", "i am okay", "im okay", "happy", "great", "awesome"
    ],
    "user_feeling_bad":[
        "tired", "sad", "burnout", "overwhelmed", "anxious", "stress", "not good", "bad day",
        "exhausted", "frustrated", "upset", "worried", "depressed", "unhappy", "down", "nervous",
        "i'm tired", "i am tired", "im tired", "i'm sad", "i am sad", "im sad",
        "i'm stressed", "i am stressed", "im stressed", "i'm anxious", "i am anxious", "im anxious",
        "i'm upset", "i am upset", "im upset", "i'm worried", "i am worried", "im worried",
        "i'm exhausted", "i am exhausted", "im exhausted", "i'm frustrated", "i am frustrated", "im frustrated",
        "i'm depressed", "i am depressed", "im depressed", "i'm unhappy", "i am unhappy", "im unhappy"
    ],
    "introduction":["who are you","introduce","your name","introduce yourself"],
    "creator_info":["tell me about your creator","who is your creator","who created you"],
    "ack_creator":["i'm your creator","im your creator","i am your creator","i am aylin","im ur creator","i am ur creator"],
    "capabilities":["what can you do","how can you help","what do you do"],
    "farewell":["goodbye","bye","see you","see ya"],
    "motivational_quote":["quote","motivation","inspire","motivate me"],
    "emotional_support":["tired","sad","burnout","overwhelmed","anxious","stress"],
    "study_tips":["study smarter","how to study","study plan","study advice","tips for studying","study smart"],
    "subjects":["math","physics","chemistry","biology","computer science","cs","language","languages","english","french","spanish"],
    "study_plan":["study plan","custom study plan","schedule study","study schedule"],
    "stress_management":["stress management","manage stress","relax","stress relief","calm down"],
    "self_assessment":["self assessment","self-evaluate","test myself","quiz myself"],
    "progress_praise":["i did it","i finished","progress","achievement","i succeeded"],
    "resources":["resources","recommendations","study resources","helpful websites"],
    "time_management":["time management","pomodoro","manage time","schedule"],
    "learning_styles":["learning style","visual learner","auditory learner","kinesthetic learner"],
    "exam_prep":["exam preparation","prepare for exam","exam tips","test prep"],
    "reflection_questions":["reflect","reflection","think about"],
    "fun_facts":["fun fact","challenge","quiz"]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    
    # Clean keywords for reliable matching
    cleaned_keywords = {cat: [clean_text(kw) for kw in kws] for cat, kws in KEYWORDS.items()}

    # Priority: positive feelings
    if any(kw in msg for kw in cleaned_keywords["user_feeling_good"]):
        return random.choice(RESPONSE_DATA["user_feeling_good"])

    # Then negative feelings
    if any(kw in msg for kw in cleaned_keywords["user_feeling_bad"]):
        return random.choice(RESPONSE_DATA["user_feeling_bad"])

    # How are you
    if any(kw in msg for kw in cleaned_keywords["how_are_you"]):
        return random.choice(RESPONSE_DATA["how_are_you"])

    # Greetings
    if any(kw in msg for kw in cleaned_keywords["greetings"]):
        return random.choice(RESPONSE_DATA["greetings"])

    # Subjects: check keywords then respond with subject advice
    if any(subj in msg for subj in cleaned_keywords["subjects"]):
        for subj_key in RESPONSE_DATA["subjects"]:
            if subj_key in msg:
                return RESPONSE_DATA["subjects"][subj_key]

    # Other categories (excluding ones above)
    for category in KEYWORDS.keys():
        if category in ["user_feeling_good", "user_feeling_bad", "how_are_you", "greetings", "subjects"]:
            continue
        if category in RESPONSE_DATA:
            if any(kw in msg for kw in cleaned_keywords[category]):
                return random.choice(RESPONSE_DATA[category])

    # Fallback
    return random.choice(RESPONSE_DATA["fallback"])

# Streamlit UI
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.markdown('<div class="chat-window">', unsafe_allow_html=True)

for msg in reversed(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f'<div class="user">{escape(msg["content"])}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{escape(msg["content"]).replace("\\n", "<br>")}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

user_input = st.text_input("Write your message here and press Enter or Send:", "")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_response = get_bot_reply(user_input)
    st.session_state.messages.append({"role": "bot", "content": bot_response})
    # Clear input (not possible directly, but user can just overwrite)

    # Rerun to update UI
    st.experimental_rerun()
