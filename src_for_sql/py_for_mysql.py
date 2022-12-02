#!/usr/bin/python3
import os
from datetime import datetime

today = datetime.today().date()
save_dir = '/mnt/60G'
file_name = ['hass_db', 'hist_data']

print(today)
for base_name in file_name:
    # command = f"/usr/bin/mysqldump -uroot -pbananapi {base_name} > {save_dir}/{base_name}-{today}.sql"
    command = '/usr/bin/mysqldump  -uroot -pbananapi ' + str(base_name) + '> /mnt/60G/hist_data-' + str(today) + '.sql'
    print(command)
    os.system(command)
# command1 = '/usr/bin/mysqldump  -uroot -pbananapi hist_data > /mnt/60G/hist_data-' + str(today) + '.sql'
# os.system(command1)

file_list = {}
for item in file_name:
    file_list[item] = [name for name in os.listdir(save_dir) if os.path.isfile(name) and item in name]

for item in file_name:
    if len(file_list[item]) > 4:
        for del_name in file_list[item][:-2]:
            os.remove(os.path.join(save_dir, del_name))
