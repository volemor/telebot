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


def name_for_dir1():
    root_dir = []
    root_dir_d = {}
    count = 0
    count_pod = 0

    local_dir_list = []

    name_2lvl = []
    name4_2lvl = []

    for item in dir_list:
        if 'Раздел' in str(item):
            if count != 0 and count != 5:
                root_dir.append(item)
                root_dir_d[str(item)] = {}
            else:
                root_dir.append(item)
                root_dir_d[str(item)] = []
            print(f'{item}')
            local_dir_list.append(f'{item}')
            count += 1
            continue
        if count == 2 and "Подраздел" in str(item):
            name_2lvl.append(str(item))
            root_dir_d[root_dir[-1]][str(item)] = {}
            local_dir_list.append(f'{root_dir[-1]}\\{item}')
            continue
        if count == 2 and "Часть" in str(item):
            last_livel_name.append(str(item))
            root_dir_d[root_dir[-1]][str(name_2lvl[-1])][str(item)] = []
            local_dir_list.append(f'{root_dir[-1]}\\{name_2lvl[-1]}\\{item}')
            continue
        if count == 2 and "№122211-" in str(item):
            root_dir_d[root_dir[-1]][str(name_2lvl[-1])][last_livel_name[-1]].append(str(item))
            local_dir_list.append(f'{root_dir[-1]}\\{name_2lvl[-1]}\\{last_livel_name[-1]}\\{item}')
            continue
        if count == 4 and 'ИССО' in str(item):
            name4_2lvl.append(str(item))

        if "№122211-" not in str(item):
            root_dir_d[root_dir[-1]][str(item)] = []
            last_livel_name.append(str(item))
            local_dir_list.append(f'{root_dir[-1]}\\{item}')
            continue
        if "№122211-" in str(item) and 'Раздел 1' not in root_dir[-1] and 'Раздел 6' not in root_dir[-1]:
            root_dir_d[root_dir[-1]][last_livel_name[-1]].append(str(item))
            local_dir_list.append(f'{root_dir[-1]}\{last_livel_name[-1]}\\{item}')
            continue
        if "№122211-" in str(item) and ('Раздел 1' in root_dir[-1] or 'Раздел 6' in root_dir[-1]):
            root_dir_d[root_dir[-1]].append(item)
            local_dir_list.append(f'{root_dir[-1]}\\{item}')
    # for item in root_dir_d.keys():
    #     if 'Раздел 2.' in item:
    #         # print(root_dir_d[item])
    #         print('>',item)
    #         for lvl1 in root_dir_d[item]:
    #             print('-->',lvl1)
    #             for lvl2 in root_dir_d[item][lvl1]:
    #                 print('---->', lvl2)
    #                 # if 'Подраздел 1.' in str(lvl1):
    #                 for lvl3 in root_dir_d[item][lvl1][lvl2]:
    #                     print('-------->>', lvl3)
    print('path:::')
    root_dir_name = 'LTK2'

    print(os.getcwd())
    root_dir_path = os.path.join(os.getcwd(), root_dir_name)

    # os.chdir(root_dir_path)
    print(root_dir_path)
    # print(os.getcwd())
    for item in local_dir_list:
        print(item)

    print('len::', len(local_dir_list))
