#!/usr/bin/python3
import os
from datetime import datetime
from secret_pass import Config

today = datetime.today().date()
save_dir = '/opt/backup'
file_name = ['hass_db', 'hist_data']


def make_backup():
    print(today)
    for base_name in file_name:
        command = '/usr/bin/mysqldump ' + str(
            base_name) + f' -u{Config.user} -p{Config.password} ' + f'> {save_dir}/' + str(
            base_name) + '-' + str(
            today) + '.sql'
        print(command)
        save_log(str(command))
        os.system(command)


def save_log(message: str):
    with open('sql_backup.log', 'a') as file:
        mes_loc = f"[{datetime.today()}] {message}"
        file.writelines(mes_loc)


def clean_dir():
    file_list = {}
    for item in file_name:
        file_list[item] = sorted([name for name in os.listdir(save_dir) if item in name])
    print(file_list)
    for item in file_name:
        if len(file_list[item]) > 8:
            for del_name in file_list[item][:-6]:
                os.remove(os.path.join(save_dir, del_name))
                save_log(f"deleted:{del_name}")
                print(f"deleted:{del_name}")


make_backup()
clean_dir()
