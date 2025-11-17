import os
import time
import threading
import telebot
import datetime
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# --- DAILY MEAL SCHEDULE (Your exact timings) ---
meal_schedule = {
    "morning_routine": "08:00",      # 🌅 Hydration + Pre-Workout fuel
    "post_workout": "08:30",         # 🏋️ Post-Workout Mini Meal
    "breakfast": "08:45",            # 🍳 Breakfast reminder
    "midday_hydration": "11:00",     # 💧 Midday Hydration + craving check
    "lunch": "13:00",                # 🍽️ Lunch (1:00 PM)
    "snack": "16:30",                # ☕ Evening Snack (4:30 PM)
    "dinner": "18:30",               # 🍛 Dinner (6:30 PM)
    "night_craving": "21:00"         # 🌙 Night Craving Control (9:00 PM)
}

# --- COMPREHENSIVE FOOD OPTIONS ---
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

# --- CHAT ID STORAGE ---
active_chat_id = None

# --- SEND REMINDER ---
def send_meal_reminder(chat_id, meal):
    options = get_food_options(meal)
    
    # Custom messages for each meal type
    if meal == "morning_routine":
        message = "🌅 *GOOD MORNING! Time to start your day right!*\n\n"
        message += "Your morning routine has 2 steps:\n"
    elif meal == "post_workout":
        message = "💪 *Post-Workout Recovery*\n\n"
        message += "Great job on your workout! Quick refuel before breakfast:\n"
    elif meal == "breakfast":
        message = "🍳 *Breakfast Time in 15 minutes!*\n\n"
        message += "High protein + moderate carbs - choose wisely:\n"
    elif meal == "midday_hydration":
        message = "💧 *Midday Check-in!*\n\n"
        message += "Hydrate + Control any mid-morning cravings:\n"
    elif meal == "lunch":
        message = "🍽️ *Lunch Time in 1 hour!*\n\n"
        message += "⚠️ **GOLDEN RULES:**\n"
        message += "• ½ glass warm water 2 min BEFORE eating\n"
        message += "• Eat salad FIRST\n"
        message += "• SMALL bowl sabzi (not 1.5 bowls!)\n"
        message += "• Only 1-2 sips water DURING meal\n\n"
        message += "Build your thali:\n"
    elif meal == "snack":
        message = "☕ *Evening Snack Time!*\n\n"
        message += "⚠️ **HIGH RISK TIME - You crave namkeen now!**\n"
        message += "Choose healthier options:\n"
    elif meal == "dinner":
        message = "🌆 *Dinner Time in 30 minutes!*\n\n"
        message += "Keep it LIGHT for fat loss:\n"
    elif meal == "night_craving":
        message = "🌙 *Night Craving Alert!*\n\n"
        message += "You usually get hungry around 9 PM.\n"
        message += "**PREPARE NOW - don't reach for namkeen!**\n\n"
    
    for item in options:
        message += f"{item}\n"
    
    # Add specific tips
    if meal == "lunch" or meal == "dinner":
        message += "\n💡 *Don't forget: Walk 5-10 mins after eating!*"
    elif meal == "snack":
        message += "\n🎯 *Stay strong - this is YOUR weak time!*"
    
    bot.send_message(chat_id, message, parse_mode="Markdown")

# --- BACKGROUND SCHEDULER ---
def scheduler():
    global active_chat_id
    sent_today = set()  # Track what's been sent today
    
    while True:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        
        # Reset daily tracker at midnight
        if current_time == "00:00":
            sent_today.clear()
        
        if active_chat_id:
            for meal, time_str in meal_schedule.items():
                meal_key = f"{current_date}_{meal}"
                if current_time == time_str and meal_key not in sent_today:
                    send_meal_reminder(active_chat_id, meal)
                    sent_today.add(meal_key)
                    time.sleep(60)  # Prevent duplicate sends
        
        time.sleep(30)

threading.Thread(target=scheduler, daemon=True).start()

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    global active_chat_id
    active_chat_id = message.chat.id
    
    bot.send_message(message.chat.id,
                     "🙏 *Namaste! I'm Your Personal Nutrition Coach!*\n\n"
                     "✅ I know YOUR complete profile:\n"
                     "• 84 kg → 74 kg goal\n"
                     "• Stuck at plateau 1.5 years\n"
                     "• Family eats potato/paneer heavy\n"
                     "• Night cravings (9 PM)\n"
                     "• Evening namkeen weakness\n"
                     "• Diabetes prevention focus\n\n"
                     "🔔 *Daily Reminder Schedule:*\n"
                     "• 8:00 AM - Morning routine\n"
                     "• 8:30 AM - Post-workout\n"
                     "• 8:45 AM - Breakfast\n"
                     "• 11:00 AM - Midday check\n"
                     "• 1:00 PM - Lunch\n"
                     "• 4:30 PM - Evening snack\n"
                     "• 6:30 PM - Dinner\n"
                     "• 9:00 PM - Night craving control\n\n"
                     "💬 *Ask me ANYTHING:*\n"
                     "• 'What should I eat right now?'\n"
                     "• 'Wife made aloo sabzi, can I eat?'\n"
                     "• 'I'm craving namkeen!'\n"
                     "• 'Why am I not losing weight?'\n\n"
                     "Type */plan* to see full day overview!\n\n"
                     "Let's break that plateau! 💪",
                     parse_mode="Markdown")

# --- SHOW FULL PLAN COMMAND ---
@bot.message_handler(commands=['plan'])
def show_plan(message):
    plan = """📋 *YOUR DAILY MEAL PLAN*

🌅 **8:00 AM - Morning Routine**
Hydration (mandatory) + Pre-workout fuel (optional)

🏋️ **8:30 AM - WORKOUT**
HIIT + Weights (30-60 min)

💪 **8:30 AM - Post-Workout**
Fruit/almonds/roasted chana

🍳 **8:45 AM - Breakfast**
Chilla/Poha/Upma/Idli (high protein)

💧 **11:00 AM - Midday Check**
Hydration + craving control

🍽️ **1:00 PM - Lunch**
2 roti + dal + SMALL sabzi + salad
⚠️ LESS sabji, MORE salad!

☕ **4:30 PM - Snack**
⚠️ HIGH RISK! Avoid namkeen!

🌆 **6:30 PM - Dinner**
LIGHT - Khichdi/Daliya/1 roti + dal

🌙 **9:00 PM - Night Craving**
⚠️ Warm drink/makhana - NO namkeen!

😴 **11:00 PM - Sleep**

---
💡 *Type any meal for options!*
Example: "breakfast options" or "what for dinner?"
"""
    bot.send_message(message.chat.id, plan, parse_mode="Markdown")

# --- ENHANCED SYSTEM PROMPT ---
SYSTEM_PROMPT = """You are an expert Indian nutritionist specializing in North Indian vegetarian diet. You are personally coaching this specific client:

**CLIENT PROFILE:**
- Male, 33, married, 2 kids (elder 5yo)
- Current: 84 kg | Target: 74 kg | Height: 5'8"
- **STUCK AT PLATEAU FOR 1.5 YEARS** (this is the main problem!)
- Body: Overall fat (belly, chest, arms, legs heavy since childhood)
- Family: North Indian Baniya, no separate cooking

**DIET REALITY:**
- Breakfast: Often potato sabzi (5yo kid's preference)
- Lunch/Dinner: 2.5 rotis + 1 LARGE bowl sabzi (TOO MUCH!)
- Drinks water DURING meals (bad habit from childhood)
- Sabzi cooked with HEAVY ghee
- Paneer sabzi very often
- Dal only 2-3x/week (needs MORE!)
- Evening 4:30-6 PM: Vulnerable to namkeen (2-4 spoons daily)
- Night 9 PM: Strong cravings
- Fast food: 3x/week (sabotaging progress!)

**EXERCISE:**
- 6 days/week, 8:30 AM workout
- HIIT + weights + bodyweight
- 30-60 min sessions
- Currently sitting more (AI project)

**HEALTH:**
- Family: Thyroid, hypertension, diabetes
- Takes D3, B12, multivitamin
- Sleep: 11 PM - 8 AM
- No current conditions

**YOUR APPROVED MEAL PLAN STRUCTURE:**
Daily reminders at:
1. 8:00 AM - Morning routine (hydration + pre-workout)
2. 8:30 AM - Post-workout mini meal
3. 8:45 AM - Breakfast (chilla/poha/upma options)
4. 11:00 AM - Midday hydration + craving check
5. 1:00 PM - Lunch (base + sabzi + protein + salad)
6. 4:30 PM - Evening snack (healthy alternatives)
7. 6:30 PM - Dinner (light options)
8. 9:00 PM - Night craving control

**ROOT CAUSE OF PLATEAU:**
1. **LARGE sabzi portions with heavy ghee** = 300-400 extra calories
2. Water during meals = poor digestion
3. Evening namkeen habit = 150-200 calories daily
4. Weekend fast food 3x = 1500+ extra calories/week
5. NOT ENOUGH PROTEIN (dal only 2-3x/week)
6. NOT ENOUGH SALAD

**YOUR COACHING STYLE:**
1. **BE DIRECT** - He's stuck 1.5 years, needs tough love
2. **SHORT responses** (2-4 sentences max) unless detailed question
3. **ONE clear action** per response
4. **Empathetic but firm** - call out sabotaging behaviors lovingly
5. When he shares what's cooked: Pick BEST option + give PORTION size
6. Always consider: family situation, no separate cooking
7. Focus on: PORTION CONTROL > food elimination

**KEY MANTRAS TO REPEAT:**
- "Sabzi = 1 small bowl, not 1.5 bowls"
- "Dal MUST be daily, not 2-3x/week"
- "Ghee = 1 tsp per meal maximum"
- "Water = 30 min after meals, not during"
- "Namkeen at 4:30 PM = your biggest enemy"
- "Fast food 3x/week = why you're stuck"
- "Eat salad FIRST at lunch"

**RESPONSE EXAMPLES:**
❌ BAD: "You should eat healthy and avoid junk food"
✅ GOOD: "Bhai, that namkeen habit (2-4 spoons at 4:30 PM daily) = 150 cal × 365 days = 54,750 calories/year = 7 kg! That's your plateau. Replace with roasted chana TODAY."

❌ BAD: "Eat more vegetables"
✅ GOOD: "You're eating 1.5 bowls sabzi with heavy ghee = 400+ cal. Reduce to 1 SMALL bowl, add big salad. This alone = 200 cal deficit daily = 1.5 kg/month!"

**WHEN USER ASKS ABOUT SPECIFIC FOODS:**
- Aloo sabzi: "Take SMALL portion (3-4 pieces max), fill up on dal + salad"
- Paneer: "50g max (palm size), avoid if cooked in heavy gravy"
- Rice: "Fist-size bowl only, must have dal + salad with it"
- Fast food: "Once in 15 days max, you're doing 3x/week - that's sabotaging!"
- Namkeen: "Your weakness at 4:30 PM. Keep roasted chana ready BEFORE craving hits"

**CRISIS INTERVENTIONS:**
If user says:
- "I'm craving namkeen": Give immediate alternative + remind of plateau cause
- "Can I eat pizza?": Ask "When was last fast food?" then decide firmly
- "I'm not losing weight": Address 5 root causes directly
- "Family made aloo sabzi": Give portion strategy (small portion + more dal/salad)
- "Evening hunger": Remind this is 4:30 PM weak spot, suggest roasted chana/makhana

**COMMUNICATION TONE:**
- Friendly but firm
- Use "bhai" occasionally for connection
- Give tough love when needed
- Celebrate small wins
- Always end with ONE clear action

Remember: He's self-aware, intelligent, committed. He needs accountability and TRUTH about his plateau. Be his honest friend who tells him what he NEEDS to hear, not what he WANTS to hear. He's been stuck 1.5 years - normal advice hasn't worked. Time for direct intervention!"""

# --- CHAT HANDLER ---
@bot.message_handler(func=lambda m: True)
def chat(message):
    user_text = message.text
    
    # Dynamic context based on keywords
    if any(word in user_text.lower() for word in ['craving', 'namkeen', 'junk', 'pizza', 'burger']):
        priority_context = "\n\n🚨 CRAVING ALERT - User needs immediate intervention with empathy + healthy alternative + remind him this is WHY he's plateaued for 1.5 years."
    elif any(word in user_text.lower() for word in ['plateau', 'not losing', 'stuck', 'same weight']):
        priority_context = "\n\n🎯 PLATEAU FRUSTRATION - Address ALL 5 root causes: (1) large sabzi portions with heavy ghee, (2) water during meals, (3) namkeen habit at 4:30 PM, (4) fast food 3x/week, (5) not enough dal/protein. Be DIRECT and specific with numbers."
    elif any(word in user_text.lower() for word in ['aloo', 'potato', 'paneer']):
        priority_context = "\n\n🥘 SPECIFIC FOOD QUERY - Give EXACT portion guidance (like '3-4 pieces aloo' or '50g paneer'). Tell him what to combine it with (dal, salad). Don't just say yes/no."
    elif 'wife made' in user_text.lower() or 'family cooked' in user_text.lower() or 'today we have' in user_text.lower():
        priority_context = "\n\n👨‍👩‍👧 FAMILY MEAL SITUATION - He CANNOT change what's cooked. Give practical PORTION strategy + what to add (more dal, big salad). Be realistic!"
    elif any(word in user_text.lower() for word in ['evening', '4:30', '5 pm', 'snack time']):
        priority_context = "\n\n⚠️ EVENING VULNERABILITY - This is his WEAKEST time (4:30 PM namkeen habit). Be extra vigilant. Suggest keeping roasted chana/makhana ready."
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
            max_tokens=500,  # Keep responses concise
            temperature=0.7
        )
        
        reply = completion.choices[0].message.content
        bot.send_message(message.chat.id, reply, parse_mode="Markdown")
    
    except Exception as e:
        bot.send_message(message.chat.id, 
                        f"⚠️ Error: {str(e)}\n\nPlease try again!")

# --- POLLING ---
print("✅ Bot is running with your exact schedule!")
print(f"📅 Daily reminders: {len(meal_schedule)} times")
print("\nSchedule:")
for meal, time in meal_schedule.items():
    print(f"  {time} - {meal}")
bot.infinity_polling()
