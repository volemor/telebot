#! /usr/bin/env python3
# coding: utf-8
# for Orange_pi_PC


import os
print("RUN check start!!!")

####
run_process_name = ['os_pc_plus_telebot.py']
com_line = os.popen('ps axf|grep .py').read()
# print(com_line)

if run_process_name[0] not in com_line:
    os.popen('python3 /root/telebot/os_pc_plus_telebot.py')
    print('Start 0')

