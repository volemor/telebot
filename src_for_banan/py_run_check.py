#! /usr/bin/env python3
# coding: utf-8
# for banana

import os

print("RUN check start!!!")

run_process_name = ['my_os_test.py', 'menu_bot.py']
com_line = os.popen('ps axf|grep .py').read()
# print(com_line)

if run_process_name[0] not in com_line:
    os.popen('nohup python3 /root/my_py/telebot/ban_monitor/my_os_test.py')
    print('Start 0')

if run_process_name[1] not in com_line:
    mess = os.popen('nohup cd /root/my_py/telebot/ban_monitor && python3 menu_bot.py ').read()
    print('Start 1', mess)
