#!/usr/bin/python3
import os
from datetime import datetime

today = datetime.today().date()

print(today)
command = '/usr/bin/mysqldump  -uroot -pbananapi hass_db > /mnt/60G/hassio_db-' + str(today) + '.sql'
os.system(command)
command1 = '/usr/bin/mysqldump  -uroot -pbananapi hist_data > /mnt/60G/hist_data-' + str(today) + '.sql'
os.system(command1)

save_dir = '/mnt/60G'
file_name = ['hassio_db', 'hist_data']
file_list = {}
for item in file_name:
    file_list[item] = [name for name in os.listdir(save_dir) if os.path.isfile(name) and item in name]

for item in file_name:
    if len(file_list[item]) > 4:
        for del_name in file_list[item][:-2]:
            os.remove(os.path.join(save_dir, del_name))
