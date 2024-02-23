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
        command = '/usr/bin/mysqldump ' + str(base_name) + f' -u{Config.user} -p{Config.password} ' + f'> {save_dir}/' + str(
            base_name) + '-' + str(
            today) + '.sql'
        print(command)
        os.system(command)


def clean_dir():
    file_list = {}
    for item in file_name:
        file_list[item] = [name for name in os.listdir(save_dir) if item in name]
    print(file_list)
    for item in file_name:
        if len(file_list[item]) > 4:
            for del_name in file_list[item][:-2]:
                os.remove(os.path.join(save_dir, del_name))


make_backup()
clean_dir()
