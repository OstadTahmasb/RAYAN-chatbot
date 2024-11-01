from ai import AI

import os
from dotenv import load_dotenv

import telebot
from telebot.types import ReplyKeyboardMarkup

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

ai = AI()


@bot.message_handler(commands=['start'])
def start(message):
    text = "Welcome the the RAYAN AI international contest chatbot! You can ask any questions you have about the contest, in your own language.\nFollow our [official Telegram channel](https://t.me/Rayan_AI_Contest)\nIf you encountered a problem, [contact us](https://t.me/rayanai_info)"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

#
# @bot.message_handler(commands=['support'])
# def support(message):
#     text = "لطفا کدملی خودتون رو با حروف انگلیسی وارد بفرمایید:"
#     msg = bot.send_message(message.chat.id, text)
#     data = {"chat_id": message.chat.id, "national_id": 0, "email": "a", "problem": "a"}
#     bot.register_next_step_handler(msg, national_code_getter, data)
#
#
# def national_code_getter(message, data):
#     data['national_id'] = message.text
#     text = "و همچنین ایمیلی که با اون توی دوره ثبت نام کردید:"
#     msg = bot.send_message(message.chat.id, text)
#     bot.register_next_step_handler(msg, email_getter, data)
#
#
# def email_getter(message, data):
#     data['email'] = message.text
#     text = "حالا بفرمایید به چه مشکلی برخوردید:"
#     msg = bot.send_message(message.chat.id, text)
#     bot.register_next_step_handler(msg, problem_handler, data)
#
#
# def problem_handler(message, data):
#     # data['problem'] = ai.tag(message.text)
#     data['problem'] = message.text
#     bot.send_message(os.getenv('SUPPORT_CHANNEL'), str(data))
#     text = "ممنونم! مشکل شما ثبت شد. همکارانم در پشتیبانی به زودی به اون رسیدگی خواهند کرد و نتیجه همینجا به شما اعلام می شود."
#     bot.send_message(message.chat.id, text)


# @bot.message_handler(commands=['info'])
# def info(message):
#     text = "در رابطه با کدوم مورد سوال دارید؟ از بین دو گزینه زیر انتخاب کنید:"
#     msg = bot.reply_to(message, text, reply_markup=info_keyboard)
#     bot.register_next_step_handler(msg, info_classifier)
#
#
# def info_classifier(message):
#     text = "سوالتون رو بفرمایید:"
#     msg = bot.send_message(message.chat.id, text)
#     if message.text == "مسابقه":
#         print("contest")
#         bot.register_next_step_handler(msg, contest_info_handler)
#     else:
#         print("course")
#         bot.register_next_step_handler(msg, courses_info_handler)


# def courses_info_handler(message):
#     print(message)
#     response = ai.get_courses_info(message.text)
#     print(response)
#     bot.send_message(message.chat.id, response['response'])
#

@bot.message_handler()
def contest_info_handler(message):
    response = ai.get_contest_info(message.text, message.chat.id)
    bot.send_message(message.chat.id, response)


bot.infinity_polling()
