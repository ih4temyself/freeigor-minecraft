import telebot
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv('API_TOKE52N')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_help(message):
    help_text = "blabalb"
    bot.reply_to(message, help_text)

bot.infinity_polling()
