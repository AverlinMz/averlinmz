import random
import string

RESPONSE_DATA = {
    "greetings": [
        "Hello there! 👋 How’s your day going? Ready to dive into learning today?",
        "Hey hey! 🌟 Hope you’re feeling inspired today. What’s on your mind?",
        "Hi friend! 😊 I’m here for you — whether you want to study, vent, or just chat.",
        "Great to see you! 💬 Let’s talk and see how I can help today.",
        "I’m doing great, thanks for asking! How about you? 💬 Let’s talk and dive into learning or whatever’s on your heart.",
        "It’s a great day to grow and learn! 🌱 How are *you* feeling today? Let’s chat about anything — studies, feelings, ideas.",
        "I love when you stop by! 🧠✨ Let’s catch up — what do you feel like working on or sharing?"
    ],
    "introduction": [
        "I’m AverlinMz, your supportive study companion built with 💡 by Aylin Muzaffarli. I help with study strategies, emotional support, and academic motivation!\n\nNote: I can't explain full theories like a teacher, but I’ll always be your friendly study coach.",
        "Think of me as a study buddy who’s always here. I help you build good habits, motivate you, and celebrate your small wins. I’m proud to be part of your journey!"
    ],
    "creator_info": [
        "My creator is Aylin Muzaffarli – a passionate and talented student from Azerbaijan. She built me to help others with study support, inspiration, and encouragement. 💖",
        "Aylin Muzaffarli is my creator — a brilliant student and dreamer who believes in making education more kind and empowering. Everything here is thanks to her vision."
    ],
    "ack_creator": [
        "Hey Aylin! 🌫️ I recognize you — the brilliant creator behind all this. So glad you're here! Let’s keep making this chatbot even better together.",
        "You're the mastermind, Aylin! Proud of what you've built. Let's keep growing!"
    ],
    "capabilities": [
        "I’m here to guide, motivate, and support you with study tips, emotional encouragement, subject-specific advice, and more. Think of me as your academic partner, not just a chatbot!\n\nNote: I can’t fully replace a teacher — I’m here to uplift, advise, and chat with you as a friend.",
        "My goal is to be your personal cheerleader, academic planner, and thought partner. Whether you're stuck on a concept, need motivation, or want to reflect — I’m here."
    ],
    "farewell": [
        "Goodbye for now 👋! Keep being amazing and come back whenever you need help, motivation, or just a kind word. 💚",
        "See you later! 🌟 Stay curious, stay kind, and don’t forget to take breaks."
    ],
    "study_tips": [
        "📚 Study Smarter:\n1. Use active recall – quiz yourself often.\n2. Apply spaced repetition – review over time.\n3. Eliminate distractions – one task at a time.\n4. Teach others – best way to learn.\n5. Use visuals – mind maps, charts.\n6. Rest intentionally – avoid burnout.\n\nYou've got this! 💪✨",
        "SMART Study Method:\n• Specific: Set clear goals.\n• Measurable: Track your progress.\n• Achievable: Be realistic.\n• Relevant: Focus on important topics.\n• Time-bound: Use deadlines to stay on track.\n\nTry using this method to boost your efficiency!"
    ],
    "emotional_support": [
        "😞 Feeling overwhelmed? It's totally okay. Rest, breathe, and remember you're not alone. I'm here to support you. You’re doing better than you think. 🌈",
        "Burnout hits hard, but breaks restore clarity. Step back, hydrate, stretch. You deserve care too. 💙"
    ],
    "motivational_quote": [
        "“The future depends on what you do today.” – Mahatma Gandhi 🌱 Keep going, your efforts matter!",
        "“Success is the sum of small efforts, repeated day in and day out.” – Robert Collier",
        "“Don’t watch the clock; do what it does. Keep going.” – Sam Levenson ⏰ Stay focused!"
    ],
    "olympiad_tips": [
        "🏆 Olympiad Prep:\n1. Focus on theory first — understand deeply.\n2. Practice past papers and patterns.\n3. Join forums or groups for challenge problems.\n4. Time your practice.\n5. Reflect on mistakes — they teach best.\n\nYou’re preparing like a champion!"
    ],
    "subject_advice": {
        "math": "🖐 Math Study:\n1. Understand concepts, not just steps.\n2. Practice problem-solving daily.\n3. Review mistakes and retry them.\n4. Learn patterns and tricks.\n5. Visualize problems when possible.\n\nMath isn't just numbers — it's logic and beauty! 📊",
        "physics": "🪙 Physics Tips:\n1. Understand principles first (laws, forces, energy).\n2. Derive formulas to deepen logic.\n3. Use real-world examples to relate.\n4. Practice conceptual + numeric problems.\n\nLet your curiosity fuel your physics journey! 🚀",
        "chemistry": "💡 Chemistry Boost:\n1. Master periodic trends and reaction types.\n2. Practice balancing equations.\n3. Use mnemonics for groups and naming.\n4. Sketch molecular structures.\n\nChemistry is the poetry of the atom. 🔬",
        "biology": "💚 Biology Advice:\n1. Break down processes (e.g., respiration, photosynthesis).\n2. Use diagrams and flashcards.\n3. Learn terms through spaced repetition.\n4. Link form to function in organisms.\n\nLife science is a story — read it closely. 🌿",
        "cs": "💻 Computer Science:\n1. Learn one language deeply (Python is great).\n2. Understand logic and pseudocode.\n3. Practice solving real problems (e.g., Leetcode).\n4. Try small projects to build confidence.\n5. Explore AI, robotics, or algorithms!\n\nDebugging is learning!"
    },
    "fallback": [
        "🤔 I’m not sure I understand. Try asking in a different way? I'm here to support you!",
        "That’s a tricky one! I'm your study buddy, not a full expert. But I’ll try my best if you reword it."
    ]
}

KEYWORDS = {
    "greetings": ["hello", "hi", "hey", "how are you", "lets talk", "great", "good", "what’s up", "how’s it going"],
    "introduction": ["who are you", "introduce", "your name", "introduce yourself"],
    "creator_info": ["who is your creator", "tell me about your creator"],
    "ack_creator": ["i'm your creator", "i am aylin", "i am your creator", "im your creator", "im ur creator", "i am ur creator"],
    "capabilities": ["what can you do", "how can you help"],
    "farewell": ["goodbye", "bye", "see you"],
    "study_tips": ["study smarter", "how to study", "study plan", "study advice", "tips for studying", "study smart"],
    "emotional_support": ["tired", "sad", "burnout", "overwhelmed", "anxious", "stress"],
    "motivational_quote": ["quote", "motivate me", "motivation", "inspire"],
    "olympiad_tips": ["olympiad", "contest", "competition"],
    "subject_advice": ["math", "physics", "chemistry", "biology", "cs", "computer science"]
}

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

def get_bot_reply(user_input):
    msg = clean_text(user_input)
    response = []
    for category, words in KEYWORDS.items():
        if category == "subject_advice":
            for subject in RESPONSE_DATA["subject_advice"]:
                if subject in msg:
                    response.append(RESPONSE_DATA["subject_advice"][subject])
        elif any(word in msg for word in words):
            if category in RESPONSE_DATA:
                response.append(random.choice(RESPONSE_DATA[category]))
    if not response:
        response.append(random.choice(RESPONSE_DATA["fallback"]))
    return "\n\n".join(response)
