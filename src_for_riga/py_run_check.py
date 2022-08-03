#! /usr/bin/env python3
# coding: utf-8
# for Riga


import os
print("RUN check start!!!")


run_process_name = ['telegramm_bot_for_riga.py']
com_line = os.popen('ps axf|grep .py').read()
# print(com_line)

if run_process_name[0] not in com_line:
    os.popen('/root/mytelebot_start.bat')
    print('Start 0')

