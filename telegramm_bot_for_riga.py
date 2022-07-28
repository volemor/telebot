#! /usr/bin/env python3
# coding: utf-8


"""
телеграмм бот для мониторинга системы 'r'
команды бота - описание:
start - ps axf|grep python3
netstat - netstat 22 port

"""

import os
import telebot
from tendo import singleton
import time
from secret_bot import *

me = singleton.SingleInstance()  ### проверка на работу и запуск альтернативной версии скрипта - чтоб не задвоялась

# проверка собстенными силами.. не всегда может сработать - имя поменять и все..
processoutput = os.popen("ps -axf").read()
my_list = processoutput.split('\n')
count_my_prog = 0
for index in my_list:
    if '.py' in index:
        if 'telegramm_bot_for_riga.py' in index:
            count_my_prog += 1
        if count_my_prog == 2:
            print('programm allready run!!!')
            exit()



bot = telebot.TeleBot(secrets_bot_token)
""" бот для запуска на линуксе и мониторинга """


def check_for_access(name):
    if str(name) in my_access_list:
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def start(message):
    if check_for_access(message.from_user.id):
        my_process_py = ''
        processoutput = os.popen("ps -axf").read()
        my_list = processoutput.split('\n')
        for index in my_list:
            if '.py' in index:
                my_process_py += index + '\n'
        bot.send_message(message.chat.id, my_process_py)
    else:
        bot.send_message(message.chat.id, 'запуск прошел успешно')


@bot.message_handler(commands=['netstat'])
def nenstat_status(message):
    if check_for_access(message.from_user.id):
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

@bot.message_handler(commands=['allrestart'])
def allrestart(message):
    if check_for_access(message):
        kill_line = ''
        for line in os.popen('ps -axf|grep .py').read().split('\n'):
            if 'telegramm_bot_for_riga.py' in line:
                print(line.split()[0])
                kill_line += line.split()[0] + ' '
        print('kill_line:', kill_line)
        bot.send_message(message.chat.id, f'old process [{kill_line}] killed, make git pull and start new')
        os.popen(f'nohup /home/dmitry/start_telebot.bat && kill {kill_line}').read()



def save_exeption(_ex: str):
    with open('telebot_ex.log', 'a') as file:
        file.writelines(_ex + '\n')


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        save_exeption(_ex)
    time.sleep(100)
