import datetime
import sqlite3
import time, os
from telebot import types
from telebot.types import Message
import telebot
from secret_tkb import Conf_tkb as __Conf_tkb
import pandas as pd
from sqlalchemy import create_engine

bot = telebot.TeleBot(__Conf_tkb.API_KEY)

print('START TKB_bot')
print(__Conf_tkb.my_access_list)


def check_local_data_base():
    """
    add local db for users if not open
    :return:
    """

    local_sql = sqlite3.connect(__Conf_tkb.db_NAME)
    tab_name = {j for i in local_sql.execute("select name from sqlite_master where type = 'table';").fetchall() for j in
                i}
    print('\nTAB NAME:::', tab_name)
    if 'USER' not in tab_name:
        local_sql.execute("""
            CREATE TABLE USER (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_group TEXT,
                user_activation INTEGER, 
                user_date_act timestamp
            );
        """)

        sql = 'INSERT INTO USER (user_id, user_group,user_activation, user_date_act) values( ?, ?, ?, ?)'
        data = [
            (__Conf_tkb.my_access_list[0], 'root', 1, datetime.datetime.strptime('2030/11/25', '%Y/%m/%d')),
        ]
        with local_sql:
            local_sql.executemany(sql, data)
        bot.send_message(__Conf_tkb.my_access_list[0], f'CREATE TABLE USER in db')
        mess_add = local_sql.execute('select * from USER;').fetchall()
        bot.send_message(__Conf_tkb.my_access_list[0], f'USER in db:{mess_add}')
    if "PENDING_USER" not in tab_name:
        local_sql.execute("""
                    CREATE TABLE PENDING_USER (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,              
                        user_date_request timestamp
                    );
                """)
        local_sql.commit()
        bot.send_message(__Conf_tkb.my_access_list[0], f'CREATE TABLE PENDING_USER in db')
    if "BLOKED_USER" not in tab_name:
        local_sql.execute("""
                    CREATE TABLE BLOKED_USER (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,              
                        user_date_request timestamp
                    );
                """)
        local_sql.commit()
        bot.send_message(__Conf_tkb.my_access_list[0], f'CREATE TABLE BLOKED_USER in db')


def remove_from_bloked_list(user_id: int):
    local_sql = sqlite3.connect(__Conf_tkb.db_NAME)
    local_sql.execute(f'delete from BLOKED_USER where user_id="{user_id}";')
    local_sql.commit()


check_local_data_base()


def check_for_access(message: Message):
    if len(__Conf_tkb.my_access_set) == 0:
        __Conf_tkb.my_access_set.add(int(__Conf_tkb.my_access_list[0]))
        local_sql = sqlite3.connect(__Conf_tkb.db_NAME)
        for item in local_sql.execute(
                'select user_id from USER where user_group = "root" and user_activation="1";').fetchall():
            __Conf_tkb.my_access_set.add(item[0])
        print('my A _set::', __Conf_tkb.my_access_set)

    if message.from_user.id in __Conf_tkb.my_access_set:
        return True
    else:
        return False


def check_for_subscribers(user_id: int):
    if len(__Conf_tkb.subscriber_set_db) == 0:
        local_sql = sqlite3.connect(__Conf_tkb.db_NAME)
        __Conf_tkb.subscriber_set_db = set(i[0] for i in local_sql.execute('select user_id from USER;').fetchall())
        #
        # print('sub_SET:::',subscriber_set_db)
        __Conf_tkb.subscriber_set_db.add(int(__Conf_tkb.my_access_list[0]))
    if user_id in __Conf_tkb.subscriber_set_db:
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def start(message: Message):
    if check_for_subscribers(message.from_user.id):
        bot.send_message(message.from_user.id, "start BOT")
        if check_for_access(message):
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtna = types.KeyboardButton('вступить')
            itembtnv = types.KeyboardButton('понравиться')
            itembtnc = types.KeyboardButton('статистика')
            itembtnd = types.KeyboardButton('время')
            itembtnf = types.KeyboardButton('меню')
            itembtne = types.KeyboardButton('старт')
            markup.row(itembtna, itembtnv)
            markup.row(itembtnc, itembtnd)
            markup.row(itembtnf, itembtne)
            bot.send_message(message.from_user.id, "you are ROOT: \n", reply_markup=markup)
            # bot.send_message(message.from_user.id, my_process_py)
        else:
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtna = types.KeyboardButton('вступить')
            itembtnb = types.KeyboardButton('статистика')

            itembtne = types.KeyboardButton('start')
            markup.row(itembtna, itembtnb)
            markup.row(itembtne)
            bot.send_message(message.from_user.id, reply_markup=markup)
    else:
        local_sql = sqlite3.connect(__Conf_tkb.db_NAME)
        bloked_user_set = {i for i in local_sql.execute('select user_id from BLOKED_USER;').fetchall()}
        if message.from_user.id not in bloked_user_set:
            itembtna = types.KeyboardButton('/sendmessage')
            markup = types.ReplyKeyboardMarkup(row_width=2)
            markup.row(itembtna)
            bot.send_message(message.from_user.id, "start BOT.\nYou not in subscriber list\nYou can send message\n",
                             reply_markup=markup)


@bot.message_handler(content_types=['text'])
def any_run(message: Message):
    if check_for_access(message):
        if message.text == 'вступить':
            split_message = message.text.split()
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            itembtna = types.KeyboardButton('секта')
            itembtnd = types.KeyboardButton('гей клуб')
            itembtnf = types.KeyboardButton('КПСС')
            itembtne = types.KeyboardButton('/start')
            markup.row(itembtna, itembtnd, itembtnf)
            markup.row(itembtne)
            bot.send_message(message.from_user.id, 'куда встапаем?', reply_markup=markup)
        elif message.text == 'секта':
            bot.send_message(message.from_user.id, "ты в секте")
        elif message.text == 'гей клуб':
            bot.send_message(message.from_user.id, "теперь ты в гей")
        elif message.text == 'КПСС':
            bot.send_message(message.from_user.id, "теперь ты член КПСС")


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        print(f"found Error::{_ex}")
        pass
    time.sleep(10)
