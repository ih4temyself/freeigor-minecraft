import telebot
from dotenv import load_dotenv
import os
from telebot import types

load_dotenv()
BOT_TOKEN = os.getenv('API_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_help(message):
    help_text = "blabalb"
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['weather'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("clear", callback_data='weather_clear'))
    markup.add(types.InlineKeyboardButton("rain", callback_data='weather_rain'))
    markup.add(types.InlineKeyboardButton("thunder", callback_data='weather_thunder'))
    bot.send_message(message.chat.id, "Выбери опцию:", reply_markup=markup)


bot.infinity_polling()