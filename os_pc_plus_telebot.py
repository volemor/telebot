'''
telegramm bot для мониторинга работы orange pi pc plus

смотрил логи бинанс ботов, ...
jr

'''
import os, time, datetime
from tendo import singleton
import telebot

from os_pi_plus_secure import *

import pandas as pd

me = singleton.SingleInstance()

bot = telebot.TeleBot(secret_bot_token)
print("start Ok")


def check_accesss(name):
    if str(name) in my_access_list:
        return True
    else:
        return False


@bot.message_handler(commands=['b1'])
def bin_bot_log_list(message):
    if check_accesss(message.from_user.id):
        bot.send_message(message.chat.id, os.popen('tail -10 /root/binance_main/bot_1.log').read())
    else:
        bot.send_message(message.chat.id, 'not found')


@bot.message_handler(commands=['b1_json'])
def bin_bot_deal_log_list(message):
    if check_accesss(message.from_user.id):
        mes_data = ''
        for line in os.popen('tail -10 /root/binance_main/bot_1_deal_log.json').read().split('\n'):
            data_l = line.split(',')
            new_data = ''
            if len(data_l) > 2:
                # print(data_l)
                m = [1, 2, -3, -2, -1]
                for i in m:
                    new_data += data_l[i] + ' '
            else:
                new_data += data_l[0]
            new_data += '\n'
            mes_data += new_data
        bot.send_message(message.chat.id, mes_data)
    else:
        bot.send_message(message.chat.id, 'not found')


@bot.message_handler(commands=['python'])
def python_process(message):
    if check_accesss(message.from_user.id):
        my_process_py = ''
        for index in os.popen("ps -axf").read().split('\n'):
            if '.py' in index:
                my_process_py += index + '\n'
        if 'bin_bot1.py' in my_process_py and 'os_pc_plus_telebot.py' in my_process_py:
            my_process_py += 'ALL modul are runing.. OK\n'
        bot.send_message(message.chat.id, my_process_py)
    else:
        bot.send_message(message.chat.id, 'not found')


@bot.message_handler(commands=['start'])
def start(message):
    print('start')
    bot.send_message(message.chat.id, 'test complete')


@bot.message_handler(commands=['start_binbot1'])
def start(message):
    if check_accesss(message.from_user.id):
        for line in os.popen('ps -axf|grep .py').read().split('\n'):
            kill_line = ''
            if 'bin_bot1.py' in line or 'os_pc_plus_telebot.py' in line:
                kill_line += line.split()[0] + ' '
        bot.send_message(message.chat.id, f'old process [{kill_line}] killed, make git pull and start new')
        os.popen(f'kill {kill_line} && /root/bot1_start.bat').read()
        # if 'bin_bot1.py' not in os.popen("ps -axf").read():
        #     os.popen('/root/bot1_start.bat').read()
        # for index in os.popen("ps -axf").read().split('\n'):
        #     if 'bin_bot1.py' in index:
        #         pid = index.split()[0]
        # bot.send_message(message.chat.id, f'old process [{line_s}] killed, make git pull and start new [{pid}]')
    # bot.send_message(message.chat.id, 'test complete')


while True:
    try:
        print('tet')
        bot.polling(none_stop=True)
    except Exception as _ex:
        print(_ex)
        time.sleep(20)