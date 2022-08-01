import sqlite3
import time

from telegram_menu import BaseMessage, TelegramMenuSession, NavigationHandler

from telebot import types
from telebot.types import Message
import telebot
from secret_for_menu import API_KEY, my_access_list, subscriber_list

db_NAME = 'local_sql__menu_bot.db'
my_access_set = set()
subscriber_set_db = set()
bot = telebot.TeleBot(API_KEY)

print('START menu_bot')


def check_local_data_base():
    """
    add local db for users if not open
    :return:
    """

    local_sql = sqlite3.connect('local_sql__menu_bot.db')
    tab_name = {j for i in local_sql.execute("select name from sqlite_master where type = 'table';").fetchall() for j in
                i}
    # print('\nTAB NAME:::',tab_name)

    if 'USER' not in tab_name:
        local_sql.execute("""
            CREATE TABLE USER (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_group TEXT,
                user_activation INTEGER
            );
        """)

        sql = 'INSERT INTO USER (user_id, user_group) values( ?, ?)'
        data = [
            (my_access_list[0], 'root'), (my_access_list[1], 'root'),
            (subscriber_list[2], 'subscriber'), (subscriber_list[3], 'subscriber')
        ]
        with local_sql:
            local_sql.executemany(sql, data)
        bot.send_message(my_access_list[0], f'CREATE TABLE USER in db')
        mess_add = local_sql.execute('select * from USER;').fetchall()
        bot.send_message(my_access_list[0], f'USER in db:{mess_add}')
    # else:
    #
    #     mess_add = local_sql.execute('select * from USER;').fetchall()
    #     bot.send_message(my_access_list[0], f'USER in db:{mess_add}')


check_local_data_base()


def check_for_access(message):
    global my_access_set
    if len(my_access_set) == 0:
        my_access_set.add(int(my_access_list[0]))
        local_sql = sqlite3.connect(db_NAME)
        for item in local_sql.execute(
                'select user_id from USER where user_group = "root" and user_activation="1";').fetchall():
            my_access_set.add(item[0])
        print('my A _set::', my_access_set)

    if str(message.from_user.id) in my_access_list:
        # save_name_to_log(message, 'access')
        return True
    else:
        return False


def check_for_subscribers(user_id: int):
    global subscriber_set_db
    if len(subscriber_set_db) == 0:
        local_sql = sqlite3.connect(db_NAME)
        subscriber_set_db = set(i[0] for i in local_sql.execute('select user_id from USER;').fetchall())
        #
        # print('sub_SET:::',subscriber_set_db)
    if user_id in subscriber_set_db:
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def start(message: Message):
    if check_for_subscribers(message.from_user.id):
        bot.send_message(message.from_user.id, "start BOT ")

        if check_for_access(message):
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtna = types.KeyboardButton('/user')
            itembtnv = types.KeyboardButton('/user list')
            itembtnc = types.KeyboardButton('/report_status')
            itembtnd = types.KeyboardButton('/sendmefile')
            itembtne = types.KeyboardButton('some 4')
            markup.row(itembtna, itembtnv)
            markup.row(itembtnc, itembtnd)
            markup.row(itembtne)
            bot.send_message(message.from_user.id, "you are ROOT: \nChoose one letter:", reply_markup=markup)
            # bot.send_message(message.chat.id, my_process_py)
        else:
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtna = types.KeyboardButton('/user_info')
            itembtnb = types.KeyboardButton('/sendmefile')
            itembtnc = types.KeyboardButton('/report_status')
            markup.row(itembtna, itembtnb, itembtnc)
            bot.send_message(message.from_user.id, "Choose one letter:", reply_markup=markup)
    else:
        itembtna = types.KeyboardButton('/sendmessage')
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup.row(itembtna)
        bot.send_message(message.from_user.id, "start BOT.\nYou not in subscriber list\nYou can send message\n",
                         reply_markup=markup)


@bot.message_handler(commands=['sendmessage'])
def send_message_to_root(message: Message):
    bot.send_message(439255451, f'user[{message.from_user.id}] wants to join\n ')
    bot.send_message(439255451, f'{message.from_user}')
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtna = types.KeyboardButton(f'/user add -{message.from_user.id}- -subscriber-')
    itembtnb = types.KeyboardButton(f'/start')
    markup.row(itembtna)
    markup.row(itembtnb)
    bot.send_message(439255451, f'/user add -{message.from_user.id}- -subscriber-', reply_markup=markup)


@bot.message_handler(commands=['user'])
def user(message: Message):
    if check_for_access(message):
        markup = types.ReplyKeyboardMarkup()
        global subscriber_set_db

        # class Add_User(BaseModel):
        #     user_id: int
        #     user_group: Literal['root', 'subscriber']
        #     user_activation: bool

        # /user add -1222111112- -subscriber-
        # /user add -12212312- -root-
        # /user add -1111f243- -subscriber-
        # /user list
        # /user remove -1114f12-
        # /user activate -1111h3227-

        def check_format_uid(u_id: str):
            try:
                u_id_int = int(u_id)
                return u_id_int
            except:
                return False

        mess_split = message.text.split()

        local_sql = sqlite3.connect(db_NAME)
        if len(mess_split) > 1:
            if 'add' in mess_split[1]:
                u_id = check_format_uid(mess_split[2].strip('-'))
                if u_id:
                    if check_for_subscribers(u_id):
                        bot.send_message(message.from_user.id, f'- user allready in database')
                    else:
                        user_data = {'user_id': u_id,
                                     'user_group': str(mess_split[3].strip("-")),
                                     'user_activation': True}
                        if 'root' in user_data['user_group']:
                            local_sql.execute(
                                f'INSERT INTO USER (user_id, user_group,user_activation ) values({user_data["user_id"]}, "root", "1");')
                            local_sql.commit()
                            bot.send_message(message.from_user.id, '-add_user root')
                            my_access_set.add(u_id)
                            subscriber_set_db.add(u_id)
                        elif 'subscriber' in user_data['user_group']:
                            local_sql.execute(
                                f'INSERT INTO USER (user_id, user_group,user_activation) values({user_data["user_id"]}, "subscriber", "1");')
                            local_sql.commit()
                            bot.send_message(message.from_user.id, '-add_user subscriber')
                            subscriber_set_db.add(u_id)
                        else:
                            bot.send_message(message.from_user.id, '-add_user error = invalid group name')
                            return False
                        # print(local_sql.execute('select * from USER ;').fetchall())
                else:
                    bot.send_message(message.from_user.id, f'-invalid user_id format')
            if 'list' in mess_split[1]:
                # local_sql.execute('delete from USER where rowid not in (select min(rowid) from USER group by user_id );')
                # local_sql.commit()
                U_list = local_sql.execute('select * from USER ;').fetchall()
                # print(U_list)
                mess_loc_s, mess_loc_r = '', ''
                count_s, count_r = 0, 0
                for item in U_list:
                    if 'subscriber' == item[2]:
                        if item[3]:
                            x = True
                        else:
                            x = False
                        mess_loc_s += f'  id:{item[1]} activ:{x}\n'
                        count_s += 1
                    if 'root' == item[2]:
                        if item[3]:
                            x = True
                        else:
                            x = False
                        mess_loc_r += f'  id:{item[1]} activ:{x}\n'

                bot.send_message(message.from_user.id,
                                 f'Subscriber [{count_s}]:\n{mess_loc_s}\n Root:[{count_r}]:\n{mess_loc_r}')

            if 'remove' in mess_split[1]:
                u_id = check_format_uid(mess_split[2].strip('-'))
                if u_id:
                    if check_for_subscribers(u_id):
                        local_sql.execute(f'delete from USER where user_id="{u_id}"; ')
                        local_sql.commit()
                        bot.send_message(message.from_user.id, f'-user {u_id} removed')
                        subscriber_set_db.remove(u_id)
                    else:
                        bot.send_message(message.from_user.id, f'-no user {u_id} in database:')
                else:
                    bot.send_message(message.from_user.id, f'-invalid user_id format')
            if 'activate' in mess_split[1]:
                u_id = check_format_uid(mess_split[2].strip('-'))
                if u_id:
                    # u_id = int(mess_split[2].strip('-'))
                    if check_for_subscribers(u_id):
                        local_sql.execute(f"update USER set user_activation = '1' where user_id='{u_id}'; ")
                        local_sql.commit()
                        bot.send_message(message.from_user.id, f'-activate_user {u_id}')
                    else:
                        bot.send_message(message.from_user.id, f'-no user {u_id} in database:')
                else:
                    bot.send_message(message.from_user.id, f'-invalid user_id format')
            if 'deactivate' in mess_split[1]:
                u_id = check_format_uid(mess_split[2].strip('-'))
                if u_id:
                    if check_for_subscribers(u_id):
                        local_sql.execute(f"update USER set user_activation = '0' where user_id='{u_id}'; ")
                        local_sql.commit()
                        bot.send_message(message.from_user.id, f'-deactivate_user {u_id}')
                    else:
                        bot.send_message(message.from_user.id, f'-no user {u_id} in database:')
                else:
                    bot.send_message(message.from_user.id, f'-invalid user_id format')
            # U_list = local_sql.execute('select * from USER ;').fetchall()
            # print('list::', U_list)
            print('Subscr_db:', subscriber_set_db)
            print('aCses_db:', my_access_set)


        else:
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtna = types.KeyboardButton(f'/user list')
            itembtnb = types.KeyboardButton(f'/start')
            markup.row(itembtna,itembtnb)
            bot.send_message(message.from_user.id,
                             'You can: \n user add -id- -group-,\n user list,\n user remove -id-\n user activate -id-\n user deactivate -id-', reply_markup=markup
                             )
            bot.send_message(message.from_user.id,
                         'group:\nroot\nsubscriber\n'
                         )
        # bot.send_message(message.chat.id, '/add_user -name- -group-')
        # itembtna = types.KeyboardButton('/add_user -name- -group-')
        # markup.row(itembtna)


# Using the ReplyKeyboardMarkup class
# It's constructor can take the following optional arguments:
# - resize_keyboard: True/False (default False)
# - one_time_keyboard: True/False (default False)
# - selective: True/False (default False)
# - row_width: integer (default 3)
# row_width is used in combination with the add() function.
# It defines how many buttons are fit on each row before continuing on the next row.



while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        pass
    time.sleep(100)

