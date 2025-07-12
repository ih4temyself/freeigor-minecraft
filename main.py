import os

import telebot
from dotenv import load_dotenv
from mcrcon import MCRcon
from telebot import types

from json_managment import UserManager

load_dotenv()

BOT_TOKEN = os.getenv("API_TOKEN")
RCON_PASS = os.getenv("RCON_PASSWORD")
RCON_HOST = "127.0.0.1"
RCON_PORT = 25575

bot = telebot.TeleBot(BOT_TOKEN)
user_manager = UserManager()

last_message_id: dict[int, int] = {}


def mc_command(cmd: str) -> str:
    try:
        with MCRcon(RCON_HOST, RCON_PASS, port=RCON_PORT) as mcr:
            return mcr.command(cmd)
    except Exception as e:
        return f"❌ RCON error: {e}"


COMMANDS: dict[str, str] = {
    "weather_clear": "weather clear",
    "weather_rain": "weather rain",
    "weather_thunder": "weather thunder",
    "time_set_day": "time set day",
    "time_set_night": "time set night",
}


@bot.message_handler(commands=["start"])
def cmd_start(message: telebot.types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "unknown"
    user_manager.check_and_add_user(user_id, username)

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("weather", callback_data="option_weather"))
    kb.add(types.InlineKeyboardButton("time", callback_data="option_time"))

    msg = bot.send_message(message.chat.id, "Выберите команду:", reply_markup=kb)
    last_message_id[message.chat.id] = msg.message_id


@bot.message_handler(commands=["admin"])
def cmd_admin(message: telebot.types.Message):
    if user_manager.is_admin(message.from_user.id):
        print(f"admin {message.from_user.id} написал в бота")
    else:
        print(f"НЕ admin {message.from_user.id} написал в бота")


@bot.callback_query_handler(func=lambda call: True)
def cb_router(call: telebot.types.CallbackQuery):
    chat_id, data = call.message.chat.id, call.data

    if data == "option_weather":
        _swap_keyboard(
            chat_id,
            "Выберите погоду:",
            [
                ("clear", "weather_clear"),
                ("rain", "weather_rain"),
                ("thunder", "weather_thunder"),
            ],
        )

    elif data == "option_time":
        _swap_keyboard(
            chat_id,
            "Выберите время:",
            [("set_day", "time_set_day"), ("set_night", "time_set_night")],
        )

    elif data in COMMANDS:
        bot.delete_message(chat_id, last_message_id.get(chat_id, call.message.id))

        bot.answer_callback_query(call.id, text="⏱ doing…")
        reply = mc_command(COMMANDS[data])
        bot.send_message(chat_id, reply or "ready!")

    else:
        bot.answer_callback_query(call.id, text="Unknown option 🤔")


def _swap_keyboard(chat_id: int, prompt: str, rows: list[tuple[str, str]]):
    bot.delete_message(chat_id, last_message_id.get(chat_id))
    kb = types.InlineKeyboardMarkup()
    for text, cb in rows:
        kb.add(types.InlineKeyboardButton(text, callback_data=cb))
    msg = bot.send_message(chat_id, prompt, reply_markup=kb)
    last_message_id[chat_id] = msg.message_id


if __name__ == "__main__":
    print("Bot is running…")
    bot.infinity_polling()
