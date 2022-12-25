from secret import Conf as __Conf
import sqlite3, datetime


def check_local_data_base(bot):
    """
    add local db for users if not open
    :return:
    """

    local_sql = sqlite3.connect(__Conf.db_NAME)
    tab_name = {j for i in local_sql.execute("select name from sqlite_master where type = 'table';").fetchall() for j in
                i}
    print('\nTAB NAME:::', tab_name)
    if 'USER' not in tab_name:
        local_sql.execute("""
            CREATE TABLE USER (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_group TEXT,
                user_activation INTEGER, 
                user_date_act timestamp
            );
        """)

        sql = 'INSERT INTO USER (user_id, user_group,user_activation, user_date_act) values( ?, ?, ?, ?)'
        data = [
            (__Conf.my_access_list[0], 'root', 1, datetime.datetime.strptime('2030/11/25', '%Y/%m/%d')),
        ]
        with local_sql:
            local_sql.executemany(sql, data)
        bot.send_message(__Conf.my_access_list[0], f'CREATE TABLE USER in db')

    else:
        mess_add = local_sql.execute('select user_id from USER;').fetchall()
        bot.send_message(__Conf.my_access_list[0], f'USER in db:{mess_add}')

    if "PENDING_USER" not in tab_name:
        local_sql.execute("""
                    CREATE TABLE PENDING_USER (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,              
                        user_date_request timestamp
                    );
                """)
        local_sql.commit()
        bot.send_message(__Conf.my_access_list[0], f'CREATE TABLE PENDING_USER in db')
    else:
        mess_add = local_sql.execute('select user_id from PENDING_USER;').fetchall()
        bot.send_message(__Conf.my_access_list[0], f'PENDING_USER in db:{mess_add}')
    if "BLOKED_USER" not in tab_name:
        local_sql.execute("""
                    CREATE TABLE BLOKED_USER (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,              
                        user_date_request timestamp
                    );
                """)
        local_sql.commit()
        bot.send_message(__Conf.my_access_list[0], f'CREATE TABLE BLOKED_USER in db')
    else:
        mess_add = local_sql.execute('select user_id from BLOKED_USER;').fetchall()
        bot.send_message(__Conf.my_access_list[0], f'BLOKED_USER in db:{mess_add}')



