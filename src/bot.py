from chat import Tagger

import os
from dotenv import load_dotenv
import telebot

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

national_code = 0
email = ""

tagger = Tagger()


@bot.message_handler(commands=['start'])
def start(message):
    text = "سلام وقت بخیر!\nبه بات پشتیبان مسابقه هوش مصنوعی رایان خوش اومدین!\nلطفا اگر مشکلی براتون به وجود اومده از support\\ استفاده کنید و اگر سوالی در مورد دوره ها دارید ask\\ رو بزنید.\nممنونیم!"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    # bot.register_next_step_handler(msg, handler)


# def handler(message):
#     lang = message.text
#     # bot.reply_to(message, lang)
#     bot.send_message(chat_id=-1002130542303, text=lang)


@bot.message_handler(commands=['support'])
def support(message):
    text = "لطفا کدملی خودتون رو با حروف انگلیسی وارد بفرمایید:"
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, national_code_handler)


def national_code_handler(message):
    global national_code
    national_code = message.text
    text = "و همچنین ایمیلی که با اون توی دوره ثبت نام کردید:"
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, email_handler)


def email_handler(message):
    global email
    email = message.text
    text = "حالا بفرمایید به چه مشکلی برخوردید:"
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, problem_handler)


def problem_handler(message):
    tag = tagger.tag(message.text)
    bot.send_message(os.getenv('SUPPORT_CHANNEL'), str(national_code) + "\n" + str(email) + "\n" + tag)


bot.infinity_polling()
