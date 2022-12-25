from secret import Conf as __Conf
from telebot.types import Message
import sqlite3, datetime
from telebot.handler_backends import State, StatesGroup


class My_States(StatesGroup):
    state_start = State()
    state_con = State()


def remove_from_bloked_list(user_id: int):
    local_sql = sqlite3.connect(__Conf.db_NAME)
    local_sql.execute(f'delete from BLOKED_USER where user_id="{user_id}";')
    local_sql.commit()


def add_user_to_pending_list(user_id: int):
    local_sql = sqlite3.connect(__Conf.db_NAME)
    local_sql.execute(
        f'INSERT INTO PENDING_USER (user_id, user_date_request) values("{user_id}", "{datetime.datetime.now().date()}");')
    local_sql.commit()
    return True


def check_for_access(message: Message):
    if len(__Conf.my_access_set) == 0:
        __Conf.my_access_set.add(int(__Conf.my_access_list[0]))
        local_sql = sqlite3.connect(__Conf.db_NAME)
        root_in_sql = set(local_sql.execute(
                'select user_id from USER where user_group = "root" and user_activation="1";').fetchall())
        print('root_in_sql',root_in_sql)
        if __Conf.my_access_list[0] not in root_in_sql:
            local_sql.execute(
                f'INSERT INTO USER (user_id, user_group,user_activation ) values("{__Conf.my_access_list[0]}", "root", "1");')
            local_sql.commit()
        for item in root_in_sql:
            __Conf.my_access_set.add(item[0])
        print('my A _set:', __Conf.my_access_set)
    if message.from_user.id in __Conf.my_access_set:
        # print('ch_f_acc:True')
        return True
    else:
        # print('ch_f_acc:False')
        return False


def check_for_subscribers(user_id: int):
    if len(__Conf.subscriber_set_db) == 0:
        local_sql = sqlite3.connect(__Conf.db_NAME)
        __Conf.subscriber_set_db = set(i[0] for i in local_sql.execute('select user_id from USER;').fetchall())
        #
        # print('sub_SET:::',subscriber_set_db)
        __Conf.subscriber_set_db.add(int(__Conf.my_access_list[0]))
    if user_id in __Conf.subscriber_set_db:
        return True
    else:
        return False


def check_for_pending_user(message: Message):
    local_sql = sqlite3.connect(__Conf.db_NAME)
    pending_user_set = {int(i) for i in local_sql.execute('select user_id from PENDING_USER;').fetchall()}
    if int(message.from_user.id) in pending_user_set:
        return True
    else:
        return False


def check_for_bloked_user(message: Message):
    local_sql = sqlite3.connect(__Conf.db_NAME)
    bloked_user_set = {int(i) for i in local_sql.execute('select user_id from BLOKED_USER;').fetchall()}
    if int(message.from_user.id) in bloked_user_set:
        return True
    else:
        return False
