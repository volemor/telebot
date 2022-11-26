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
print(f'список доступа:{__Conf_tkb.my_access_list}')


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

def add_user_to_pending_list(user_id:int):
    pass


def check_for_access(message: Message):
    if len(__Conf_tkb.my_access_set) == 0:
        __Conf_tkb.my_access_set.add(int(__Conf_tkb.my_access_list[0]))
        local_sql = sqlite3.connect(__Conf_tkb.db_NAME)
        for item in local_sql.execute(
                'select user_id from USER where user_group = "root" and user_activation="1";').fetchall():
            __Conf_tkb.my_access_set.add(item[0])
        print('my A _set::', __Conf_tkb.my_access_set)
    if message.from_user.id in __Conf_tkb.my_access_set:
        # print('ch_f_acc:True')
        return True
    else:
        # print('ch_f_acc:False')
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

def check_for_bloked_user(message: Message):
    local_sql = sqlite3.connect(__Conf_tkb.db_NAME)
    bloked_user_set = {int(i) for i in local_sql.execute('select user_id from BLOKED_USER;').fetchall()}
    if int(message.from_user.id) in bloked_user_set:
        return True
    else:
        return False

def check_for_pending_user(message: Message):
    local_sql = sqlite3.connect(__Conf_tkb.db_NAME)
    pending_user_set = {int(i) for i in local_sql.execute('select user_id from PENDING_USER;').fetchall()}
    if int(message.from_user.id) in pending_user_set:
        return True
    else:
        return False

@bot.message_handler(commands=['pending_user'])
def pending(message: Message):
    if check_for_access(message):
        mess_split = message.text.split()
        local_sql = sqlite3.connect(__Conf_tkb.db_NAME)
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtna = types.KeyboardButton(f'/pending_user list')
        itembtnb = types.KeyboardButton(f'/pending_user command')
        itembtnc = types.KeyboardButton(f'/pending_user info')
        itembtnd = types.KeyboardButton(f'/pending_user block')
        itembtne = types.KeyboardButton(f'/pending_user')
        itembtnf = types.KeyboardButton(f'/start')
        markup.row(itembtna, itembtnb)
        markup.row(itembtnc, itembtnd)
        markup.row(itembtne, itembtnf)
        bot.send_message(message.from_user.id, "Choose one letter:", reply_markup=markup)

        def generate_user_list(com, user_id_list: list):
            itembtn = list()
            markup = types.ReplyKeyboardMarkup(row_width=2)
            for item in user_id_list:
                itembtn.append(types.KeyboardButton(f'/pending_user {com} {item}'))
            print('item_len--', len(itembtn))
            if len(itembtn) < 3:
                markup.row(*itembtn[:])
            else:
                for item in range(0, len(itembtn), 2):
                    markup.row(*itembtn[item:item + 2])
            markup.row(types.KeyboardButton('/pending_user list'), types.KeyboardButton('/start'))
            bot.send_message(__Conf_tkb.my_access_list[0], f'choose one:', reply_markup=markup)

        if len(mess_split) > 1:
            if 'list' in mess_split[1]:

                pending_user_list = [i[1] for i in local_sql.execute('select * from PENDING_USER;').fetchall()]
                if len(pending_user_list) != 0:
                    bot.send_message(__Conf_tkb.my_access_list[0], f'pending_user_list len:{len(pending_user_list)}')
                    mess_loc = 'list of pending_user:\n'
                    for item in pending_user_list:
                        mess_loc += f"-{item}\n"
                    bot.send_message(__Conf_tkb.my_access_list[0], mess_loc)

                    generate_user_list('command', pending_user_list)
                else:
                    bot.send_message(__Conf_tkb.my_access_list[0], f'pending_user_list is empty..')
            if 'command' in mess_split[1]:
                if len(mess_split) > 2:
                    print('pending command', len(mess_split))
                    markup = types.ReplyKeyboardMarkup(row_width=2)
                    markup.row(types.KeyboardButton(f'/pending_user info {mess_split[2]}'))
                    markup.row(types.KeyboardButton(f'/user add -{mess_split[2]}- -subscriber-'),
                               types.KeyboardButton(f'/pending_user block {mess_split[2]}'))
                    markup.row(types.KeyboardButton('/pending_user list'), types.KeyboardButton('/start'))
                    bot.send_message(__Conf_tkb.my_access_list[0], f'choose one:', reply_markup=markup)
                else:
                    bot.send_message(__Conf_tkb.my_access_list[0], f'не верный формат')
            if 'info' in mess_split[1]:
                if len(mess_split) > 2:
                    bot.send_message(__Conf_tkb.my_access_list[0], f'{mess_split[2]}')
                    markup = types.ReplyKeyboardMarkup(row_width=2)
                    markup.row(types.KeyboardButton(f'/user add -{mess_split[2]}- -subscriber-'),
                               types.KeyboardButton(f'/pending_user block {mess_split[2]}'))
                    markup.row(types.KeyboardButton('/pending_user list'), types.KeyboardButton('/start'))
                    bot.send_message(__Conf_tkb.my_access_list[0], f'choose one:', reply_markup=markup)
                else:
                    bot.send_message(__Conf_tkb.my_access_list[0], f'не верный формат')
            if 'block' in mess_split[1]:
                if len(mess_split) > 2:
                    local_sql.execute(
                        f'INSERT INTO BLOKED_USER (user_id, user_date_request) values({mess_split[2]}, {datetime.datetime.today()})')
                    local_sql.commit()
                    local_sql.execute(f'delete from PENDING_USER where user_id="{mess_split[2]}";')
                    local_sql.commit()
                    bot.send_message(__Conf_tkb.my_access_list[0], f'user bloked {mess_split[2]}')
                else:
                    bot.send_message(__Conf_tkb.my_access_list[0], f'не верный формат')


@bot.message_handler(commands=['user'])
def user(message: Message):
    def generate_com_button(command_list: list, us_id: int):
        itembtn = list()
        markup = types.ReplyKeyboardMarkup(row_width=1)
        for item in command_list:
            itembtn.append(types.KeyboardButton(f'/{item} -{us_id}-'))
        # for item in range(len(itembtn)):
        if len(itembtn) <= 3:
            markup.row(*itembtn[:])
            markup.row(types.KeyboardButton('/user list'), types.KeyboardButton('/user'))
        else:
            markup.row(*itembtn[:3])
            markup.row(*itembtn[3:])
            markup.row(types.KeyboardButton('/user list'), types.KeyboardButton('/user'))
        bot.send_message(__Conf_tkb.my_access_list[0], f'choose one:', reply_markup=markup)

    def generate_user_list(com, user_id_list: list):
        itembtn = list()
        markup = types.ReplyKeyboardMarkup(row_width=2)
        for item in user_id_list:
            itembtn.append(types.KeyboardButton(f'/user {com} -{item}-'))
        print('item_len--', len(itembtn))
        if len(itembtn) < 3:
            markup.row(*itembtn[:])
            markup.row(types.KeyboardButton('/user list'), types.KeyboardButton('/user'))
        else:
            for item in range(0, len(itembtn), 2):
                markup.row(*itembtn[item:item + 2])

            # markup.row(*itembtn[3:])
            markup.row(types.KeyboardButton('/user list'), types.KeyboardButton('/user'))

        bot.send_message(__Conf_tkb.my_access_list[0], f'choose one:', reply_markup=markup)

    if check_for_access(message):
        markup = types.ReplyKeyboardMarkup()

        # class Add_User(BaseModel):
        #     user_id: int
        #     user_group: Literal['root', 'subscriber']
        #     user_activation: bool

        # /user add -1324248- -subscriber-
        # /user add -12212312- -root-
        # /user add -1111f243- -subscriber-
        # /user add -439255451- -subscriber-
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

        local_sql = sqlite3.connect(__Conf_tkb.db_NAME)
        if len(mess_split) > 1:
            if 'add' in mess_split[1]:
                u_id = check_format_uid(mess_split[2].strip('-'))

                def check_in_pending_user(user_id):
                    if user_id in {i[1] for i in local_sql.execute('select * from PENDING_USER;').fetchall()}:
                        return True
                    return False

                if u_id:
                    if check_for_subscribers(u_id):
                        bot.send_message(message.from_user.id, f'- user allready in database')
                    else:
                        user_data = {'user_id': u_id,
                                     'user_group': str(mess_split[3].strip("-")),
                                     'user_activation': True}
                        if 'root' in user_data['user_group']:
                            local_sql.execute(
                                f'INSERT INTO USER (user_id, user_group,user_activation ) values("{user_data["user_id"]}", "root", "1");')
                            local_sql.commit()
                            bot.send_message(message.from_user.id, '-add_user root')
                            __Conf_tkb.my_access_set.add(u_id)
                            __Conf_tkb.subscriber_set_db.add(u_id)
                        elif 'subscriber' in user_data['user_group']:
                            local_sql.execute(
                                f'INSERT INTO USER (user_id, user_group,user_activation) values("{user_data["user_id"]}", "subscriber", "1");')
                            local_sql.commit()

                            if check_in_pending_user(u_id):
                                local_sql.execute(f'delete from PENDING_USER where user_id="{u_id}";')
                                local_sql.commit()

                            bot.send_message(message.from_user.id, '-add_user subscriber')
                            __Conf_tkb.subscriber_set_db.add(u_id)
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
                user_list = []
                mess_loc_s, mess_loc_r = '', ''
                count_s, count_r = 0, 0
                for item in U_list:
                    if 'subscriber' == item[2]:
                        if item[3]:
                            x = True
                        else:
                            x = False
                        user_list.append(item[1])
                        mess_loc_s += f'  id:{item[1]} activ:{x}\n'
                        count_s += 1
                    if 'root' == item[2]:
                        if item[3]:
                            x = True
                        else:
                            x = False
                        mess_loc_r += f'  id:{item[1]} activ:{x}\n'
                print('user_list ---', user_list)
                generate_user_list('command', user_list)
                bot.send_message(message.from_user.id,
                                 f'Subscriber [{count_s}]:\n{mess_loc_s}\n Root:[{count_r}]:\n{mess_loc_r}')

            if 'command' in mess_split[1]:
                u_id = check_format_uid(mess_split[2].strip('-'))
                if u_id:
                    if check_for_subscribers(u_id):
                        generate_com_button(['user remove', 'user activate', 'user deactivate'], u_id)
            if 'remove' in mess_split[1]:
                u_id = check_format_uid(mess_split[2].strip('-'))
                if u_id:
                    if check_for_subscribers(u_id):
                        local_sql.execute(f'delete from USER where user_id="{u_id}"; ')
                        local_sql.commit()
                        bot.send_message(message.from_user.id, f'-user {u_id} removed')
                        __Conf_tkb.subscriber_set_db.remove(u_id)
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
            print('Subscr_db:', __Conf_tkb.subscriber_set_db)
            print('aCses_db:', __Conf_tkb.my_access_set)


        else:
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtna = types.KeyboardButton(f'/user list')
            itembtnb = types.KeyboardButton(f'/start')
            markup.row(itembtna, itembtnb)
            bot.send_message(message.from_user.id,
                             'You can: \n user add -id- -group-,\n user list,\n user remove -id-\n user activate -id-\n user deactivate -id-',
                             reply_markup=markup
                             )
            bot.send_message(message.from_user.id,
                             'group:\nroot\nsubscriber\n'
                             )


@bot.message_handler(commands=['start'])
def start(message: Message):
    if check_for_subscribers(message.from_user.id):
        # bot.send_message(message.from_user.id, "start BOT")
        if check_for_access(message):
            markup = types.ReplyKeyboardMarkup(row_width=4)
            itembtna = types.KeyboardButton('/pending_user')
            itembtnc = types.KeyboardButton('/user')
            markup.row(itembtna)
            markup.row(itembtnc)
            bot.send_message(message.from_user.id, "you are ROOT: \n", reply_markup=markup)
            # bot.send_message(message.from_user.id, my_process_py)
        else:
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtna = types.KeyboardButton('🎁вступить')
            itembtnb = types.KeyboardButton('статистика👍')
            markup.row(itembtna, itembtnb)
            bot.send_message(message.from_user.id, reply_markup=markup)
    elif check_for_bloked_user(message):
        bot.send_message(message.from_user.id, 'вы заблокированы..')
    else:
        markup = types.ReplyKeyboardMarkup(row_width=4)
        itembtna = types.KeyboardButton('отправить заявку😀')
        markup.row(itembtna)
        bot.send_message(message.from_user.id, 'Вас нет в списках, отправить заявку?😀', reply_markup=markup)



@bot.message_handler(content_types=['text'])
def any_run(message: Message):
    if check_for_subscribers(message.from_user.id):
        if 'вступить' in message.text:
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
            bot.send_message(message.from_user.id, "теперь ты гей")
        elif message.text == 'КПСС':
            bot.send_message(message.from_user.id, "теперь ты член КПСС")
    elif check_for_bloked_user(message):
        bot.send_message(message.from_user.id, 'вы заблокированы..')
    elif check_for_pending_user(message):
        bot.send_message(message.from_user.id, 'вы в списке ожидания, скоро вас добавят')
    else:
        pass
    if "отправить заявку" in message.text:
        pass



while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        print(f"found Error::{_ex}")
        pass
    time.sleep(10)
