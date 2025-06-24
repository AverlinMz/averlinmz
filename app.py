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

.chat-window { flex-grow: 1; overflow-y: auto; max-height: 60vh; padding: 15px; display: flex; flex-direction: column; gap: 15px; }
.user, .bot { width: 100%; word-wrap: break-word; box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-family: 'Poppins', sans-serif; }
.user { background-color: #D1F2EB; color: #0B3D2E; padding: 12px 16px; border-radius: 18px 18px 4px 18px; align-self: flex-start; }
.bot  { background-color: #EFEFEF; color: #333; padding: 12px 16px; border-radius: 18px 18px 18px 4px; align-self: flex-start; }

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

# Full response data with rich exam prep and new "passed exam" responses
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
        "I provide study strategies, motivation, emotional support, and detailed advice on subjects like Math, Physics, Chemistry, Biology, Computer Science, languages, and more.",
        "I can also help with exam preparation advice, time management techniques, self-assessment quizzes, and fun learning challenges."
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
        "📚 Study Smarter:\n1. Use active recall – quiz yourself often.\n2. Apply spaced repetition – review material over time.\n3. Eliminate distractions – focus on one task at a time.\n4. Teach others – explaining concepts helps retention.\n5. Use visuals – mind maps and charts improve memory.\n6. Rest intentionally – breaks prevent burnout.\nYou've got this! 💪✨",
        "SMART Study Method:\n• Specific: Set clear goals.\n• Measurable: Track your progress.\n• Achievable: Be realistic.\n• Relevant: Focus on important topics.\n• Time-bound: Use deadlines to stay on track.\nTry using this method to boost your efficiency!"
    ],
    "study_plan": [
        "🗓️ Customizable Study Plans:\n- Set realistic goals for each day or week.\n- Include breaks and variety to stay motivated.\n- Review and adjust your plan as you learn more about your pace."
    ],
    "stress_management": [
        "🧘 Stress Management Tips:\n• Practice deep breathing exercises daily.\n• Take short mindfulness breaks every hour.\n• Incorporate light exercise or stretching.\n• Maintain a balanced diet and prioritize sleep."
    ],
    "self_assessment": [
        "✅ Self-Assessment Tips:\n- Quiz yourself with flashcards or practice questions.\n- Reflect on mistakes and identify knowledge gaps.\n- Celebrate small victories to stay motivated."
    ],
    "progress_praise": [
        "🎉 Great job on your progress! Every step forward counts. Keep up the amazing work!",
        "🌟 I’m proud of your effort. Remember, consistency beats perfection."
    ],
    "passed_exam": [
        "🎉 Congratulations on passing your exam! All your hard work paid off — keep shining! 🌟",
        "Awesome news! You passed! That’s a big achievement. Proud of you! 💪",
        "You did it! Passing the exam shows your dedication and skill. Celebrate your success! 🎊"
    ],
    "resources": [
        "📚 Helpful Resources:\n- Khan Academy for foundational lessons.\n- Quizlet for flashcards.\n- Coursera and edX for free university courses.\n- Brilliant.org for interactive STEM challenges."
    ],
    "time_management": [
        "⏰ Time Management Tips:\n- Use the Pomodoro technique (25 min focus + 5 min break).\n- Prioritize tasks using the Eisenhower matrix.\n- Batch similar tasks together to reduce context switching."
    ],
    "learning_styles": [
        "🎨 Learning Style Tips:\n- Visual: Use diagrams and color-coded notes.\n- Auditory: Record and listen to explanations.\n- Kinesthetic: Practice hands-on activities or experiments."
    ],
    "exam_prep": [
        "📖 Ultimate Exam Preparation Guide:\n\n"
        "🧠 Study Strategy:\n"
        "1. Begin preparation 4–6 weeks before the exam.\n"
        "2. Create a subject-wise timetable with specific topics.\n"
        "3. Use active recall – practice with flashcards and past papers.\n"
        "4. Apply spaced repetition – revisit topics at increasing intervals.\n"
        "5. Simulate test conditions: timed sessions, no notes.\n"
        "6. Solve a variety of question types – conceptual, numerical, essay.\n"
        "7. Focus on understanding, not just memorizing.\n\n"

        "⏰ Time Management:\n"
        "1. Use the Pomodoro technique – 25 mins study, 5 mins break.\n"
        "2. Prioritize tasks with the Eisenhower Matrix (urgent vs. important).\n"
        "3. Set clear daily goals – review at the end of the day.\n"
        "4. Break big tasks into small chunks.\n\n"

        "🧘 Stress Management:\n"
        "1. Practice deep breathing or short meditation sessions.\n"
        "2. Take tech-free breaks – walk, stretch, listen to calming music.\n"
        "3. Avoid multitasking – focus brings peace.\n"
        "4. Stay connected – talk to someone when feeling overwhelmed.\n\n"

        "💪 Physical & Mental Health:\n"
        "1. Sleep 7–9 hours per night – memory consolidation happens during sleep.\n"
        "2. Eat brain-friendly foods: nuts, berries, fish, dark chocolate.\n"
        "3. Stay hydrated – even mild dehydration can affect focus.\n"
        "4. Avoid excessive caffeine – balance energy and calm.\n\n"

        "📅 Final Week Checklist:\n"
        "• Revise summaries and high-yield notes.\n"
        "• Don't cram – use light reviews and rest more.\n"
        "• Organize exam materials in advance.\n"
        "• Visualize success – use positive mental rehearsal.\n"
        "• Believe in yourself – you’ve prepared, now trust your brain. 💚"
    ],
    "subjects": {
        "math": (
            "📐 Math Advice & Inspiration:\n\n1. Master fundamental concepts before formulas.\n2. Solve varied problems: algebra, geometry, calculus.\n3. Analyze mistakes: identify pattern, correct approach.\n4. Study proofs to build logical rigor.\n5. Teach solutions aloud or write detailed steps."
        ),
        "physics": (
            "🧲 Physics Advice & Inspiration:\n\n1. Visualize problems: draw force diagrams.\n2. Connect equations to real-world scenarios.\n3. Derive key formulas yourself.\n4. Prioritize conceptual understanding before calculations.\n5. Practice numerical and conceptual questions equally."
        ),
        "chemistry": (
            "⚗️ Chemistry Tips & Inspiration:\n\n1. Learn periodic trends and reaction mechanisms.\n2. Balance equations methodically.\n3. Practice organic reaction pathways step-by-step.\n4. Use molecular models for structure visualization.\n5. Relate theory to lab observations."
        ),
        "biology": (
            "🧬 Biology Strategy & Inspiration:\n\n1. Create detailed labelled diagrams (cell, cycles).\n2. Use flashcards for terminology and processes.\n3. Explain concepts to peers or record yourself.\n4. Relate parts to overall systems.\n5. Study examples of real-life applications."
        ),
        "computer science": (
            "💻 Computer Science Guidance & Inspiration:\n\n1. Practice data structures: arrays, lists, trees.\n2. Master algorithms: sorting, searching, graphs.\n3. Code daily: small challenges build fluency.\n4. Read and debug others’ code.\n5. Document your thought process and solutions."
        )
    },
    "reflection_questions": [
        "🤔 Reflective Questions:\n- What challenged you most today and why?\n- How can you apply this knowledge in real scenarios?\n- What one change could optimize your study routine?"
    ],
    "fun_facts": [
        "🎲 Fun Fact: The human brain processes information at around 120 m/s!",
        "Challenge: Explain today’s topic in 3 sentences or less."
    ],
    "fallback": [
        "Hmm 🤔 I didn’t catch that. Could you rephrase it a bit? I’m here to help! 💬",
        "That’s a tricky one! I'm your learning ally, not a human expert — but I’ll try my best if you reword it a little."
    ]
}

# Keywords dictionary, including new passed exam variants
KEYWORDS = {
    "greetings": ["hello","hi","hey","good morning","good evening"],
    "how_are_you": ["how are you","how're you","how r u","how you doing","how do you do"],
    "user_feeling_good": ["im doing well","i am doing well","im good","i am good","im fine","i am fine","doing great","feeling good","feeling great","all good","im okay","i am okay"],
    "user_feeling_bad": ["im tired","i am tired","im sad","i am sad","burnout","overwhelmed","anxious","stress","not good","bad day","exhausted","frustrated","upset","worried","depressed","unhappy"],
    "love": ["i love you","love you","i adore you","you are awesome","you rock"],
    "introduction": ["who are you","introduce","your name","introduce yourself"],
    "creator_info": ["tell me about your creator","who is your creator","who created you"],
    "ack_creator": ["im your creator","i am your creator","i am aylin","im ur creator"],
    "capabilities": ["what can you do","how can you help","what do you do","what else can you offer","what else you can offer","what else do you offer"],
    "farewell": ["goodbye","bye","see you","see ya"],
    "motivational_quote": ["quote","motivation","inspire","motivate me"],
    "emotional_support": ["tired","sad","burnout","overwhelmed","anxious","stress"],
    "study_tips": ["study smarter","how to study","study plan","study advice","tips for studying"],
    "study_plan": ["study plan","custom study plan","schedule study","study schedule"],
    "stress_management": ["stress management","manage stress","relax","stress relief","calm down"],
    "self_assessment": ["self assessment","self-evaluate","test myself","quiz myself"],
    "progress_praise": ["i did it","i finished","progress","achievement","i succeeded"],
    "passed_exam": ["i passed my exam","i passed the exam","i cleared the exam","i passed","i cleared","passed exam","passed my test","passed test"],
    "resources": ["resources","recommendations","study resources","helpful websites"],
    "time_management": ["time management","pomodoro","manage time","schedule"],
    "learning_styles": ["learning style","visual learner","auditory learner","kinesthetic learner"],
    "exam_prep": ["exam prep","exam preparation","prep advice","give me exam prep advice","preparation","prep","prepation","prep tips","prep for exam","exam prep tips"],
    "subjects": ["math","physics","chemistry","biology","computer science"],
    "reflection_questions": ["reflect","reflection","think about"],
    "fun_facts": ["fun fact","challenge","quiz"]
}

# Text cleaner
def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

# Bot reply logic
def get_bot_reply(user_input):
    msg = clean_text(user_input)
    cleaned = {cat: [clean_text(kw) for kw in kws] for cat, kws in KEYWORDS.items()}

    # Priority intents
    for cat in [
        'passed_exam', 'progress_praise', 'user_feeling_good','user_feeling_bad','love',
        'how_are_you','greetings','exam_prep','capabilities'
    ]:
        if any(kw in msg for kw in cleaned.get(cat, [])):
            return random.choice(RESPONSE_DATA[cat])
    # Subjects detailed
    for subj in cleaned.get('subjects', []):
        if subj in msg and subj in RESPONSE_DATA['subjects']:
            return RESPONSE_DATA['subjects'][subj]
    # Other categories
    for cat, kws in cleaned.items():
        if cat in ['passed_exam', 'progress_praise', 'user_feeling_good','user_feeling_bad','love','how_are_you','greetings','exam_prep','capabilities','subjects']:
            continue
        if cat in RESPONSE_DATA and any(kw in msg for kw in kws):
            return random.choice(RESPONSE_DATA[cat])
    # Fallback
    return random.choice(RESPONSE_DATA['fallback'])

# Chat form & display
with st.form('chat_form', clear_on_submit=True):
    user_input = st.text_input('Write your message…', key='input_field')
    if st.form_submit_button('Send') and user_input.strip():
        # Add user message first
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        # Then add bot reply
        st.session_state.messages.append({'role': 'bot', 'content': get_bot_reply(user_input)})

# Render chat messages with user's messages ABOVE bot's replies
st.markdown('<div class="chat-container"><div class="chat-window">', unsafe_allow_html=True)

# Display all messages in the order: user first, then bot, then user, then bot ...
# But since we append user then bot, the list is: [user, bot, user, bot, ...]
# So we display them as pairs (user above bot)
for i in range(0, len(st.session_state.messages), 2):
    if i < len(st.session_state.messages):
        user_msg = st.session_state.messages[i]['content']
        st.markdown(f'<div class="user">{escape(user_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    if i+1 < len(st.session_state.messages):
        bot_msg = st.session_state.messages[i+1]['content']
        st.markdown(f'<div class="bot">{escape(bot_msg).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
