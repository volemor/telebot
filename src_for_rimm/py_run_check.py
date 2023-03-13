#! /usr/bin/env python3
# coding: utf-8
# for rimm

import os

print("RUN check start!!!")

run_process_name = ['menu_bot.py', "divTelebot.py"]
com_line = os.popen('ps axf|grep .py').read()
# print(com_line)

if run_process_name[0] not in com_line:
    os.popen('cd /opt/Py_proj/telebot && nohup python3 menu_bot.py')
    print(f'Start 0:{run_process_name[0]}' )


if run_process_name[1] not in com_line:
    mess = os.popen('cd /opt/Py_proj/telebot && nohup python3 divTelebot.py').read()
    print(f'Start 1:{run_process_name[1]}\n', mess)

# if 'cheker_mes_bot.py' not in com_line:
#     mess = os.popen('cd /root/my_py/telebot/ban_monitor && nohup python3 cheker_mes_bot.py').read()
#     print('Start 2', mess)
