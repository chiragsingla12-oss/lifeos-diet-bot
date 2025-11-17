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

# --- DAILY MEAL TIMES ---
meal_schedule = {
    "breakfast": "08:30",
    "lunch": "13:00",
    "snack": "17:00",
    "dinner": "18:30"
}

# --- FOOD OPTIONS FOR EACH MEAL ---
def get_food_options(meal):
    if meal == "breakfast":
        return [
            "Moong dal chilla + mint chutney",
            "Upma with veggies",
            "Oats with fruits",
            "Besan chilla",
            "2 multigrain rotis + sabji (no potato)"
        ]
    if meal == "lunch":
        return [
            "2 multigrain rotis + dal + sabji",
            "1 bowl rice + rajma / chole + salad",
            "Khichdi + ghee + curd",
            "Roti + paneer + salad"
        ]
    if meal == "snack":
        return [
            "Fruit bowl",
            "Coconut water",
            "Roasted chana",
            "Peanuts",
            "Curd bowl"
        ]
    if meal == "dinner":
        return [
            "2 rotis + sabji",
            "1 bowl dal + salad",
            "Khichdi",
            "Daliya + veggies"
        ]

# --- SEND REMINDER ---
def send_meal_reminder(chat_id, meal):
    options = get_food_options(meal)
    
    message = f"⏰ *{meal.capitalize()} Reminder!* \nHere are your options:\n"
    for item in options:
        message += f"• {item}\n"

    bot.send_message(chat_id, message, parse_mode="Markdown")

# --- BACKGROUND THREAD FOR AUTOMATIC REMINDERS ---
def scheduler():
    chat_id = None

    while True:
        now = datetime.datetime.now().strftime("%H:%M")

        if chat_id:
            for meal, time_str in meal_schedule.items():
                if now == time_str:
                    send_meal_reminder(chat_id, meal)

        time.sleep(30)

threading.Thread(target=scheduler, daemon=True).start()

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Hello! I'm your personal diet assistant.\n\n"
                     "I will send you reminders before meals and help you choose what to eat.\n\n"
                     "👉 Send me your meal options anytime (like: *Today I have roti, paneer, milk*) "
                     "and I will choose the best one for your goal!",
                     parse_mode="Markdown")

# --- CHAT AI RESPONSE ---
@bot.message_handler(func=lambda m: True)
def chat(message):
    user_text = message.text

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": "You are an expert Indian nutritionist focusing on weight loss and balanced meals."
        },{
            "role": "user",
            "content": user_text
        }]
    )

    reply = completion.choices[0].message["content"]
    bot.send_message(message.chat.id, reply)

bot.infinity_polling()
