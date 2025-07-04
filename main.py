# import telebot
# from dotenv import load_dotenv
# import os
# from telebot import types

# load_dotenv()
# BOT_TOKEN = os.getenv('API_TOKEN')

# bot = telebot.TeleBot(BOT_TOKEN)

# #START
# @bot.message_handler(commands=['start'])
# def send_help(message):
#     help_text = "Это бот для майнкрафта, выберите команду"
#     bot.reply_to(message, help_text)

# #WEATHER
# @bot.message_handler(commands=['weather'])
# def start(message):
#     markup = types.InlineKeyboardMarkup()
#     markup.add(types.InlineKeyboardButton("clear", callback_data='weather_clear'))
#     markup.add(types.InlineKeyboardButton("rain", callback_data='weather_rain'))
#     markup.add(types.InlineKeyboardButton("thunder", callback_data='weather_thunder'))
#     bot.send_message(message.chat.id, "Выбери опцию:", reply_markup=markup)

# #TIME
# @bot.message_handler(commands=['time'])
# def start(message):
#     markup = types.InlineKeyboardMarkup()
#     markup.add(types.InlineKeyboardButton("clear", callback_data='set_day'))
#     markup.add(types.InlineKeyboardButton("rain", callback_data='set_night'))
#     bot.send_message(message.chat.id, "Выбери опцию:", reply_markup=markup)

# bot.infinity_polling()




import telebot
from dotenv import load_dotenv
import os
from telebot import types
from json_managment import UserManager

load_dotenv()
BOT_TOKEN = os.getenv('API_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

user_manager = UserManager()
last_message_id = {}


@bot.message_handler(commands=['start'])
def send_help(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "unknown"    
    user_manager.check_and_add_user(user_id, username)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("weather", callback_data='option_weather'))
    markup.add(types.InlineKeyboardButton("time", callback_data='option_time'))
    msg = bot.send_message(message.chat.id, "Выберите команду:", reply_markup=markup)
    last_message_id[message.chat.id] = msg.message_id

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    print(user_manager.is_admin(message.from_user.id))
    if user_manager.is_admin(message.from_user.id):
        print(f"admin {message.from_user.id } napisav v bota")
    else: 
        print(f"NE admin {message.from_user.id } napisav v bota")
# Handle callback queries
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == 'option_weather':
        bot.delete_message(chat_id, last_message_id[chat_id])
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("clear", callback_data='weather_clear'))
        markup.add(types.InlineKeyboardButton("rain", callback_data='weather_rain'))
        markup.add(types.InlineKeyboardButton("thunder", callback_data='weather_thunder'))
        msg = bot.send_message(chat_id, "Выберите погоду:", reply_markup=markup)
        last_message_id[chat_id] = msg.message_id
    elif call.data == 'option_time':
        bot.delete_message(chat_id, last_message_id[chat_id])
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("set_day", callback_data='time_set_day'))
        markup.add(types.InlineKeyboardButton("set_night", callback_data='time_set_night'))
        msg = bot.send_message(chat_id, "Выберите время:", reply_markup=markup)
        last_message_id[chat_id] = msg.message_id
    elif call.data.startswith('weather_'):
        bot.delete_message(chat_id, last_message_id[chat_id])
        option = call.data.replace('weather_', '')
        bot.send_message(chat_id, f"Вы успешно выбрали вариант: {option}")
    elif call.data.startswith('time_'):
        bot.delete_message(chat_id, last_message_id[chat_id])
        option = call.data.replace('time_', '')
        bot.send_message(chat_id, f"Вы успешно выбрали вариант: {option}")

bot.infinity_polling()