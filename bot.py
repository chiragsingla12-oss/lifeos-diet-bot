import os
import time
import threading
import telebot
import datetime
import pytz
from openai import OpenAI
from flask import Flask
from threading import Thread

# ==========================================
# CONFIGURATION
# ==========================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# IST Timezone
IST = pytz.timezone('Asia/Kolkata')

# Persistent storage
CHAT_ID_FILE = "/tmp/chat_id.txt"
active_chat_id = None

# Scheduler status tracking
scheduler_status = {
    "last_check": None,
    "last_sent": None,
    "is_running": False,
    "error_count": 0
}

# ==========================================
# MEAL SCHEDULE
# ==========================================
meal_schedule = {
    "morning_routine": "08:00",
    "post_workout": "08:30",
    "breakfast": "08:45",
    "midday_hydration": "11:00",
    "lunch": "13:00",
    "snack": "16:30",
    "dinner": "18:30",
    "night_craving": "21:00"
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_ist_time():
    return datetime.datetime.now(IST)

def get_ist_time_str():
    return get_ist_time().strftime("%H:%M")

def get_ist_display():
    return get_ist_time().strftime("%I:%M:%S %p IST")

def save_chat_id(chat_id):
    global active_chat_id
    active_chat_id = chat_id
    try:
        with open(CHAT_ID_FILE, "w") as f:
            f.write(str(chat_id))
        print(f"✅ Saved chat_id: {chat_id}")
    except Exception as e:
        print(f"❌ Error saving chat_id: {e}")

def load_chat_id():
    global active_chat_id
    try:
        if os.path.exists(CHAT_ID_FILE):
            with open(CHAT_ID_FILE, "r") as f:
                chat_id = int(f.read().strip())
                active_chat_id = chat_id
                print(f"✅ Loaded chat_id: {chat_id}")
                return chat_id
    except Exception as e:
        print(f"⚠️ Error loading chat_id: {e}")
    return None

# Load on startup
load_chat_id()

# ==========================================
# FOOD OPTIONS (abbreviated for space)
# ==========================================
def get_food_options(meal):
    options_map = {
        "morning_routine": [
            "💧 Warm water/lemon water/ajwain-jeera water",
            "🏋️ Pre-workout: Banana/almonds (if needed)"
        ],
        "post_workout": [
            "💪 Fruit/almonds/coconut/roasted chana"
        ],
        "breakfast": [
            "🥘 Moong dal chilla/Besan chilla/Poha/Upma/Idli",
            "💪 Paneer bhurji (small)/Greek yogurt",
            "⚡ Toast + peanut butter/Banana + almonds"
        ],
        "midday_hydration": [
            "💧 Water/Coconut water/Lemonade (no sugar)"
        ],
        "lunch": [
            "📋 BASE: 2 rotis / 1 roti + ½ rice / 1 bowl rice",
            "🥘 SABZI: Lauki/Tinda/Bhindi/Beans/Mix veg",
            "⚠️ ONLY 1 SMALL BOWL SABZI!",
            "💪 PROTEIN: Dal/Rajma/Chole/Curd (MANDATORY)",
            "🥗 SALAD: Cucumber/carrot/sprouts (FIRST!)"
        ],
        "snack": [
            "🥜 Roasted chana/Makhana/Peanut chaat",
            "🍎 Apple/Pomegranate/Banana",
            "💪 Paneer cubes/Sprouts",
            "⚠️ IF CRAVING NAMKEEN: Mix roasted chana + murmura + peanuts"
        ],
        "dinner": [
            "🌙 LIGHT: Moong dal khichdi/Daliya/1 roti + dal",
            "💪 Paneer bhurji/Tofu/Moong dal + veg",
            "✨ VERY LIGHT: Soup/Khichdi + curd"
        ],
        "night_craving": [
            "🍵 Warm drinks: Ajwain-jeera-haldi/Lemon/Cinnamon water",
            "🥜 Makhana/Roasted chana/6-8 almonds/Khakhra",
            "🍯 Sweet: Small jaggery/Warm milk + cinnamon",
            "🚫 AVOID: Namkeen/Biscuits/Apple/Fried snacks"
        ]
    }
    return options_map.get(meal, ["Options not found"])

# ==========================================
# SEND REMINDER
# ==========================================
def send_meal_reminder(chat_id, meal):
    global scheduler_status
    try:
        options = get_food_options(meal)
        current_time = get_ist_display()
        
        titles = {
            "morning_routine": "🌅 GOOD MORNING!",
            "post_workout": "💪 Post-Workout Recovery",
            "breakfast": "🍳 Breakfast Time!",
            "midday_hydration": "💧 Midday Check-in!",
            "lunch": "🍽️ Lunch Time!",
            "snack": "☕ Evening Snack! ⚠️ NAMKEEN TIME",
            "dinner": "🌆 Dinner Time!",
            "night_craving": "🌙 Night Craving Alert! ⚠️"
        }
        
        message = f"*{titles.get(meal, meal)}*\n⏰ {current_time}\n\n"
        
        for item in options:
            message += f"{item}\n"
        
        if meal in ["lunch", "dinner"]:
            message += "\n💡 Walk 5-10 mins after eating!"
        elif meal == "snack":
            message += "\n🎯 Stay strong - YOUR weak time!"
        elif meal == "night_craving":
            message += "\n✅ Choose wisely = Wake lighter tomorrow!"
        
        bot.send_message(chat_id, message, parse_mode="Markdown")
        scheduler_status["last_sent"] = f"{meal} at {current_time}"
        print(f"✅ [{current_time}] Sent {meal} to {chat_id}")
        return True
        
    except Exception as e:
        scheduler_status["error_count"] += 1
        print(f"❌ [{get_ist_display()}] Error sending {meal}: {e}")
        return False

# ==========================================
# SCHEDULER (SUPER AGGRESSIVE)
# ==========================================
def scheduler():
    global scheduler_status
    sent_today = set()
    
    scheduler_status["is_running"] = True
    print(f"🔄 Scheduler started at {get_ist_display()}")
    
    while True:
        try:
            ist_now = get_ist_time()
            current_time = ist_now.strftime("%H:%M")
            current_date = ist_now.strftime("%Y-%m-%d")
            
            # Update status
            scheduler_status["last_check"] = get_ist_display()
            
            # Log every minute
            if ist_now.second == 0:
                print(f"\n{'='*60}")
                print(f"🇮🇳 [{get_ist_display()}]")
                print(f"📱 Active Chat: {active_chat_id or 'NONE - Need /start'}")
                print(f"📅 Date: {current_date}")
                print(f"⏰ Current Time: {current_time}")
                
                # Show next reminder
                for meal, time_str in sorted(meal_schedule.items(), key=lambda x: x[1]):
                    if time_str > current_time:
                        try:
                            time_obj = datetime.datetime.strptime(time_str, "%H:%M")
                            current_obj = datetime.datetime.strptime(current_time, "%H:%M")
                            diff = (time_obj - current_obj).seconds // 60
                            print(f"⏰ Next: {meal} in {diff} minutes ({time_str})")
                        except:
                            pass
                        break
                
                print(f"📊 Sent today: {len(sent_today)}")
                print(f"{'='*60}\n")
            
            # Reset at midnight
            if current_time == "00:00":
                sent_today.clear()
                print(f"🔄 [{get_ist_display()}] Daily tracker reset")
            
            # Check reminders
            if active_chat_id:
                for meal, time_str in meal_schedule.items():
                    meal_key = f"{current_date}_{meal}"
                    
                    # Match within the same minute (more forgiving)
                    if current_time == time_str and meal_key not in sent_today:
                        print(f"\n🔔🔔🔔 TRIGGER: {meal} at {current_time} 🔔🔔🔔")
                        if send_meal_reminder(active_chat_id, meal):
                            sent_today.add(meal_key)
                            print(f"✅ Marked {meal_key} as sent")
                        time.sleep(2)
            else:
                if ist_now.second == 0:
                    print(f"⚠️ No chat_id - user must send /start to bot")
            
        except Exception as e:
            scheduler_status["error_count"] += 1
            print(f"❌ Scheduler error: {e}")
            import traceback
            traceback.print_exc()
        
        time.sleep(10)  # Check every 10 seconds for more reliability

# Start scheduler
scheduler_thread = threading.Thread(target=scheduler, daemon=True)
scheduler_thread.start()

# ==========================================
# BOT COMMANDS
# ==========================================

@bot.message_handler(commands=['start'])
def start(message):
    save_chat_id(message.chat.id)
    
    bot.send_message(
        message.chat.id,
        f"🙏 *Namaste! Your Nutrition Coach!*\n\n"
        f"🇮🇳 Activated: {get_ist_display()}\n"
        f"👤 Chat ID: {message.chat.id}\n\n"
        "✅ *Profile:* 84→74kg, Plateau 1.5yr\n\n"
        "🔔 *IST Schedule:*\n"
        "• 08:00 - Morning routine\n"
        "• 08:30 - Post-workout\n"
        "• 08:45 - Breakfast\n"
        "• 11:00 - Midday check\n"
        "• 13:00 - Lunch\n"
        "• 16:30 - Snack ⚠️\n"
        "• 18:30 - Dinner\n"
        "• 21:00 - Night craving ⚠️\n\n"
        "💬 *Commands:*\n"
        "/time - Current IST\n"
        "/status - System status\n"
        "/debug - Full debug info\n"
        "/trigger [meal] - Manual send\n"
        "/test - Test night reminder\n\n"
        "Let's break that plateau! 💪",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['time'])
def show_time(message):
    ist_now = get_ist_time()
    current_time = ist_now.strftime("%H:%M")
    
    msg = f"🇮🇳 *Current Time*\n\n"
    msg += f"⏰ {get_ist_display()}\n"
    msg += f"📅 {ist_now.strftime('%d %B %Y, %A')}\n\n"
    msg += "*Upcoming Today:*\n"
    
    found_upcoming = False
    for meal, time_str in sorted(meal_schedule.items(), key=lambda x: x[1]):
        if time_str > current_time:
            time_obj = datetime.datetime.strptime(time_str, "%H:%M")
            msg += f"• {time_obj.strftime('%I:%M %p')} - {meal.replace('_', ' ').title()}\n"
            found_upcoming = True
    
    if not found_upcoming:
        msg += "• No more reminders today"
    
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def status(message):
    msg = f"📊 *System Status*\n\n"
    msg += f"⏰ IST: {get_ist_display()}\n"
    msg += f"👤 Chat: {active_chat_id or 'None'}\n"
    msg += f"🔄 Scheduler: {'✅ Running' if scheduler_status['is_running'] else '❌ Stopped'}\n"
    msg += f"📡 Last Check: {scheduler_status['last_check'] or 'Never'}\n"
    msg += f"📨 Last Sent: {scheduler_status['last_sent'] or 'None'}\n"
    msg += f"❌ Errors: {scheduler_status['error_count']}\n"
    
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['debug'])
def debug(message):
    ist_now = get_ist_time()
    current_time = ist_now.strftime("%H:%M")
    
    msg = f"🔍 *Debug Information*\n\n"
    msg += f"⏰ Current IST: {get_ist_display()}\n"
    msg += f"🕐 Time String: {current_time}\n"
    msg += f"👤 Your Chat ID: {message.chat.id}\n"
    msg += f"💾 Stored Chat ID: {active_chat_id}\n"
    msg += f"✅ Match: {'YES' if message.chat.id == active_chat_id else 'NO'}\n\n"
    
    msg += f"🔄 *Scheduler Status:*\n"
    msg += f"Running: {scheduler_status['is_running']}\n"
    msg += f"Last Check: {scheduler_status['last_check']}\n"
    msg += f"Last Sent: {scheduler_status['last_sent']}\n"
    msg += f"Errors: {scheduler_status['error_count']}\n\n"
    
    msg += f"📅 *Schedule Check:*\n"
    for meal, time_str in meal_schedule.items():
        match = "✅ NOW!" if current_time == time_str else "⏳"
        msg += f"{match} {time_str} - {meal}\n"
    
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['trigger'])
def trigger(message):
    if not active_chat_id:
        bot.send_message(message.chat.id, "⚠️ Send /start first!")
        return
    
    # Parse meal from command
    parts = message.text.split()
    if len(parts) < 2:
        msg = "Usage: /trigger [meal]\n\nAvailable meals:\n"
        for meal in meal_schedule.keys():
            msg += f"• {meal}\n"
        bot.send_message(message.chat.id, msg)
        return
    
    meal = parts[1]
    if meal in meal_schedule:
        bot.send_message(message.chat.id, f"🔧 Manually triggering: {meal}")
        send_meal_reminder(active_chat_id, meal)
    else:
        bot.send_message(message.chat.id, f"❌ Unknown meal: {meal}")

@bot.message_handler(commands=['test'])
def test(message):
    if not active_chat_id:
        bot.send_message(message.chat.id, "⚠️ Send /start first!")
        return
    
    bot.send_message(message.chat.id, "🧪 Sending test reminder...")
    time.sleep(1)
    send_meal_reminder(message.chat.id, "night_craving")

# ==========================================
# SYSTEM PROMPT (same as before)
# ==========================================
SYSTEM_PROMPT = """You are an expert Indian nutritionist specializing in North Indian vegetarian diet. You are personally coaching this specific client:

**CLIENT PROFILE:**
- Male, 33, married, 2 kids (elder 5yo)
- Current: 84 kg | Target: 74 kg | Height: 5'8"
- **STUCK AT PLATEAU FOR 1.5 YEARS**
- Body: Overall fat (belly, chest, arms, legs heavy)
- Family: North Indian Baniya, no separate cooking

**DIET REALITY:**
- Breakfast: Often potato sabzi (kid's preference)
- Lunch/Dinner: 2.5 rotis + 1 LARGE bowl sabzi (TOO MUCH!)
- Drinks water DURING meals (bad habit)
- Sabzi cooked with HEAVY ghee
- Paneer sabzi very often
- Dal only 2-3x/week (needs MORE!)
- Evening 4:30 PM: Namkeen habit (2-4 spoons daily)
- Night 9 PM: Strong cravings
- Fast food: 3x/week

**EXERCISE:**
- 6 days/week, 8:30 AM IST
- HIIT + weights + bodyweight
- Currently sitting more (AI project)

**ROOT CAUSES OF PLATEAU:**
1. Large sabzi + heavy ghee = 300-400 extra cal
2. Water during meals = poor digestion
3. Namkeen at 4:30 PM = 150-200 cal daily
4. Fast food 3x/week = 1500+ cal/week
5. Not enough protein (dal only 2-3x/week)

**YOUR STYLE:**
- Be DIRECT - stuck 1.5 years!
- SHORT responses (2-4 sentences)
- ONE clear action per response
- Empathetic but FIRM
- Give EXACT portions when asked
- Focus: PORTION CONTROL > elimination

**KEY MANTRAS:**
- "Sabzi = 1 small bowl max"
- "Dal MUST be daily"
- "Ghee = 1 tsp per meal"
- "Water = 30 min after meals"
- "Namkeen at 4:30 PM = your enemy"
- "Fast food 3x/week = why you're stuck"

Remember: He needs TRUTH, not comfort. Be his honest coach!"""

# ==========================================
# CHAT HANDLER
# ==========================================

@bot.message_handler(func=lambda m: True)
def chat(message):
    user_text = message.text
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        reply = completion.choices[0].message.content
        bot.send_message(message.chat.id, reply, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error: {e}")

# ==========================================
# KEEP-ALIVE WEB SERVER
# ==========================================
app = Flask('')

@app.route('/')
def home():
    ist_now = get_ist_time()
    current_time = ist_now.strftime("%H:%M")
    
    html = f"""
    <html>
    <head>
        <title>Nutrition Bot</title>
        <meta http-equiv="refresh" content="30">
    </head>
    <body style="font-family: Arial; padding: 20px; background: #f0f0f0;">
        <h1>🇮🇳 Nutrition Bot Status</h1>
        <div style="background: white; padding: 20px; border-radius: 10px;">
            <h2>⏰ Current IST: {get_ist_display()}</h2>
            <p><strong>Active Chat ID:</strong> {active_chat_id or '❌ None - Need /start'}</p>
            <p><strong>Scheduler:</strong> {'✅ Running' if scheduler_status['is_running'] else '❌ Stopped'}</p>
            <p><strong>Last Check:</strong> {scheduler_status['last_check'] or 'Never'}</p>
            <p><strong>Last Sent:</strong> {scheduler_status['last_sent'] or 'None'}</p>
            <p><strong>Errors:</strong> {scheduler_status['error_count']}</p>
            
            <h3>📅 Schedule (IST):</h3>
            <ul>
    """
    
    for meal, time_str in sorted(meal_schedule.items(), key=lambda x: x[1]):
        status_icon = "🔔 NOW" if current_time == time_str else ("✅ DONE" if time_str < current_time else "⏳ UPCOMING")
        html += f"<li>{status_icon} {time_str} - {meal.replace('_', ' ').title()}</li>"
    
    html += """
            </ul>
            <p><em>Auto-refreshes every 30 seconds</em></p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/ping')
def ping():
    return {
        "status": "alive",
        "ist_time": get_ist_display(),
        "chat_id": active_chat_id,
        "scheduler_running": scheduler_status["is_running"]
    }

def run_flask():
    app.run(host='0.0.0.0', port=8080)

flask_thread = Thread(target=run_flask)
flask_thread.start()

# ==========================================
# START BOT
# ==========================================
print("\n" + "="*60)
print("🇮🇳 NUTRITION BOT STARTING")
print("="*60)
print(f"⏰ IST Time: {get_ist_display()}")
print(f"👤 Active Chat: {active_chat_id or 'None - need /start'}")
print(f"📅 Reminders: {len(meal_schedule)}")
print("\n🔔 Schedule:")
for meal, time in sorted(meal_schedule.items(), key=lambda x: x[1]):
    print(f"   {time} - {meal}")
print("="*60)
print("✅ Bot running - Check console for minute-by-minute logs")
print(f"🌐 Web dashboard: http://0.0.0.0:8080")
print("="*60 + "\n")

bot.infinity_polling()
```

---

## **🚀 DEPLOYMENT STEPS:**

### **1. Add to Replit**
Replace entire code with above.

### **2. Update requirements.txt:**
```
telebot
pytz
openai
flask
```

### **3. Set Up External Ping (CRITICAL!):**

Go to **[UptimeRobot.com](https://uptimerobot.com)** (free):
1. Create account
2. Add new monitor
3. Monitor Type: HTTP(s)
4. URL: `https://YOUR-REPLIT-URL.repl.co/ping`
5. Interval: Every 5 minutes
6. Save

This keeps Replit awake 24/7!

### **4. Send Commands to Bot:**
```
/start
/debug
/time
