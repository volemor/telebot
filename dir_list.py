import pandas as pd
import os
import openpyxl

file_name = 'dir_l_06.07.2022.xlsx'
df = pd.read_excel(file_name, engine='openpyxl')
print(df.columns)
dir_list = df['shifr'].to_list()
print('rooooot::', dir_list, '\n')
root_dir = []
root_dir_d = {}
count = 0
count_pod = 0
last_livel_name = []
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
exit()
test = {'раздел 1':
            {'подраздел1':
                 {'часть1':
                      ['кж1', 'кж2'],
                  'часть2':
                      ['кж1', 'кж2']},
             'подраздел2':
                 ['кж1', 'кж2']}}
print(test)
print(test.keys())
print(test.items())
for item in test['раздел 1']:
    print(item)
    for item_l2 in test['раздел 1'][item]:
        print('---', item_l2)
        if '2' not in item:
            for item_l3 in test['раздел 1'][item][item_l2]:
                print('-----', item_l3)

# [('раздел 1', {'подраздел1': {'часть1': ['кж1', 'кж2'], 'часть2': ['кж1', 'кж2']}, 'подраздел2': ['кж1', 'кж2']})]
# print(root_dir_d)
'''
{'раздел 1': {'ИССО': {'подраздел1': ['кж1', 'кж2']}}} 
 {'раздел 1': {'ИССО': ['кж1', 'кж2']}}
 {'раздел 1': {'подраздел': ['кж1', 'кж2']}, 'подраздел2': ['кж1', 'кж2']}}
'''
