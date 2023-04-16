import datetime
import sqlite3
import time, os
from telebot import types
from telebot.types import Message
import telebot
from secret_for_protokoler import API_KEY, my_access_list, Config_bot
import pandas as pd
from sqlalchemy import create_engine
"""
делаем протокллер - будет делать сводку по всем протоколам...
брать данные и делать выборку - выполнено или нет..

"""

# db_connection = create_engine(sql_login, connect_args={'connect_timeout': 10})

db_NAME = 'local_sql__protokoler.db'
my_access_set = set(Config_bot.my_access_list)
# subscriber_set_db = set()

bot = telebot.TeleBot(API_KEY)

print('START protokoler_bot')


def check_for_access(message: Message):
    global my_access_set
    if len(my_access_set) == 0:
        my_access_set.add(int(my_access_list[0]))
        local_sql = sqlite3.connect(db_NAME)
        for item in local_sql.execute(
                'select user_id from USER where user_group = "root" and user_activation="1";').fetchall():
            my_access_set.add(item[0])
        print('my Access_set::', my_access_set)

    if message.from_user.id in my_access_set:
        return True
    else:
        return False


def save_exeption(message: str):
    with open(Config_bot.proj_path + '\\protokoler_exeption.log') as file:
        file.writelines(f"[{datetime.datetime.now()}]:{message}\n")


@bot.message_handler(commands=['start'])
def start(message: Message):
    if check_for_access(message):
        bot.send_message(message.from_user.id, "start BOT")
        if check_for_access(message):
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtna = types.KeyboardButton('/protokol')
            itembtnb = types.KeyboardButton('/start')
            markup.row(itembtna, itembtnb)
            bot.send_message(message.from_user.id, "you are ROOT: \n", reply_markup=markup)
            # bot.send_message(message.from_user.id, my_process_py)
        # else:
        #     markup = types.ReplyKeyboardMarkup(row_width=2)
        #     itembtna = types.KeyboardButton('/user_info')

        #     itembtne = types.KeyboardButton('/start')
        #     markup.row(itembtna, itembtnb, itembtnc)
        #     markup.row(itembtne)
        #     bot.send_message(message.from_user.id, "Choose one letter:", reply_markup=markup)


@bot.message_handler(commands=['protokol'])
def protokol(message:Message):
    if check_for_access(message):
        bot.send_message(message.from_user.id, "PROTOKOL::")
        




while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        print(f"found Error::{_ex}")
        save_exeption(_ex)
    time.sleep(10)
