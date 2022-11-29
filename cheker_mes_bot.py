import datetime, os, io
import sqlite3
import time
from telebot import types
from telebot.types import Message
import telebot
from secret_cheker import Conf_cheker as __Conf

# from sqlalchemy import create_engine

"""
пробуем сделать бота для группы 
- 1)читать сообщения
2)загружать файлы
3)загружать фото и видео..

    
"""

bot = telebot.TeleBot(__Conf.API_KEY)

print('START cheker_bot')
print(f'список супер доступа:{__Conf.my_access_list}')


def check_local_data_base():
    """
    add local db for users if not open
    :return:
    """

    local_sql = sqlite3.connect(__Conf.db_NAME)
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
            (__Conf.my_access_list[0], 'root', 1, datetime.datetime.strptime('2030/11/25', '%Y/%m/%d')),
        ]
        with local_sql:
            local_sql.executemany(sql, data)
        bot.send_message(__Conf.my_access_list[0], f'CREATE TABLE USER in db')
        mess_add = local_sql.execute('select * from USER;').fetchall()
        bot.send_message(__Conf.my_access_list[0], f'USER in db:{mess_add}')
    if "PENDING_USER" not in tab_name:
        local_sql.execute("""
                    CREATE TABLE PENDING_USER (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,              
                        user_date_request timestamp
                    );
                """)
        local_sql.commit()
        bot.send_message(__Conf.my_access_list[0], f'CREATE TABLE PENDING_USER in db')
    if "BLOKED_USER" not in tab_name:
        local_sql.execute("""
                    CREATE TABLE BLOKED_USER (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,              
                        user_date_request timestamp
                    );
                """)
        local_sql.commit()
        bot.send_message(__Conf.my_access_list[0], f'CREATE TABLE BLOKED_USER in db')


check_local_data_base()


# @bot.message_handler(func=lambda message: message.chat.id == __Conf.group_ID)
# def any_run(message: Message):
#     print(message.from_user.id, message.text)
#     if message.entities is not None:
#         for entity in message.entities:  # Пройдёмся по всем entities в поисках ссылок
#             if entity.type in ["url", "text_link"]:
#                 # Мы можем не проверять chat.id, он проверяется ещё в хэндлере
#                 bot.delete_message(message.chat.id, message.message_id)
#                 bot.send_message(message.chat.id, 'link запрещены')

# @bot.message_handler(func=lambda message: message.chat.id == __Conf.group_ID_in)
# def copy_pdf(message: Message):
#     print(message.chat.id, message.text)
#     if message.entities is not None:
#         for entity in message.entities:  # Пройдёмся по всем entities в поисках ссылок
#             if entity.type in ["url", "text_link"]:
#                 # Мы можем не проверять chat.id, он проверяется ещё в хэндлере
#                 bot.delete_message(message.chat.id, message.message_id)
#                 bot.send_message(message.chat.id, 'link запрещены')


@bot.message_handler(content_types='document')
def copy_pdf(message: Message):
    if message.chat.id == __Conf.group_ID_in:
        print('pdf:->', message)
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)
        bot.send_document(__Conf.group_ID_out, document=message.document.file_id, visible_file_name=message.document.file_name,
                          caption=message.caption)


        # test_dir = os.path.join(os.getcwd(), 'test')
        # with open(f'{os.path.join(test_dir, message.document.file_name)}', 'wb') as file_name:
        #         file_name.write(file)
        #     print(os.listdir(test_dir))




while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        print(f"found Error::{_ex}")
        pass
    # time.sleep(10)
