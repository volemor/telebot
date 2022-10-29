import pandas as pd
import os
import openpyxl

file_name = 'dir_l_06.07.2022.xlsx'
df = pd.read_excel(file_name, engine='openpyxl')
dir_list = df['shifr'].to_list()
root_dir_name = 'LTK2'
livel_key = {0: 'Раздел', 1: "Подраздел", 2: "Часть", 3: '№122211'}
livel_name = {0: '', 1: "", 2: "", 3: '№122211'}

dir_name_list = []

for item in dir_list:
    if livel_key.get(0) in str(item):
        livel_name[0] = str(item)
        livel_name[1] = ''
        livel_name[2] = ''
        os.makedirs(os.path.join(root_dir_name, item), exist_ok=True)
        continue
    if livel_key.get(1) in str(item):
        livel_name[1] = str(item)
        livel_name[2] = ''
        os.makedirs(os.path.join(root_dir_name, os.path.join(livel_name[0], item)), exist_ok=True)
        continue
    if livel_key.get(2) in str(item):
        livel_name[2] = str(item)
        os.makedirs(os.path.join(root_dir_name, os.path.join(livel_name[0], os.path.join(livel_name[1], item))),
                    exist_ok=True)
        continue
    if livel_key.get(3) in str(item):
        s_name = ("\\" + livel_name[2]) if len(livel_name[2]) > 0 else ""
        s_name1 = ("\\" + livel_name[1]) if len(livel_name[1]) > 0 else ""
        dir_name_list.append(f'{livel_name[0]}{s_name1}{s_name}\\{item}')
        os.makedirs(os.path.join(root_dir_name, dir_name_list[-1]), exist_ok=True)

print(len(dir_name_list))

exit()
