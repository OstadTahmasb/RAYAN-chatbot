from ai import AI

import os
from dotenv import load_dotenv

import telebot
from telebot.types import ReplyKeyboardMarkup

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

national_code = 0
email = ""

ai = AI()

info_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
info_keyboard.add("دوره های آموزشی", "مسابقه")


@bot.message_handler(commands=['start'])
def start(message):
    text = "سلام وقت بخیر!\nبه بات پشتیبان مسابقه هوش مصنوعی رایان خوش اومدین!\nلطفا اگر مشکلی براتون به وجود اومده از /support استفاده کنید و اگر سوالی در مورد دوره ها یا مسابقه دارید /info رو بزنید.\nممنونیم!"
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
    bot.register_next_step_handler(msg, national_code_getter)


def national_code_getter(message):
    global national_code
    national_code = message.text
    text = "و همچنین ایمیلی که با اون توی دوره ثبت نام کردید:"
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, email_getter)


def email_getter(message):
    global email
    email = message.text
    text = "حالا بفرمایید به چه مشکلی برخوردید:"
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, problem_handler)


def problem_handler(message):
    tag = ai.tag(message.text)
    bot.send_message(os.getenv('SUPPORT_CHANNEL'),
                     str(message.chat.id) + '\n' + str(national_code) + '\n' + str(email) + '\n' + tag)
    text = "ممنونم! مشکل شما ثبت شد. همکارانم در پشتیبانی به زودی به اون رسیدگی خواهند کرد و نتیجه همینجا به شما اعلام می شود."
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['info'])
def info(message):
    text = "در رابطه با کدوم مورد سوال دارید؟ از بین دو گزینه زیر انتخاب کنید:"
    msg = bot.reply_to(message, text, reply_markup=info_keyboard)
    bot.register_next_step_handler(msg, info_classifier)


def info_classifier(message):
    text = "سوالتون رو بفرمایید:"
    msg = bot.send_message(message.chat.id, text)
    if message.text == "مسابقه":
        print("contest")
        bot.register_next_step_handler(msg, contest_info_handler)
    else:
        print("course")
        bot.register_next_step_handler(msg, courses_info_handler)


def contest_info_handler(message):
    print(message)
    response = ai.get_contest_info(message.text)
    print(response)
    bot.send_message(message.chat.id, response['response'])


def courses_info_handler(message):
    print(message)
    response = ai.get_courses_info(message.text)
    print(response)
    bot.send_message(message.chat.id, response['response'])


bot.infinity_polling()
