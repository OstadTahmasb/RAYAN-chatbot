from ai import AI

import os
from dotenv import load_dotenv

import telebot

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

ai = AI()


@bot.message_handler(commands=['start'])
def start(message):
    text = "Welcome the the RAYAN AI international contest chatbot! You can ask any questions you have about the contest, in your own language.\nFollow our [official Telegram channel](https://t.me/Rayan_AI_Contest)\nIf you encountered a problem, [contact us](https://t.me/rayanai_info)"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler()
def contest_info_handler(message):
    response = ai.get_contest_info(message.text, message.chat.id)
    bot.send_message(message.chat.id, response)


bot.infinity_polling()
