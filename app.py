import streamlit as st
import random

st.title("AverlinMz - Study Chatbot")

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

def generate_reply(user_msg):
    msg = user_msg.lower()

    # 1) Introduce/creator check (must come first)
    if any(x in msg for x in ["introduce", "who are you", "your name", "about you", "creator", "who made you"]):
        return ("Hello. My name is AverlinMz, your study chatbot 🌱. "
                "My creator is Aylin Muzaffarli, born in 2011 in Azerbaijan. "
                "She's passionate about music, programming, robotics, AI, physics, top universities, and more. "
                "If you have questions, write to: muzaffaraylin@gmail.com 💌. Good luck on your journey!")
    
    # 2) What can you do?
    elif "what can you do" in msg or "what you can do" in msg:
        return ("I’m here to support your studying journey 💡. I can give motivation, advice, and emotional support. "
                "Just chat with me when you need a boost, tips on Olympiad prep, or a friendly ear!")

    # 3) Greetings (without “yo”)
    elif any(greet in msg for greet in ["hey", "hi", "hello"]):
        return ("Hey! I'm here for you. What are you studying today? "
                "Taking the first step is always the hardest — but you've already done it!")

    # 4) Emotional support
    elif any(word in msg for word in ["tired", "exhausted"]):
        return ("It's completely okay to feel tired 😴. Rest is not a weakness — it's a tool. "
                "Take a small break, do some deep breathing, and return refreshed.")
    elif any(word in msg for word in ["sad", "down", "depressed", "crying"]):
        return ("I'm sorry you're feeling that way 💙. Please remember that your emotions are valid, "
                "and you're not alone. Talk to someone if you can — even me. One small step at a time.")
    elif any(word in msg for word in ["anxious", "worried", "panic", "nervous"]):
        return ("Anxiety can be tough, especially when you're aiming high. Try to pause and breathe. "
                "You don't need to do everything at once. Focus on just one next step — you've got this 💪.")

    # 5) Failure & doubt
    elif any(word in msg for word in ["failed", "mistake", "i can't", "gave up"]):
        return ("Failure is just feedback — it's not final. Think of it as part of the learning curve. "
                "Every great person has failed more times than they’ve succeeded. Keep going 🚀.")

    # 6) Celebration & gratitude
    elif any(word in msg for word in ["i did it", "solved it", "success"]):
        return ("Yesss! 🎉 I'm proud of you. You faced the challenge and came out stronger. "
                "Celebrate this moment — you earned it!")
    elif any(word in msg for word in ["good job", "well done"]):
        return ("Thank you! But the real credit goes to you. You’re doing the hard work. "
                "I'm just here to remind you how far you've come 💫.")
    elif any(word in msg for word in ["thank you", "thanks"]):
        return ("You're so welcome 💖. I'm proud of the effort you're putting in. "
                "Never underestimate how far kindness and discipline will take you.")

    # 7) Help
    elif "help" in msg:
        return ("Of course, I’m here to help 🤝. Tell me what you’re struggling with, or how you’re feeling.")

    # 8) Farewells
    elif any(bye in msg for bye in ["goodbye", "bye", "see ya", "see you"]):
        return ("See you soon 👋. Keep doing your best, take care, and come back when you need a boost!")

    # 9) Olympiad advice
    elif "advice" in msg or ("prepare" in msg and "olympiad" in msg):
        return ("Here’s Olympiad advice 💡: Study smart — not just hard. Focus on concepts, not just problems. "
                "Review deeply, prioritize quality over quantity, and don’t compare your pace with others. "
                "Quality of your work = Focus × Time. You've got this!")

    # 10) Productivity & planning
    elif any(word in msg for word in ["consistent", "discipline", "productive"]):
        return ("Discipline beats motivation. Set small goals each day, reflect weekly, "
                "and forgive yourself for bad days. Systems are stronger than moods. Just keep showing up.")
    elif any(word in msg for word in ["break", "rest", "sleep"]):
        return ("Yes — take that break! 🧘‍♀️ Resting recharges your mind and builds stamina. "
                "Even machines need time to cool down. You’re doing the smart thing.")
    elif any(word in msg for word in ["smart", "study plan", "study smarter"]):
        return ("Studying smart means knowing what *not* to focus on. Prioritize what matters, remove distractions, "
                "and take time to reflect. It’s not about hours — it’s about intention.")
    
    # 11) Default motivational replies
    else:
        replies = [
            ("Keep going 💪. You’re doing better than you think. Every small effort matters."),
            ("Progress > Perfection. Take things one step at a time and be kind to yourself."),
            ("Believe in your ability to grow. You’ve already made progress just by showing up."),
            ("You're capable of more than you know 🌟. Keep moving — even if it’s slow."),
            ("It’s okay to struggle. That means you’re growing. Be patient with the process.")
        ]
        return random.choice(replies)

# User input
user_input = st.text_input("Write your message:")

if st.button("Send"):
    if user_input.strip():
        # Prepend messages so newest appear at top
        st.session_state.messages.insert(0, {"bot": generate_reply(user_input)})
        st.session_state.messages.insert(0, {"user": user_input})

# Display conversation (newest first)
for msg in st.session_state.messages:
    if "user" in msg:
        st.markdown(f"**You:** {msg['user']}")
    else:
        st.markdown(f"**Bot:** {msg['bot']}")
