import io
import pdfplumber
import pandas as pd
from datetime import datetime, timedelta
import telebot
from tendo import singleton
import requests as req
# from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time, shutil
from divTelebot_config import *  # файл с переменными --secret_token - токен телеграмм бота, my_access_list - список доступа - пока отклбчено

me = singleton.SingleInstance()  ### проверка на работу и запуск альтернативной версии скрипта - чтоб не задвоялас

bot = telebot.TeleBot(secret_token)
"""Бот расчета размера оплаты налогов в РФ по дивидендам иностранных компаний, по отчетам БКС (за 2021 год) 
в идеале для формирования отчета в налоговую нужны:
(Наиенование эмитента), (дата выплаты), (размер выплаченных дивидендов),  (размер уплаченных налогов) 
и итоговую табличку нужно делать в таком виде.. 

при расчете налогов учитывается только те тикеры, где удержан 10% налог,
там где 30% - не учитывается - доплачивать налоги в РФ не нужно, иначе нужно доплатить 3%. 

"""


def load_usd_curs():
    '''качаем актуальные курсы'''
    # TODO: сделать загрузку с сайта цб
    url_name_2 = f"http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/12/2021&date_req2={datetime.today().date().strftime('%d/%m/%Y')}&VAL_NM_RQ=R01235"
    # url_name_2 = f"http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/2022&date_req2=23/12/2022&VAL_NM_RQ=R01235"
    data_2 = req.post(url=url_name_2, stream=True)
    # print(data_2.content)
    with open('usd_r.xml', 'wb') as file:
        file.write(data_2.content)

    rc_df = pd.DataFrame(columns=['data', 'curs'])
    tables = ET.parse('usd_r.xml')
    for item in tables.findall('Record'):
        # print(item.attrib['Date'], item.find('Value').text)
        rc_df = pd.concat([rc_df, pd.DataFrame([[item.attrib['Date'], item.find('Value').text]], columns=['data', 'curs'])])

    # print(rc_df)
    rc_df.to_excel("RC.xlsx", index=False, sheet_name='RC')


load_usd_curs()
# exit()


def check_for_access(name):
    if str(name) in my_access_list:
        return True
    else:
        return False


def pdf_calc(pdf_io, message=False):  # False -  на случай если вызывать модуль не из телеги.. или еще почему
    pdf = pdfplumber.open(io.BytesIO(pdf_io))

    try:
        cb_df = pd.read_excel(f'{proj_path}RC.xlsx', sheet_name='RC',
                              engine='openpyxl')  # курсы валют по ЦБ за нужный год
        print(cb_df)
    except Exception as _ex:
        print('[error]:', _ex)
        load_usd_curs()
        save_exeption(_ex)

    my_list = []

    def make_lost_data(df):  # дополняем список курсов $ пропущенными данными с учетом выходных
        day_start = datetime(datetime.today().year - 2, 12, 1)
        # print(day_start, df.columns, df)
        local_day = day_start
        curss = df.loc[0]['curs']
        while local_day != datetime(datetime.today().year, 1, 1):
            if len(df[df['data'] == local_day.strftime('%d.%m.%Y')]['curs'].values) == 1:
                filter = df['data'] == local_day.strftime('%d.%m.%Y')
                curss = df[filter]['curs'].values[0]
                # print(curss, local_day.strftime('%d.%m.%Y'))
            else:
                df.loc[len(df.index)] = [local_day.date().strftime('%d.%m.%Y'), curss]
                # df.loc[len(df.index)] = [1, local_day, curss, 'tnew']
            local_day += timedelta(days=1)
            # print(local_day)
        df['data'] = pd.to_datetime(df['data'], format='%d.%m.%Y')
        df.sort_values(by=['data'], inplace=True)
        return df

    pages = pdf.pages
    # print('Pages::',pages)
    # print(pdf.pages[0].extract_text())
    if 'Компании БКС' in pdf.pages[0].extract_text():
        # print('________________________ start')
        cb_df = make_lost_data(cb_df)
        # print('cb_df::',cb_df)
        cb_df.set_index(['data'], inplace=True)
        name_comp_list = []
        if message != False:
            bot.send_message(message.chat.id, 'формат БКС, пробуем считать')
        for page in pages:
            for line in page.extract_text().split('\n'):
                if len(line) > 1:
                    if 'Page' not in line:
                        local_ll = line.strip().split()
                        if 'Наименование Эмитента' in line:
                            my_list.append(local_ll[2:])
                        if 'Дата выплаты' in line:
                            date = datetime.strptime(local_ll[-1], '%d.%m.%Y').date()
                            my_list.append(date)
                        if 'Общая сумма начисленных денежных средств' in line:
                            my_list.append(local_ll[-1])
                        if 'Основная ставка налога' in line:
                            my_list.append(local_ll[-1])
                        if 'Оплата дивидендов,' in line or 'Погашение купона,' in line:
                            name_comp_list.append(local_ll[4:])
    else:
        bot.send_message(message.chat.id, 'Не та кодировка PDF - не формат БКС, загрузите верный файл')
        if message != False:
            bot.send_message(message.chat.id, 'Не та кодировка PDF - не формат БКС, загрузите верный файл')
        return False
    my_dict = {}
    for index, key, comp_loc_name in zip(range(0, len(my_list), 4), range(len(my_list) // 4), name_comp_list):
        my_dict[key] = [my_list[index], my_list[index + 1], my_list[index + 2], my_list[index + 3]]
        print(my_dict[key]) #пока отключили
    new_name_comp_list = []
    for ind in name_comp_list:
        my_loc = ''
        for local_list in ind:
            my_loc += local_list + ' '
        new_name_comp_list.append(my_loc)
    summa_n = 0
    summa_r = 0
    df_div_calc_tax = pd.DataFrame(
        columns=['name', 'date_pay', 'dividend($) with tax', 'CB_curs (rub)', 'dividend (rub)', 'tax 3% (rub)'])
    for num, key in enumerate(my_dict.keys()):
        if my_dict.get(key)[-1] != '13':
            if my_dict.get(key)[-1] == '10':
                date_ii = pd.to_datetime(my_dict.get(key)[1])
                cur_curs = float(cb_df[cb_df.index == date_ii]['curs'].values[0].replace(',', '.'))
                if ',' in my_dict.get(key)[2]:
                    value_loc = float(my_dict.get(key)[2].replace(',', '.'))
                    summa_n += value_loc
                    summa_r += value_loc * cur_curs
                else:
                    value_loc = int(my_dict.get(key)[2])
                    summa_n += value_loc
                    summa_r += value_loc * cur_curs
                df_div_calc_tax.loc[len(df_div_calc_tax.index)] = [new_name_comp_list[num], date_ii, value_loc,
                                                                   cur_curs, round(value_loc * cur_curs,2),
                                                                   round(value_loc * cur_curs * 0.03,2)]
            if my_dict.get(key)[-1] == '30':
                date_ii = pd.to_datetime(my_dict.get(key)[1])
                cur_curs = cb_df[cb_df.index == date_ii]['curs'].values[0]
                if ',' in my_dict.get(key)[2]:
                    value_loc = float(my_dict.get(key)[2].replace(',', '.'))
                    summa_n += value_loc
                    summa_r += value_loc * cur_curs
                else:
                    value_loc = int(my_dict.get(key)[2])
                    summa_n += value_loc  #########
                    summa_r += value_loc * cur_curs
                df_div_calc_tax.loc[len(df_div_calc_tax.index)] = [new_name_comp_list[num], date_ii, value_loc,
                                                                   cur_curs, round(value_loc * cur_curs,2),
                                                                   round(value_loc * cur_curs * 0.0,2)]
    stik_div_summ = {}  # суммируем для каждого тикера полученные дивиденды
    for name in df_div_calc_tax.index:
        if df_div_calc_tax.at[name, 'name'] not in stik_div_summ:
            stik_div_summ[df_div_calc_tax.at[name, 'name']] = round(df_div_calc_tax.at[name, 'dividend($) with tax'], 2)
        else:
            stik_div_summ[df_div_calc_tax.at[name, 'name']] += round(df_div_calc_tax.at[name, 'dividend($) with tax'],
                                                                     2)
    cumm_div_for_mess = ''
    for key_m in stik_div_summ.keys():
        cumm_div_for_mess += f'{key_m} {round(stik_div_summ[key_m], 2)}$ \n'
    if message != False:
        bot.send_message(message.chat.id, f"Суммарно полученные дивиденды по тикерам \n {cumm_div_for_mess}")
    print('df_div_calc_tax::',df_div_calc_tax)
    return df_div_calc_tax


def save_exeption(_ex):
    with open(proj_path + 'div_telebot_ex.log', 'a') as file:
        file.writelines(str(_ex) + '\n')


def save_user_info(message):
    log_contact = f'[{datetime.today()}] id:[{message.from_user.id}] first_name [{message.from_user.first_name}]'
    with open(proj_path + 'Divtelebot_visitors.log', 'a') as file_log:
        file_log.write(log_contact + '\n')
    # print(log_contact)


@bot.message_handler(content_types='document')
def check_doc_type(message):
    if message.document.mime_type == 'application/pdf':
        save_user_info(message)
        file_info = bot.get_file(message.document.file_id)
        file = bot.download_file(file_info.file_path)  ### файл из бота для сохранения в режиме wb
        bot.send_message(message.chat.id, 'проверяем...')
        df_div_calc_tax = pdf_calc(file, message)
        if type(df_div_calc_tax) == type(pd.DataFrame()):
            file_streem = io.BytesIO()
            df_div_calc_tax.to_excel(file_streem)
            file_streem.name = 'отчет по дивидендам.xlsx'
            bot.send_message(message.chat.id,
                             f"по этому отчету надо заплатить {round(df_div_calc_tax['tax 3% (rub)'].sum(), 2)} рублей налогов")
            bot.send_document(message.from_user.id, document=file_streem.getvalue(),
                              visible_file_name='отчет по дивидендам.xlsx', caption='отчет по дивидендам.xlsx')

    else:
        bot.send_message(message.chat.id, f"отправьте pdf..")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Бот расчета оплаты налогов в РФ по дивидендам иностранных компаний, по отчетам БКС (за 2021 год). \n Загрузите pdf файл 'VyplataDohoda ........pdf'  ")


while True:
    try:
        print('start BOT')
        bot.polling(none_stop=True)
    except Exception as _ex:
        print('[errror]:::',_ex)
        save_exeption(_ex)
    time.sleep(25)
