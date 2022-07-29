#! /usr/bin/env python3
# coding: utf-8


"""
телеграмм бот для мониторинга системы 'r'
команды бота - описание:
start - ps axf|grep python3
netstat - netstat 22 port
allrestart- old process killed, make git pull and start new
auth_log - auth_log
test - test
uptime - uptime
"""

import os
import telebot
from telebot.types import Message
from tendo import singleton
import time, datetime
from secret_bot import secrets_bot_token, my_access_list

me = singleton.SingleInstance()  ### проверка на работу и запуск альтернативной версии скрипта - чтоб не задвоялась

# проверка собстенными силами.. не всегда может сработать - имя поменять и все..

print("Start telebot riga")
bot = telebot.TeleBot(secrets_bot_token)
""" бот для запуска на линуксе и мониторинга """


def check_for_access(name: str):
    if str(name) in my_access_list:
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def start(message: Message):
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
def nenstat_status(message: Message):
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
def allrestart(message: Message):
    if check_for_access(message.from_user.id):
        kill_line = ''
        for line in os.popen('ps -axf|grep .py').read().split('\n'):
            if 'telegramm_bot_for_riga.py' in line:
                print(line.split()[0])
                kill_line += line.split()[0] + ' '
        print('kill_line:', kill_line)
        bot.send_message(message.chat.id, f'old process [{kill_line}] killed, make git pull and start new')
        os.popen(f'nohup /home/dmitry/start_telebot.bat && kill {kill_line}').read()


@bot.message_handler(commands=['test'])
def test_test(message: Message):
    if check_for_access(message.from_user.id):
        bot.send_message(message.chat.id, f'you in access list')
    else:
        bot.send_message(message.chat.id, f'not for you')


def save_exeption(_ex: str):
    with open('telebot_ex.log', 'a') as file:
        file.writelines(_ex + '\n')


@bot.message_handler(commands=['auth_log'])
def auth_log(message: Message):
    if check_for_access(message.from_user.id):
        my_mess = auth_log_analyser(message)
        bot.send_message(message.chat.id, f'{my_mess}')
    else:
        bot.send_message(message.chat.id, f'not for you')


@bot.message_handler(commands=['uptime'])
def uptime(message):
    if check_for_access(message.from_user.id):
        if os.name != 'nt':
            bot.send_message(message.chat.id, f"{os.popen('uptime').read()}")
    else:
        bot.send_message(message.chat.id, f'not for you')


def auth_log_analyser(message):
    count_fail = 0
    fail_list = []
    filename = '/var/log/auth.log'
    log_list = os.listdir('/var/log/')
    if 'auth.log' in log_list:
        with open(filename, mode='r') as file:
            for line in file:
                if 'Failed password' in line:
                    fail_list.append([*line.split()[:3], line.split()[-4]])
                    count_fail += 1
    else:
        return 'log file not found'

    hack_count = {ip_item[3]: 0 for ip_item in fail_list}
    for my_item in hack_count.keys():
        counting = 0
        for list_item in fail_list:
            if my_item in list_item:
                counting += 1

        hack_count[my_item] = counting
    hach_ip_message = 'auth.log status:\n'
    for h_key, h_item in hack_count.items():
        hach_ip_message += f'hackers ip [{h_key}] try [{h_item}]\n'
        # print(f'hackers ip [{h_key}] try [{h_item}]')
    hach_ip_message += f'try [{count_fail}] from unique address [{len(hack_count)}]\n\n'
    # print(f'try [{count_fail}] from unique address [{len(hack_count)}]')

    warning_status = []
    for my_item in hack_count.keys():
        delta_time = []
        for time in fail_list:
            if my_item in time[3]:
                delta_time.append(time)
        for index_d in range(len(delta_time) - 1):
            h, m, s = delta_time[index_d][2].split(':')
            hl, ml, sl = delta_time[index_d + 1][2].split(':')
            if (datetime.time(hour=int(hl), minute=int(ml), second=int(sl)).second
                - datetime.time(hour=int(h), minute=int(m), second=int(s)).second) < 4:
                warning_status.append((my_item, delta_time[index_d][:3]))
        # print('row time---', my_item, delta_time)
    # print('warn', warning_status)
    for hack_ip, h_time in warning_status:
        hach_ip_message += f'IP:{hack_ip}:{h_time}\n'
        print(hack_ip, h_time)
    return hach_ip_message


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        save_exeption(_ex)
    time.sleep(100)
