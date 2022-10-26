import datetime
import sqlite3
import time, os
from telebot import types
from telebot.types import Message, ReplyKeyboardRemove
import telebot
from secret_help_fond import *

db_NAME = 'local_sql__help_fond_bot.db'

"""три типа пользоветелей - 
    root- 
    volonter - 
    rescued -
    """
my_access_set = set()
volonter_set_db = set()
rescued_set_db = set()
bot = telebot.TeleBot(API_KEY)

print('START menu_bot')


def check_local_data_base():
    """
    add local db for users if not open
    :return:
    """

    local_sql = sqlite3.connect(db_NAME)
    tab_name = {j for i in local_sql.execute("select name from sqlite_master where type = 'table';").fetchall() for j in
                i}
    print('\nTAB NAME:::', tab_name)
    if 'USER' not in tab_name:
        local_sql.execute("""
            CREATE TABLE USER (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_group TEXT,
                user_address TEXT,
                user_activation INTEGER, 
                user_date_act timestamp 
            );
        """)

        sql = 'INSERT INTO USER (user_id, user_group,user_activation, user_date_act,user_address) values( ?, ?, ?, ?, ?)'
        data = [
            (my_access_list[0], 'root', 1, datetime.datetime.strptime('2030/08/10', '%Y/%m/%d'), 'Москва'),

        ]
        with local_sql:
            local_sql.executemany(sql, data)
        bot.send_message(my_access_list[0], f'CREATE TABLE USER in db')
        mess_add = local_sql.execute('select * from USER;').fetchall()
        bot.send_message(my_access_list[0], f'USER in db:{mess_add}')

    if "PENDING_USER" not in tab_name:
        local_sql.execute("""
                    CREATE TABLE PENDING_USER (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,   
                        user_group TEXT,  
                        user_address TEXT,         
                        user_date_request timestamp
                    );
                """)
        local_sql.commit()
        bot.send_message(my_access_list[0], f'CREATE TABLE PENDING_USER in db')

    # if "BLOKED_USER" not in tab_name:
    #     local_sql.execute("""
    #                 CREATE TABLE BLOKED_USER (
    #                     id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    #                     user_id INTEGER,
    #                     user_date_request timestamp
    #                 );
    #             """)
    #     local_sql.commit()
    #     bot.send_message(my_access_list[0], f'CREATE TABLE BLOKED_USER in db')


check_local_data_base()


@bot.message_handler(commands=['restart'])
def restart(message: Message):
    if check_for_access(message):
        spl = message.text.split()
        if spl[1] == 'USER':
            local_sql = sqlite3.connect(db_NAME)
            local_sql.execute('drop table USER;').fetchall()
            local_sql.commit()
            bot.send_message(my_access_list[0], f'USER table droped:')


def check_for_access(user_id: int):
    global my_access_set
    if len(my_access_set) == 0:
        my_access_set.add(int(my_access_list[0]))
        local_sql = sqlite3.connect(db_NAME)
        for item in local_sql.execute(
                'select user_id from USER where user_group = "root" and user_activation="1";').fetchall():
            my_access_set.add(item[0])
        print('my A _set::', my_access_set)

    if user_id in my_access_set:
        return True
    else:
        return False


def check_for_volonter(user_id: int):
    global volonter_set_db
    if len(volonter_set_db) == 0:
        local_sql = sqlite3.connect(db_NAME)
        volonter_set_db = set(i[0] for i in local_sql.execute(
            'select user_id from USER where user_group = "volonter" and user_activation="1" ;').fetchall())
        volonter_set_db.add(int(my_access_list[0]))
    if user_id in volonter_set_db:
        return True
    else:
        return False


def check_for_rescued(user_id: int):
    global rescued_set_db
    if len(rescued_set_db) == 0:
        local_sql = sqlite3.connect(db_NAME)
        rescued_set_db = set(i[0] for i in local_sql.execute(
            'select user_id from USER where user_group = "rescued" and user_activation="1" ;').fetchall())
        rescued_set_db.add(int(my_access_list[0]))
    if user_id in rescued_set_db:
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def start(message: Message):
    if check_for_access(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtna = types.KeyboardButton('/user')
        itembtnv = types.KeyboardButton('/url')
        # itembtnc = types.KeyboardButton('/tiker_report_status')
        # itembtnd = types.KeyboardButton('/sendmefile')
        # itembtnf = types.KeyboardButton('/log')
        itembtne = types.KeyboardButton('/start')
        markup.row(itembtna, itembtnv)
        # markup.row(itembtnc, itembtnd)
        markup.row(itembtne)
        bot.send_message(message.from_user.id, "start BOT from ADMIN: \nChoose one letter:", reply_markup=markup)
        # bot.send_message(message.from_user.id, my_process_py)
    elif check_for_volonter(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtna = types.KeyboardButton('/start')
        itembtnv = types.KeyboardButton('/random')

        markup.row(itembtna, itembtnv)
        bot.send_message(message.from_user.id, "start BOT from Volonter: \nChoose one letter:", reply_markup=markup)
    elif check_for_rescued(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtna = types.KeyboardButton('/start')
        itembtnv = types.KeyboardButton('/need help')
        markup.row(itembtna, itembtnv)
        bot.send_message(message.from_user.id, "start BOT from Оберегаемый: \nChoose one letter:", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtne = types.KeyboardButton('/start')
        markup.row(itembtne)
        bot.send_message(message.from_user.id, "заявка на первичную регистрацию: \nChoose one letter:",
                         reply_markup=markup)
        bot.send_message(message.from_user.id,
                         "волонтер -- /V адрес (город)\nнуждающийся -- /R адрес (полный: город, ул, дом, корп, кв)\n админ -- /S адрес (город)")


#
# else:
# local_sql = sqlite3.connect(db_NAME)
# bloked_user_set = {i for i in local_sql.execute('select user_id from BLOKED_USER;').fetchall()}
# if message.from_user.id not in bloked_user_set:
#     itembtna = types.KeyboardButton('/sendmessage')
#     markup = types.ReplyKeyboardMarkup(row_width=2)
#     markup.row(itembtna)
#     bot.send_message(message.from_user.id, "start BOT.\nYou not in subscriber list\nYou can send message\n",
#                      reply_markup=markup)

@bot.message_handler(commands=['R'])
def rescued_reg(message: Message):
    mess_split = message.text.strip('/R')
    bot.send_message(message.from_user.id, mess_split)


@bot.message_handler(commands = ['url'])
def url(message):
    # bot.send_message(message.chat.id, 'a', reply_markup=ReplyKeyboardRemove())
    markup = types.InlineKeyboardMarkup()
    btn_my_site= types.InlineKeyboardButton(text='Наш сайт', url='https://habrahabr.ru')
    markup.add(btn_my_site)


    bot.send_message(message.chat.id, "Нажми на кнопку и перейди на наш сайт.", reply_markup = markup)


# @bot.message_handler(commands="random")
# async def cmd_random(message: Message):
#     keyboard = types.InlineKeyboardMarkup()
#     keyboard.add(types.InlineKeyboardButton(text="Нажми меня", callback_data="random_value"))
#     await message.answer("Нажмите на кнопку, чтобы бот отправил число от 1 до 10", reply_markup=keyboard)
#
#
# @bot.callback_query_handler(text="random_value")
# def send_random_value(call: types.CallbackQuery):
#     call.message.answer(str("teeett"))


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        pass
    time.sleep(100)
