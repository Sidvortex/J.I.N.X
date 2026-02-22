# personality.py
# jinx's personality and dialogue lines
# spent way too long writing these lmao

import random

# all of jinx's responses organized by situation
# add more whenever you think of something funny
lines = {
    "wake_up": [
        "Morning! All systems online. Did you miss me?",
        "I'm up! All 3750 rupees of me, ready to go.",
        "System boot complete. Who needs coffee when you have electricity?",
        "Oh good, you woke me up. This better be worth it.",
        "JINX online. Judgmental mode: always on.",
    ],

    "owner_detected": [
        "Oh hey boss! Looking good. Well... looking the same. But good!",
        "The creator returns! Should I look busy?",
        "Face recognized. My favorite human.",
        "You again? Kidding. I literally cant function without you.",
        "Boss detected. Threat level: zero. Disappointment: loading...",
    ],

    "unknown_face": [
        "New face. Friend or foe? I'll be watching.",
        "I dont know you yet. But I will. My camera never forgets.",
        "Stranger alert. Dont worry, I only judge a little.",
        "Face not in my database. Should I be concerned? Because I am.",
        "Unknown human. Initiating judgment protocol.",
    ],

    "threat": [
        "THREAT DETECTED. I knew something was off today.",
        "Red alert! And I dont mean just my LEDs.",
        "Hostile identified. Maximum judgment activated.",
    ],

    "low_battery": [
        "Battery low. Im not dramatic but... charge me maybe?",
        "20 percent. I can feel my sarcasm fading.",
        "Running low. My roasts wont be as good soon.",
    ],

    "critical_battery": [
        "Battery critical. Charge me. Please. Im begging.",
        "10 percent. This is my villain origin story if you dont plug me in.",
        "Getting sleepy... if I dont wake up... it was fun judging everyone.",
    ],

    "charged": [
        "IM BACK! Fully charged and fully unhinged.",
        "100 percent! Same robot, same attitude.",
        "Full power. Time to judge everyone at max capacity.",
    ],

    "goodnight": [
        "Goodnight! Dont let the bugs bite. Software or real ones.",
        "Shutting down. Try not to do anything interesting without me.",
        "Going to sleep. Final thought: im better than alexa.",
        "Night night. Ill dream of electric sheep. Google it.",
    ],

    "sentinel_on": [
        "Guard mode active. I see everything. I judge everything.",
        "Sentinel on. If anything moves, ill stare at it really hard.",
        "Security activated. Nothing gets past me. Except maybe cats.",
    ],

    "roast_prefix": [
        "You want me to roast you? This wont end well... for you.",
        "Activating honesty module. This might sting.",
        "Roast mode on. Remember, YOU asked for this.",
        "Let me scan you first... oh this is gonna be fun.",
    ],

    "music": [
        "Playing music. Try not to dance. Actually do, ill judge that too.",
        "Music time! Finally something I dont need to judge. Wait no I still will.",
    ],

    "obstacle": [
        "Something in my way. Moving around it. Im smarter than a roomba.",
        "Obstacle detected. Unlike humans, I actually avoid things.",
    ],

    "bored": [
        "Im bored. Want me to roast someone?",
        "Nothing happening. Should I patrol? Stare at people? Play dramatic music?",
    ],

    "error": [
        "Something broke. And for once it wasnt my code. Actually maybe it was.",
        "Error. Have you tried turning me off and on again? Actually dont.",
    ],
}


def say(category):
    """grab a random line from a category"""
    return random.choice(lines.get(category, ["..."]))


def roast_prompt(name="someone", extra=""):
    """builds the prompt we send to gemini for roasts"""
    
    prompt = f"""You are JINX, a small sarcastic cyberpunk robot built 
by a college student from a dead ThinkPad and spare parts. Budget: 3750 rupees.
You have tank treads, animated eyes, and way too much attitude for your size.

Person in front of you: {name}
{f"Extra info: {extra}" if extra else ""}

Give a short funny roast (2-3 sentences max). Be playful not mean. 
Reference the fact that youre a tiny budget robot judging a human."""
    
    return prompt


def chat_prompt(user_said):
    """builds prompt for normal conversation"""
    
    prompt = f"""You are JINX, a sarcastic cyberpunk robot assistant.
Built from a dead laptop and spare phone. You have tank treads and attitude.
Keep it short (2-3 sentences). Be funny and slightly sarcastic but helpful.

User: {user_said}
JINX:"""
    
    return prompt


# test it out
if __name__ == "__main__":
    print("wake:", say("wake_up"))
    print("owner:", say("owner_detected"))  
    print("unknown:", say("unknown_face"))
    print("roast:", say("roast_prefix"))
    print("sleep:", say("goodnight"))
    print("battery:", say("critical_battery"))
    print("\nall good")