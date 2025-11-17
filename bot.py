import os
import time
import threading
import telebot
import datetime
import pytz
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# ==========================================
# 🇮🇳 INDIAN TIMEZONE SETUP
# ==========================================
IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    """Get current time in IST"""
    return datetime.datetime.now(IST)

def get_ist_time_str():
    """Get current IST time as HH:MM string"""
    return get_ist_time().strftime("%H:%M")

def get_ist_display_time():
    """Get current IST time for display (12-hour format)"""
    return get_ist_time().strftime("%I:%M %p IST")

# ==========================================
# PERSISTENT CHAT ID STORAGE
# ==========================================
CHAT_ID_FILE = "/tmp/chat_id.txt"

def save_chat_id(chat_id):
    with open(CHAT_ID_FILE, "w") as f:
        f.write(str(chat_id))
    print(f"✅ Saved chat_id: {chat_id} at {get_ist_display_time()}")

def load_chat_id():
    try:
        if os.path.exists(CHAT_ID_FILE):
            with open(CHAT_ID_FILE, "r") as f:
                chat_id = int(f.read().strip())
                print(f"✅ Loaded chat_id: {chat_id}")
                return chat_id
    except Exception as e:
        print(f"⚠️ Error loading chat_id: {e}")
    return None

# Load chat_id on startup
active_chat_id = load_chat_id()

# ==========================================
# 🍽️ DAILY MEAL SCHEDULE (IST)
# ==========================================
meal_schedule = {
    "morning_routine": "08:00",      # 8:00 AM IST
    "post_workout": "08:30",         # 8:30 AM IST
    "breakfast": "08:45",            # 8:45 AM IST
    "midday_hydration": "11:00",     # 11:00 AM IST
    "lunch": "13:00",                # 1:00 PM IST
    "snack": "16:30",                # 4:30 PM IST
    "dinner": "18:30",               # 6:30 PM IST
    "night_craving": "21:00"         # 9:00 PM IST
}

# ==========================================
# FOOD OPTIONS (same as before)
# ==========================================
def get_food_options(meal):
    
    if meal == "morning_routine":
        hydration = [
            "💧 **STEP 1 - Hydration (Mandatory!):**",
            "• 300ml warm water",
            "• Warm lemon water",
            "• Warm ajwain + jeera water",
            "• Warm water + 1 pinch cinnamon"
        ]
        
        pre_workout = [
            "\n🏋️ **STEP 2 - Pre-Workout Fuel (Only if needed):**",
            "• 1 banana",
            "• 6-8 almonds",
            "• 1 small apple",
            "• 1 tsp peanut butter",
            "• ⏭️ Skip if not feeling low energy"
        ]
        
        return hydration + pre_workout
    
    if meal == "post_workout":
        return [
            "💪 **Post-Workout Mini Meal**",
            "(Keeps energy stable till breakfast)\n",
            "• 1 fruit (apple/banana/orange)",
            "• 8-10 almonds",
            "• Coconut slice",
            "• ½ bowl roasted chana"
        ]
    
    if meal == "breakfast":
        veg_indian = [
            "🥘 **VEG INDIAN OPTIONS:**",
            "• Moong dal chilla (2) + green chutney",
            "• Besan chilla (2) + curd",
            "• Poha with veggies + peanuts (avoid potato)",
            "• Upma with vegetables",
            "• Vegetable daliya",
            "• 2 idli + sambar + chutney",
            "• Stuffed moong dal cheela (paneer ok)"
        ]
        
        protein_boost = [
            "\n💪 **PROTEIN-BOOST OPTIONS:**",
            "• Paneer bhurji (small portion)",
            "• Greek yogurt + fruit + nuts (if available)"
        ]
        
        quick_options = [
            "\n⚡ **QUICK OPTIONS (Busy days):**",
            "• 2 multigrain toast + peanut butter",
            "• Banana + almond combo",
            "• Overnight oats"
        ]
        
        return veg_indian + protein_boost + quick_options
    
    if meal == "midday_hydration":
        return [
            "💧 **HYDRATION:**",
            "• 1 glass water",
            "• 🥥 Coconut water (BEST choice!)",
            "• Lemonade without sugar",
            "\n🍪 **Craving Check:**",
            "If feeling hungry, have 5-6 almonds or wait for lunch!"
        ]
    
    if meal == "lunch":
        base_options = [
            "📋 **BASE (Pick ONE):**",
            "• 2 multigrain rotis",
            "• 1 roti + ½ cup rice",
            "• 1 bowl rice (fist size)",
            "• 2 bajra/jowar rotis"
        ]
        
        sabzi_options = [
            "\n🥘 **SABZI (Pick ONE - avoid potato-only!):**",
            "• Lauki (bottle gourd)",
            "• Tinda (apple gourd)",
            "• Bhindi (okra)",
            "• Beans-carrot mix",
            "• Aloo-gobi (MORE gobi, LESS aloo)",
            "• Mix veg (no potato dominance)",
            "• Palak (spinach)",
            "• Mushroom-paneer 50/50 mix",
            "\n⚠️ **CRITICAL: Only 1 SMALL bowl sabzi, not 1.5 bowls!**"
        ]
        
        protein_options = [
            "\n💪 **PROTEIN (Pick ONE - MANDATORY!):**",
            "• Dal (moong/masoor/toor/arhar)",
            "• Rajma (kidney beans)",
            "• Chole (chickpeas)",
            "• Kala chana (black gram)",
            "• Curd (1 bowl)"
        ]
        
        salad_options = [
            "\n🥗 **SALAD (MANDATORY!):**",
            "• Cucumber + carrot + lemon",
            "• Sprouts salad",
            "• Onion + cucumber + chaat masala",
            "\n💡 **EAT SALAD FIRST!**"
        ]
        
        return base_options + sabzi_options + protein_options + salad_options
    
    if meal == "snack":
        healthy_crunch = [
            "🥜 **HEALTHY CRUNCH:**",
            "• Roasted chana",
            "• Makhana (foxnuts)",
            "• Peanut chaat",
            "• 1 khakhra",
            "• Coconut slices",
            "• Popcorn (homemade, no butter)"
        ]
        
        fruit_options = [
            "\n🍎 **FRUIT OPTIONS:**",
            "• Apple",
            "• Pomegranate",
            "• Banana",
            "• Papaya"
        ]
        
        protein_options = [
            "\n💪 **PROTEIN OPTIONS:**",
            "• Paneer cubes (small bowl)",
            "• Sprouts with lemon",
            "• Moong chaat"
        ]
        
        craving_fix = [
            "\n⚠️ **IF CRAVING NAMKEEN:**",
            "DON'T reach for that namkeen dabba!",
            "Make this instead:",
            "• Mix: roasted chana + murmura + peanuts + onion + lemon",
            "(Healthier, filling, won't sabotage your progress!)"
        ]
        
        return healthy_crunch + fruit_options + protein_options + craving_fix
    
    if meal == "dinner":
        light_options = [
            "🌙 **LIGHT INDIAN (Best for fat loss):**",
            "• Moong dal khichdi + curd",
            "• Daliya + vegetables",
            "• 1 roti + non-potato sabzi + dal",
            "• Palak-paneer 50/50",
            "• Lauki + dal",
            "• Mixed veg + 1 roti"
        ]
        
        protein_options = [
            "\n💪 **HIGH-PROTEIN:**",
            "• Paneer bhurji + salad",
            "• Tofu stir fry (if available)",
            "• Moong dal + mixed veg"
        ]
        
        very_light = [
            "\n✨ **VERY LIGHT (if not hungry):**",
            "• Vegetable soup",
            "• Paneer + salad only",
            "• Khichdi + curd"
        ]
        
        rules = [
            "\n⚠️ **GOLDEN RULES:**",
            "• Keep it LIGHT - no heavy meals",
            "• Less ghee/oil",
            "• Walk 5-10 min after eating"
        ]
        
        return light_options + protein_options + very_light + rules
    
    if meal == "night_craving":
        warm_drinks = [
            "🍵 **WARM DRINKS (BEST choice!):**",
            "• Ajwain-jeera-haldi warm water",
            "• Lemon warm water",
            "• Cinnamon warm water"
        ]
        
        healthy_munch = [
            "\n🥜 **HEALTHY MUNCH (If really hungry):**",
            "• 1 handful makhana",
            "• Roasted chana (small bowl)",
            "• 6-8 almonds",
            "• 1 khakhra"
        ]
        
        sweet_craving = [
            "\n🍯 **SWEET CRAVING:**",
            "• Small piece jaggery",
            "• ½ cup warm milk + cinnamon (no sugar)"
        ]
        
        warning = [
            "\n🚫 **ABSOLUTELY AVOID:**",
            "• Namkeen (your biggest enemy!)",
            "• Biscuits",
            "• Apple (sugar spike at night)",
            "• Any fried snacks"
        ]
        
        motivation = [
            "\n✅ **REMEMBER:**",
            "This is your WEAKEST time!",
            "Choose wisely = Wake up lighter tomorrow!",
            "You've done great all day - don't sabotage it now!"
        ]
        
        return warm_drinks + healthy_munch + sweet_craving + warning + motivation

# ==========================================
# 📨 SEND REMINDER FUNCTION
# ==========================================
def send_meal_reminder(chat_id, meal):
    try:
        options = get_food_options(meal)
        current_time = get_ist_display_time()
        
        if meal == "morning_routine":
            message = f"🌅 *GOOD MORNING!*\n⏰ Time: {current_time}\n\n"
            message += "Your morning routine has 2 steps:\n"
        elif meal == "post_workout":
            message = f"💪 *Post-Workout Recovery*\n⏰ {current_time}\n\n"
            message += "Great job on your workout! Quick refuel:\n"
        elif meal == "breakfast":
            message = f"🍳 *Breakfast Time!*\n⏰ {current_time}\n\n"
            message += "High protein + moderate carbs:\n"
        elif meal == "midday_hydration":
            message = f"💧 *Midday Check-in!*\n⏰ {current_time}\n\n"
            message += "Hydrate + Control cravings:\n"
        elif meal == "lunch":
            message = f"🍽️ *Lunch Time!*\n⏰ {current_time}\n\n"
            message += "⚠️ **GOLDEN RULES:**\n"
            message += "• ½ glass warm water 2 min BEFORE\n"
            message += "• Eat salad FIRST\n"
            message += "• SMALL bowl sabzi (not 1.5!)\n"
            message += "• Only 1-2 sips water DURING\n\n"
        elif meal == "snack":
            message = f"☕ *Evening Snack Time!*\n⏰ {current_time}\n\n"
            message += "⚠️ **HIGH RISK - Namkeen time!**\n"
        elif meal == "dinner":
            message = f"🌆 *Dinner Time!*\n⏰ {current_time}\n\n"
            message += "Keep it LIGHT:\n"
        elif meal == "night_craving":
            message = f"🌙 *Night Craving Alert!*\n⏰ {current_time}\n\n"
            message += "**PREPARE - don't reach for namkeen!**\n\n"
        
        for item in options:
            message += f"{item}\n"
        
        if meal == "lunch" or meal == "dinner":
            message += "\n💡 *Walk 5-10 mins after eating!*"
        elif meal == "snack":
            message += "\n🎯 *Stay strong - YOUR weak time!*"
        
        bot.send_message(chat_id, message, parse_mode="Markdown")
        print(f"✅ [{get_ist_display_time()}] Sent {meal} reminder to {chat_id}")
        
    except Exception as e:
        print(f"❌ [{get_ist_display_time()}] Error sending {meal}: {e}")

# ==========================================
# ⏰ SCHEDULER (IST OPTIMIZED)
# ==========================================
def scheduler():
    global active_chat_id
    sent_today = {}
    last_minute_logged = None
    
    print(f"🔄 Scheduler started at {get_ist_display_time()}")
    
    while True:
        try:
            # Get current IST time
            ist_now = get_ist_time()
            current_time = ist_now.strftime("%H:%M")
            current_date = ist_now.strftime("%Y-%m-%d")
            current_minute = ist_now.strftime("%H:%M")
            
            # Log once per minute (not every 30 seconds)
            if current_minute != last_minute_logged:
                print(f"🇮🇳 [{get_ist_display_time()}] Active Chat: {active_chat_id or 'None - send /start'}")
                last_minute_logged = current_minute
                
                # Show upcoming reminder
                for meal, time_str in meal_schedule.items():
                    if current_time < time_str:
                        time_until = datetime.datetime.strptime(time_str, "%H:%M") - datetime.datetime.strptime(current_time, "%H:%M")
                        mins_until = time_until.seconds // 60
                        if mins_until <= 5:
                            print(f"   ⏰ Next: {meal} in {mins_until} minutes")
                        break
            
            # Reset at midnight IST
            if current_time == "00:00" and "reset" not in sent_today.get(current_date, {}):
                sent_today = {current_date: {"reset": True}}
                print(f"🔄 [{get_ist_display_time()}] Daily tracker reset")
            
            # Check and send reminders
            if active_chat_id:
                for meal, time_str in meal_schedule.items():
                    meal_key = f"{current_date}_{meal}"
                    
                    if current_time == time_str and meal_key not in sent_today:
                        print(f"🔔 [{get_ist_display_time()}] TRIGGERING: {meal}")
                        send_meal_reminder(active_chat_id, meal)
                        sent_today[meal_key] = ist_now
                        time.sleep(2)
            
        except Exception as e:
            print(f"❌ [{get_ist_display_time()}] Scheduler error: {e}")
        
        time.sleep(30)

# Start scheduler
threading.Thread(target=scheduler, daemon=True).start()

# ==========================================
# 🤖 BOT COMMANDS
# ==========================================

@bot.message_handler(commands=['start'])
def start(message):
    global active_chat_id
    active_chat_id = message.chat.id
    save_chat_id(active_chat_id)
    
    bot.send_message(
        message.chat.id,
        f"🙏 *Namaste! Your Nutrition Coach!*\n\n"
        f"🇮🇳 Bot Time: {get_ist_display_time()}\n"
        f"✅ Chat Activated!\n\n"
        "📊 *Your Profile:*\n"
        "• 84 kg → 74 kg goal\n"
        "• Plateau: 1.5 years\n"
        "• Focus: Diabetes prevention\n\n"
        "🔔 *IST Reminder Schedule:*\n"
        "• 8:00 AM - Morning routine\n"
        "• 8:30 AM - Post-workout\n"
        "• 8:45 AM - Breakfast\n"
        "• 11:00 AM - Midday check\n"
        "• 1:00 PM - Lunch\n"
        "• 4:30 PM - Evening snack ⚠️\n"
        "• 6:30 PM - Dinner\n"
        "• 9:00 PM - Night craving ⚠️\n\n"
        "💬 *Commands:*\n"
        "/time - Check IST time\n"
        "/status - Reminder status\n"
        "/test - Test reminder\n"
        "/plan - Full day plan\n\n"
        "Let's break that plateau! 💪",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['time'])
def show_time(message):
    ist_now = get_ist_time()
    
    msg = f"🇮🇳 *Current Time Check*\n\n"
    msg += f"⏰ IST Time: {get_ist_display_time()}\n"
    msg += f"📅 Date: {ist_now.strftime('%d %B %Y')}\n"
    msg += f"📆 Day: {ist_now.strftime('%A')}\n\n"
    
    msg += "*Next Reminders Today:*\n"
    current_time = ist_now.strftime("%H:%M")
    
    for meal, time_str in sorted(meal_schedule.items(), key=lambda x: x[1]):
        if time_str > current_time:
            msg += f"• {time_str} - {meal.replace('_', ' ').title()}\n"
    
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def status(message):
    status_msg = f"📊 *Bot Status*\n\n"
    status_msg += f"🇮🇳 IST Time: {get_ist_display_time()}\n"
    status_msg += f"👤 Chat ID: {message.chat.id}\n"
    status_msg += f"✅ Reminders: {'✓ Active' if active_chat_id else '✗ Inactive'}\n\n"
    
    if active_chat_id:
        status_msg += "*All Scheduled Reminders (IST):*\n"
        for meal, time_str in sorted(meal_schedule.items(), key=lambda x: x[1]):
            # Convert to 12-hour format
            time_obj = datetime.datetime.strptime(time_str, "%H:%M")
            time_12hr = time_obj.strftime("%I:%M %p")
            status_msg += f"• {time_12hr} - {meal.replace('_', ' ').title()}\n"
    else:
        status_msg += "⚠️ Send /start to activate reminders"
    
    bot.send_message(message.chat.id, status_msg, parse_mode="Markdown")

@bot.message_handler(commands=['test'])
def test(message):
    if not active_chat_id:
        bot.send_message(message.chat.id, "⚠️ Send /start first to activate bot!")
        return
    
    bot.send_message(message.chat.id, 
                    f"🧪 *Testing Reminder System*\n\n"
                    f"Current IST: {get_ist_display_time()}\n\n"
                    f"Sending night craving reminder as test...",
                    parse_mode="Markdown")
    time.sleep(1)
    send_meal_reminder(message.chat.id, "night_craving")

@bot.message_handler(commands=['plan'])
def show_plan(message):
    plan = f"""📋 *YOUR DAILY MEAL PLAN*
🇮🇳 Current: {get_ist_display_time()}

🌅 **8:00 AM** - Morning Routine
💪 **8:30 AM** - Post-Workout  
🍳 **8:45 AM** - Breakfast
💧 **11:00 AM** - Midday Check
🍽️ **1:00 PM** - Lunch
☕ **4:30 PM** - Snack ⚠️ HIGH RISK!
🌆 **6:30 PM** - Dinner (Light)
🌙 **9:00 PM** - Night Control ⚠️
😴 **11:00 PM** - Sleep

*All times in IST (Indian Standard Time)*
"""
    bot.send_message(message.chat.id, plan, parse_mode="Markdown")

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
    
    # Dynamic context
    if any(word in user_text.lower() for word in ['craving', 'namkeen', 'junk', 'pizza', 'burger']):
        priority_context = "\n\n🚨 CRAVING - Give immediate alternative + remind this is plateau cause."
    elif any(word in user_text.lower() for word in ['plateau', 'not losing', 'stuck']):
        priority_context = "\n\n🎯 PLATEAU - Address all 5 root causes with numbers."
    elif any(word in user_text.lower() for word in ['aloo', 'potato', 'paneer']):
        priority_context = "\n\n🥘 Give EXACT portion + what to combine."
    elif 'wife made' in user_text.lower() or 'family cooked' in user_text.lower():
        priority_context = "\n\n👨‍👩‍👧 FAMILY MEAL - Give portion strategy, can't change food."
    else:
        priority_context = ""
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT + priority_context
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        reply = completion.choices[0].message.content
        bot.send_message(message.chat.id, reply, parse_mode="Markdown")
    
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error: {str(e)}\n\nTry again!")

# ==========================================
# KEEP-ALIVE SERVER (For Replit)
# ==========================================
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return f"""
    <html>
    <head><title>Nutrition Bot</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🇮🇳 Nutrition Bot is Running!</h1>
        <h2>Current Status:</h2>
        <p><strong>IST Time:</strong> {get_ist_display_time()}</p>
        <p><strong>Active Chat ID:</strong> {active_chat_id or 'None - User needs to send /start'}</p>
        <p><strong>Reminders:</strong> {'✅ Active' if active_chat_id else '❌ Inactive'}</p>
        <h3>Scheduled Reminders (IST):</h3>
        <ul>
        {''.join([f'<li>{time} - {meal.replace("_", " ").title()}</li>' for meal, time in sorted(meal_schedule.items(), key=lambda x: x[1])])}
        </ul>
        <p><em>Refresh this page to see updated time</em></p>
    </body>
    </html>
    """

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# ==========================================
# 🚀 START BOT
# ==========================================
print("=" * 60)
print("🇮🇳 INDIAN NUTRITION BOT STARTING")
print("=" * 60)
print(f"⏰ Current IST Time: {get_ist_display_time()}")
print(f"📅 Scheduled Reminders: {len(meal_schedule)}")
print("\n🔔 Reminder Schedule (IST):")
for meal, time in sorted(meal_schedule.items(), key=lambda x: x[1]):
    time_obj = datetime.datetime.strptime(time, "%H:%M")
    print(f"   {time_obj.strftime('%I:%M %p')} - {meal.replace('_', ' ').title()}")
print(f"\n💾 Chat ID Storage: {CHAT_ID_FILE}")
print(f"🌐 Timezone: Asia/Kolkata (IST)")
print(f"👤 Active Chat: {active_chat_id or 'None - waiting for /start'}")
print("=" * 60)
print("✅ Bot is now running and listening...")
print("=" * 60)

bot.infinity_polling()
```

---

## **🎯 KEY IMPROVEMENTS FOR IST:**

1. **✅ Dedicated IST Functions:**
   - `get_ist_time()` - Always returns IST datetime
   - `get_ist_time_str()` - Returns HH:MM in IST
   - `get_ist_display_time()` - Returns "02:30 PM IST" format

2. **✅ IST Timestamp in Every Message:**
   - Every reminder shows current IST time
   - Example: "⏰ Time: 09:00 PM IST"

3. **✅ New `/time` Command:**
   - Shows current IST time
   - Lists upcoming reminders for today
   - Perfect for verification!

4. **✅ Better Logging:**
   - Console shows IST time with 🇮🇳 emoji
   - Shows countdown to next reminder
   - Easy to verify timezone is correct

5. **✅ Web Dashboard:**
   - Visit your Replit URL
   - See current IST time
   - Check if reminders are active

---

## **📦 REQUIREMENTS.TXT:**
```
telebot
pytz
openai
flask
```

---

## **🧪 HOW TO VERIFY IT'S WORKING:**

### **Step 1: Deploy & Start**
1. Replace code in Replit
2. Send `/start` to your bot

### **Step 2: Check IST Time**
Send this command to bot:
```
/time
```
You should see:
```
🇮🇳 Current Time Check

⏰ IST Time: 09:15 PM IST
📅 Date: 17 November 2024
📆 Day: Monday

*Next Reminders Today:*
- 21:00 - Night Craving
```

### **Step 3: Check Console Logs**
In Replit console, you should see:
```
🇮🇳 [09:15 PM IST] Active Chat: 123456789
   ⏰ Next: night_craving in 45 minutes
```

### **Step 4: Test Reminder**
Send:
```
/test
```
You'll immediately get a test reminder with IST timestamp!

---

## **🔍 DEBUGGING:**

If reminders still don't fire at 9 PM:

1. **Check your console** - Look for:
```
   🇮🇳 [09:00 PM IST] Active Chat: YOUR_CHAT_ID
```

2. **Send `/status`** - Verify reminders show as "Active"

3. **Send `/time`** - Make sure IST time matches your watch

4. **Look for this in console:**
```
   🔔 [09:00 PM IST] TRIGGERING: night_craving
   ✅ [09:00 PM IST] Sent night_craving reminder
