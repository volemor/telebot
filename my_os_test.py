#! /usr/bin/env python3
# coding: utf-8

# my telegramm bot
"""
телеграмм бот для мониторинга системы 'ban'
команды бота - описание:
start - ps axf|grep python3
up_log - update_log
netstat - netstat 22 port
info - user info
bot_modul_update - подгрузка модулей
tiker_report_status - report_status
allrestart - old process killed, make git pull and start new
sendmefile * - send file


command:
start - ps axf|grep python3
up_log - update_log
report_status - report status
sendmefile - send last report
netstat - netstat 22 port
info - user info

"""

import os
import telebot
from telebot.types import Message
from tendo import singleton
import time
import datetime
from sqlalchemy import create_engine
from my_os_test_config import *

db_connection = create_engine(sql_login, connect_args={'connect_timeout': 10})
import pandas as pd

if os.name == 'nt': 
    proj_path = 'W:\\My_Python\\stock_update'
    print("start from WINDOWS")
    exit()
else:
    proj_path = '/mnt/1T/opt/gig/My_Python/stock_update/'
    print("start from LINUX")

me = singleton.SingleInstance()  ### проверка на работу и запуск альтернативной версии скрипта - чтоб не задвоялась

processoutput = os.popen("ps -axf").read()
my_list = processoutput.split('\n')
count_my_prog = 0
for index in my_list:
    if 'python3' in index:
        # my_process_py += index + '\n'
        if 'my_os_test.py' in index:
            count_my_prog += 1
        if count_my_prog == 2:
            print('programm allready run!!!')
            exit()


def my_monitor():
    '''
    программа для мониторинга запущенных процессов в системе.
    если нужного процесса нет - то.... пробуем запустить, или прочитать лог.. и по итогам может помощь позвать?? телеграммом.
    наверное запускается через крон -
    пока прототип
    '''
    processoutput = os.popen("ps -axf").read()
    # print(processoutput.split('\n'))
    my_list = processoutput.split('\n')
    netstat_my = os.popen('netstat -antp').read().split('\n')
    for index in netstat_my:
        pass
        print(index)
    my_tail_up_log = os.popen('tail -30 ./update-sql.log').read()
    # print(type(my_tail_up_log))


def save_user_info(message):
    log_contact = f'id:[{message.from_user.id}] first_name [{message.from_user.first_name}]'
    with open('telebot.log', 'a') as file_log:
        file_log.write(log_contact + '\n')
    print(log_contact)


def save_exeption(exeption):
    with open('telebot_ex.log', 'a') as file_log:
        file_log.write(f'[{datetime.datetime.today()}]' + str(exeption) + '\n')



bot = telebot.TeleBot(telegramm_token)
""" бот для запуска на линуксе и мониторинге """


def save_name_to_log(message, modul:str):
    with open('telebot.log', 'a') as file_log:
        file_log.write(f'[{datetime.datetime.today()}] name_id:[{message.from_user.first_name}]- {modul}\n')


def check_for_access(message):
    if str(message.from_user.id) in my_access_list:
        save_name_to_log(message, 'access')
        return True
    else:
        return False

# check_for_access(message.from_user.id)


def check_for_subscriber_list(message, modul:str):
    if str(message.from_user.id) in subscriber_list:
        save_name_to_log(message, modul)
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def start(message: Message):
    # save_user_info(message)
    if check_for_access(message):
        my_process_py = ''
        processoutput = os.popen("ps -axf").read()
        my_list = processoutput.split('\n')
        for index in my_list:
            if '.py' in index:
                my_process_py += index + '\n'
        bot.send_message(message.chat.id, my_process_py)
    else:
        bot.send_message(message.chat.id, 'запуск прошел успешно')


@bot.message_handler(commands=['up_log'])
def update_log_status(message: Message):
    if check_for_access(message):
        bot.send_message(message.chat.id, os.popen('tail -19 /root/update-sql.log').read())
    else:
        bot.send_message(message.chat.id, 'все ок')


@bot.message_handler(commands=['netstat'])
def nenstat_status(message: Message):
    if check_for_access(message):
        my_process_py = ''
        processoutput = os.popen("netstat -antp").read()
        my_list = processoutput.split('\n')
        for index in my_list:
            if 'ESTABLISHED' in index and ':22' in index:
                my_process_py += index + '\n'
        if len(my_process_py) == 0:
            my_process_py = 'сейчас нет соединений по 22 порту'
        bot.send_message(message.chat.id, my_process_py)
    else:
        bot.send_message(message.chat.id, 'нет соединений')


@bot.message_handler(commands=['info'])
def user_info(message: Message):
    if check_for_access(message):
        log_contact = f'id:[{message.from_user.id}] first_name [{message.from_user.first_name}]'
        print(log_contact)
        bot.send_message(message.chat.id, message)
    else:
        bot.send_message(message.chat.id, 'нет инфы')


@bot.message_handler(commands=['bot_modul_update'])
def update_modul(message: Message):
    if check_for_access(message):
        bot.send_message(message.chat.id, 'дополнительные модули подгружены')
    else:
        bot.send_message(message.chat.id, 'дополнительные модули не найдены')


@bot.message_handler(commands=['binance_log'])
def bin_log(message: Message):
    if check_for_access(message):
        sql_login = 'mysql+pymysql://binanse:binanse_pass@192.168.0.118/binance'
        db_connection = create_engine(sql_login, connect_args={'connect_timeout': 10})
        sql_message = 'select * from hist_data'
        df = pd.read_sql(sql_message, con=db_connection)
        new_mes = "[7] последних записей в базе данных:\n"
        mes = df['date_time'].tail(7).to_list()
        for item in mes:
            new_mes += ''.join(item)
            new_mes += ''.join('\n')
        bot.send_message(message.chat.id, new_mes)
    else:
        bot.send_message(message.chat.id, 'дополнительные модули не найдены')


@bot.message_handler(commands=['tiker_report_status'])
def user_info(message: Message):
    my_mes = 'tiker_report_status \n'
    if check_for_access(message):
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
        bot.send_message(message.chat.id, my_mes)
    else:
        bot.send_message(message.chat.id, 'нет инфы')

# set.intersection()
@bot.message_handler(commands=['allrestart'])
def allrestart(message: Message):
    if check_for_access(message):
        kill_line = ''
        for line in os.popen('ps -axf|grep .py').read().split('\n'):
            if 'my_os_test.py' in line:
                print(line.split()[0])
                kill_line += line.split()[0] + ' '
        print('kill_line:', kill_line)
        bot.send_message(message.chat.id, f'old process [{kill_line}] killed, make git pull and start new')
        os.popen(f'nohup /root/mytelebot_start.bat && kill {kill_line}').read()


@bot.message_handler(commands=['sendmefile'])
def sendmefile(message: Message):
    '''send any file'''
    path_for_telebot = '/mnt/1T/opt/gig/My_Python/st_US/otchet/'
    def sender(key: str):
        dir_list = os.listdir(path_for_telebot)
        otchet_all = [name for name in dir_list if key in name]
        otchet_all.sort()
        if len(otchet_all) > 0:
            with open(path_for_telebot + otchet_all[-1], 'rb') as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.send_message(message.chat.id, 'file not found.. sorry')

    if check_for_subscriber_list(message, 'sendmefile'):
        spl = message.text.split()
        if len(spl) > 1:
            if 'all' in spl[1]:
                sender('all')
            elif 'd' in spl[1]:
                sender('d')
            elif '?' in spl[1]:
                dir_list = os.listdir(path_for_telebot)
                otchet_all = [name for name in dir_list if 'all' in name]
                otchet_d = [name for name in dir_list if 'd' in name]
                otchet_d.sort()
                otchet_all.sort()
                bot.send_message(message.chat.id, f'last file:\n{otchet_d[-1]}\n{otchet_all[-1]}')
        else:
            bot.send_message(message.chat.id, 'может добавить ключик..?')
    else:
        bot.send_message(message.chat.id, f'Пожалуй тебя нет в списках.. id ={message.from_user.id}')
        # from my_os_test_config import subscriber_list


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        save_exeption(_ex)
    time.sleep(100)
