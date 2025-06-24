def generate_reply(user_msg):
    msg = user_msg.lower()
    if any(greet in msg for greet in ["hey", "hi", "hello", "yo"]):
        return ("Hey! I'm here for you. What are you studying today? "
                "Remember, taking the first step is the hardest but you got this!")
    elif "tired" in msg or "exhausted" in msg:
        return ("It's okay to rest sometimes. Taking a short break can refresh your mind. "
                "Come back stronger and keep pushing forward!")
    elif "sad" in msg or "down" in msg:
        return ("I’m sorry you’re feeling down. Remember, tough times don’t last, "
                "but tough people do. You're stronger than you think.")
    elif "good job" in msg or "well done" in msg:
        return ("Thank you! Your progress inspires me too. Keep up the amazing work, "
                "and don’t forget to celebrate your achievements, big or small!")
    elif "help" in msg:
        return ("I’m here to support you. What do you need help with? "
                "Feel free to share your doubts or questions anytime.")
    elif "creator" in msg or "ok, i m ur creator" in msg:
        return ("Wow! You’re my creator? That’s incredible! Your hard work and passion "
                "will definitely pay off. Keep believing in yourself!")
    else:
        replies = [
            ("Keep going, you're doing great! Every effort you put in shapes your future. "
             "Consistency is the key to success."),
            ("Don't forget to take breaks! Balance is important for long-term productivity. "
             "Stay healthy and motivated."),
            ("Your hard work will pay off! Challenges make you stronger, so keep pushing forward."),
            ("Every step counts! Progress is progress, no matter how small. You're on the right track."),
            ("Believe in yourself! You are capable of amazing things, never doubt your potential.")
        ]
        return random.choice(replies)
