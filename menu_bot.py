import datetime
import sqlite3
import time, os
from telebot import types
from telebot.types import Message
import telebot
from secret_for_menu import API_KEY, my_access_list, subscriber_list, sql_login
import pandas as pd
from sqlalchemy import create_engine

db_connection = create_engine(sql_login, connect_args={'connect_timeout': 10})

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

    local_sql = sqlite3.connect(db_NAME)
    tab_name = {j for i in local_sql.execute("select name from sqlite_master where type = 'table';").fetchall() for j in
                i}
    print('\nTAB NAME:::',tab_name)
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
            (my_access_list[0], 'root', 1, datetime.datetime.strptime('2030/08/10', '%Y/%m/%d')),
            (subscriber_list[2], 'subscriber', 1, datetime.datetime.strptime('2023/08/10', '%Y/%m/%d')),
            (subscriber_list[3], 'subscriber', 1, datetime.datetime.strptime('2023/08/10', '%Y/%m/%d'))
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
                        user_date_request timestamp
                    );
                """)
        local_sql.commit()
        bot.send_message(my_access_list[0], f'CREATE TABLE PENDING_USER in db')
    if "BLOKED_USER" not in tab_name:
        local_sql.execute("""
                    CREATE TABLE BLOKED_USER (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,              
                        user_date_request timestamp
                    );
                """)
        local_sql.commit()
        bot.send_message(my_access_list[0], f'CREATE TABLE BLOKED_USER in db')

check_local_data_base()


def remove_from_bloked_list(user_id: int):
    local_sql = sqlite3.connect(db_NAME)
    local_sql.execute(f'delete from BLOKED_USER where user_id="{user_id}";')
    local_sql.commit()


def check_for_access(message: Message):
    global my_access_set
    if len(my_access_set) == 0:
        my_access_set.add(int(my_access_list[0]))
        local_sql = sqlite3.connect(db_NAME)
        for item in local_sql.execute(
                'select user_id from USER where user_group = "root" and user_activation="1";').fetchall():
            my_access_set.add(item[0])
        print('my A _set::', my_access_set)

    if message.from_user.id in my_access_set:
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
        subscriber_set_db.add(int(my_access_list[0]))
    if user_id in subscriber_set_db:
        return True
    else:
        return False


@bot.message_handler(commands=['restart'])
def restart(message: Message):
    if check_for_access(message):
        spl = message.text.split()
        if spl[1] == 'USER':
            local_sql = sqlite3.connect(db_NAME)
            local_sql.execute('drop table USER;').fetchall()
            local_sql.commit()
            bot.send_message(my_access_list[0], f'USER table droped:')


@bot.message_handler(commands=['start'])
def start(message: Message):
    if check_for_subscribers(message.from_user.id):
        bot.send_message(message.from_user.id, "start BOT ")
        if check_for_access(message):
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtna = types.KeyboardButton('/user')
            itembtnv = types.KeyboardButton('/pending_user')
            itembtnc = types.KeyboardButton('/tiker_report_status')
            itembtnd = types.KeyboardButton('/sendmefile')
            itembtnf = types.KeyboardButton('/log')
            itembtne = types.KeyboardButton('/start')
            markup.row(itembtna, itembtnv)
            markup.row(itembtnc, itembtnd)
            markup.row(itembtnf, itembtne)
            bot.send_message(message.from_user.id, "you are ROOT: \nChoose one letter:", reply_markup=markup)
            # bot.send_message(message.from_user.id, my_process_py)
        else:
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtna = types.KeyboardButton('/user_info')
            itembtnb = types.KeyboardButton('/sendmefile')
            itembtnc = types.KeyboardButton('/tiker_report_status')
            itembtne = types.KeyboardButton('/start')
            markup.row(itembtna, itembtnb, itembtnc)
            markup.row(itembtne)
            bot.send_message(message.from_user.id, "Choose one letter:", reply_markup=markup)
    else:
        local_sql = sqlite3.connect(db_NAME)
        bloked_user_set = {i for i in local_sql.execute('select user_id from BLOKED_USER;').fetchall()}
        if message.from_user.id not in bloked_user_set:
            itembtna = types.KeyboardButton('/sendmessage')
            markup = types.ReplyKeyboardMarkup(row_width=2)
            markup.row(itembtna)
            bot.send_message(message.from_user.id, "start BOT.\nYou not in subscriber list\nYou can send message\n",
                             reply_markup=markup)


@bot.message_handler(commands=['pending_user'])
def start(message: Message):
    if check_for_access(message):
        mess_split = message.text.split()
        local_sql = sqlite3.connect(db_NAME)
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
            bot.send_message(my_access_list[0], f'choose one:', reply_markup=markup)

        if 'list' in mess_split[1]:

            pending_user_list = [i[1] for i in local_sql.execute('select * from PENDING_USER;').fetchall()]
            if len(pending_user_list) != 0:
                bot.send_message(my_access_list[0], f'pending_user_list len:{len(pending_user_list)}')
                mess_loc = 'list of pending_user:\n'
                for item in pending_user_list:
                    mess_loc += f"-{item}\n"
                bot.send_message(my_access_list[0], mess_loc)

                generate_user_list('command', pending_user_list)
            else:
                bot.send_message(my_access_list[0], f'pending_user_list is empty..')
        if 'command' in mess_split[1]:
            if len(mess_split) > 2:
                print('pending command', len(mess_split))
                markup = types.ReplyKeyboardMarkup(row_width=2)
                markup.row(types.KeyboardButton(f'/pending_user info {mess_split[2]}'))
                markup.row(types.KeyboardButton(f'/user add -{mess_split[2]}- -subscriber-'),
                           types.KeyboardButton(f'/pending_user block {mess_split[2]}'))
                markup.row(types.KeyboardButton('/pending_user list'), types.KeyboardButton('/start'))
                bot.send_message(my_access_list[0], f'choose one:', reply_markup=markup)

        if 'info' in mess_split[1]:
            if len(mess_split) > 2:
                bot.send_message(my_access_list[0], f'{mess_split[2]}')
                markup = types.ReplyKeyboardMarkup(row_width=2)
                markup.row(types.KeyboardButton(f'/user add -{mess_split[2]}- -subscriber-'),
                           types.KeyboardButton(f'/pending_user block {mess_split[2]}'))
                markup.row(types.KeyboardButton('/pending_user list'), types.KeyboardButton('/start'))
                bot.send_message(my_access_list[0], f'choose one:', reply_markup=markup)
        if 'block' in mess_split[1]:
            if len(mess_split) > 2:
                local_sql.execute(
                    f'INSERT INTO BLOKED_USER (user_id, user_date_request) values({mess_split[2]}, {datetime.datetime.today()})')
                local_sql.commit()
                local_sql.execute(f'delete from PENDING_USER where user_id="{mess_split[2]}";')
                local_sql.commit()
                bot.send_message(my_access_list[0], f'user bloked {mess_split[2]}')


@bot.message_handler(commands=['tiker_report_status'])
def tiker_report_status(message: Message):
    my_mes = 'tiker_report_status \n'
    if check_for_subscribers(message.from_user.id):
        sql_message = 'Select tiker, max(day_close) as max_day_close, market from tiker_report group by tiker;'
        df = pd.read_sql(sql_message, con=db_connection)
        for market in df['market'].unique():
            statistik_list = pd.Series({c: df[df['market'] == market][c].unique() for c in df})
            statistik_list['max_day_close'].sort()
            # my_mes += ''.join([f'len max_day_close [{len(statistik_list[1])}]\n'])
            my_mes += ''.join([
                f"[{market}][{statistik_list.iat[1][-2]}][{len(df[(df['max_day_close'] == statistik_list.iat[1][-2]) & (df['market'] == market)]['tiker'])}]\n"])
            my_mes += ''.join([
                f"[{market}][{statistik_list.iat[1][-1]}][{len(df[(df['max_day_close'] == statistik_list.iat[1][-1]) & (df['market'] == market)]['tiker'])}]\n"])
        bot.send_message(message.from_user.id, my_mes)



@bot.message_handler(commands=['sendmefile'])
def sendmefile(message: Message):
    '''send any file'''
    path_for_telebot = '/mnt/1T/opt/gig/My_Python/st_US/otchet/'

    def sendmefile_log(id: int, name: str):
        with open('sendmefile.log', 'a') as file:
            file.writelines(f"[{datetime.datetime.now()}] [{id}] [{name}]\n")

    def sender(key: str):
        dir_list = os.listdir(path_for_telebot)
        otchet_all = [name for name in dir_list if key in name]
        otchet_all.sort()
        if len(otchet_all) > 0:
            with open(path_for_telebot + otchet_all[-1], 'rb') as file:
                sendmefile_log(message.from_user.id, otchet_all[-1])
                bot.send_document(message.from_user.id, file)
        else:
            bot.send_message(message.from_user.id, 'file not found.. sorry')

    if check_for_subscribers(message.from_user.id):
        markup = types.ReplyKeyboardMarkup()
        itembtna = types.KeyboardButton('/sendmefile all')
        itembtnd = types.KeyboardButton('/sendmefile d')
        itembtnQ = types.KeyboardButton('/sendmefile ?')
        itembtnTeh = types.KeyboardButton('/sendmefile teh_out')
        itembtne = types.KeyboardButton('/start')
        markup.row(itembtna, itembtnd)
        markup.row(itembtnQ, itembtnTeh)
        markup.row(itembtne)
        spl = message.text.split()
        if len(spl) > 1:
            if 'all' in spl[1]:
                sender('all')
            elif 'd' in spl[1]:
                sender('d')
            elif 't' in spl[1]:
                sender('teh_out')
            elif '?' in spl[1]:
                dir_list = os.listdir(path_for_telebot)
                otchet_all = [name for name in dir_list if 'all' in name]
                otchet_d = [name for name in dir_list if 'd' in name]
                otchet_teh = [name for name in dir_list if 'teh_out' in name]
                otchet_d.sort()
                otchet_all.sort()
                otchet_teh.sort()
                bot.send_message(message.from_user.id,
                                 f'last file:\n{otchet_d[-1]}\n{otchet_all[-1]}\n{otchet_teh[-1]}')
        else:
            bot.send_message(message.from_user.id, "Поконкретнее:", reply_markup=markup)
    # else:
    #     bot.send_message(message.from_user.id, f'Пожалуй тебя нет в списках.. id ={message.from_user.id}')
    # from my_os_test_config import subscriber_list


@bot.message_handler(commands=['sendmessage'])
def send_message_to_root(message: Message):
    bot.send_message(my_access_list[0], f'user[{message.from_user.id}] wants to join\n ')
    bot.send_message(my_access_list[0], f'{message.from_user}')
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtna = types.KeyboardButton(f'/user add -{message.from_user.id}- -subscriber-')
    itembtnb = types.KeyboardButton(f'/start')
    markup.row(itembtna)
    markup.row(itembtnb)

    def add_to_pending_user(user_id: int):
        local_sql = sqlite3.connect(db_NAME)
        local_sql.execute(
            f'INSERT INTO PENDING_USER (user_id, user_date_request ) values("{user_id}","{datetime.datetime.now()}");')
        local_sql.commit()
        print('add user in PENDING_USER table')

    add_to_pending_user(message.from_user.id)
    bot.send_message(my_access_list[0], f'/user add -{message.from_user.id}- -subscriber-', reply_markup=markup)


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
        bot.send_message(my_access_list[0], f'choose one:', reply_markup=markup)

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

        bot.send_message(my_access_list[0], f'choose one:', reply_markup=markup)

    if check_for_access(message):
        markup = types.ReplyKeyboardMarkup()
        global subscriber_set_db

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

        local_sql = sqlite3.connect(db_NAME)
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
                            my_access_set.add(u_id)
                            subscriber_set_db.add(u_id)
                        elif 'subscriber' in user_data['user_group']:
                            local_sql.execute(
                                f'INSERT INTO USER (user_id, user_group,user_activation) values("{user_data["user_id"]}", "subscriber", "1");')
                            local_sql.commit()

                            if check_in_pending_user(u_id):
                                local_sql.execute(f'delete from PENDING_USER where user_id="{u_id}";')
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
            markup.row(itembtna, itembtnb)
            bot.send_message(message.from_user.id,
                             'You can: \n user add -id- -group-,\n user list,\n user remove -id-\n user activate -id-\n user deactivate -id-',
                             reply_markup=markup
                             )
            bot.send_message(message.from_user.id,
                             'group:\nroot\nsubscriber\n'
                             )


@bot.message_handler(commands=['log'])
def log_status(message: Message):
    if check_for_access(message):
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtna = types.KeyboardButton('/log update')
        itembtnd = types.KeyboardButton('/log calc')
        itembtnf = types.KeyboardButton('/log sendmefile')

        itembtne = types.KeyboardButton('/start')
        markup.row(itembtna, itembtnd, itembtne)
        markup.row(itembtne)
        spl = message.text.split()
        if len(spl) > 1:
            if 'update' in spl[1]:
                try:
                    mess = os.popen('tail -19 /root/update-sql.log').read()
                    if len(mess) > 4000:
                        mess = mess[-2000:]
                    bot.send_message(message.from_user.id, mess)
                except FileExistsError:
                    bot.send_message(message.from_user.id, 'File not found')

            elif 'calc' in spl[1]:
                try:
                    mess = os.popen('tail -19 /root/my_py/stock_rep_calc/log/make_from_sql.log').read()
                    if len(mess) > 4000:
                        mess = mess[-2000:]
                    bot.send_message(message.from_user.id, mess)
                except FileExistsError:
                    bot.send_message(message.from_user.id, 'File not found')
            elif 'sendmefile' in spl[1]:
                try:
                    mess = os.popen('tail -7 /root/my_py/telebot/ban_monitor/sendmefile.log').read()
                    if len(mess) > 4000:
                        mess = mess[-2000:]

                    bot.send_message(message.from_user.id, mess)
                except FileExistsError:
                    bot.send_message(message.from_user.id, 'File not found')
        else:
            bot.send_message(message.from_user.id, "Поконкретнее:", reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, 'все ок')



while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        pass
    time.sleep(100)
