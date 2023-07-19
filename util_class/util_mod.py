import sqlite3, datetime


class User_Db():
    """class для управления пользователями в базе данных: добавление, изменение роли, удаление,
    отбражение списка, статуса, проверка вхождения в группы - admin, user, очистка базы данных
    """

    def __init__(self, db_file_name: str, db_table_name: str = "USER"):
        self.db_file_name = db_file_name + ".db"
        # self.table_name = db_table_name.upper()
        import sqlite3
        local_sql = sqlite3.connect(self.db_file_name)
        tab_name = {j for i in local_sql.execute("select name from sqlite_master where type = 'table';").fetchall() for
                    j in i}
        if "USER" not in tab_name:
            local_sql.execute("""
                CREATE TABLE USER (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_group TEXT,
                    user_activation INTEGER, 
                    user_last_date_act timestamp
                );
            """)
        else:
            mess_add = local_sql.execute('select * from USER;').fetchall()
            print(f'init else:[{self.db_file_name}]:', mess_add)

    def useradd(self, user_id: int, user_role: str):
        # user_role :: admin, user
        if user_role.lower() in ['admin', 'user']:
            local_sql = sqlite3.connect(self.db_file_name)
            if local_sql.execute('select user_id from USER;').fetchall().count((user_id,)) == 0:
                sql = 'INSERT INTO USER (user_id, user_group,user_activation, user_last_date_act) values( ?, ?, ?, ?)'
                data = [(user_id, user_role, 1, datetime.datetime.now().date() + datetime.timedelta(days=3650))]
                local_sql.executemany(sql, data)
                local_sql.commit()
                print(f'user_add:mess::{user_id} added')
                return True
            else:
                print(f'user_add:mess: user {user_id} allready add')
                return False
        else:
            print(f'user_add:mess: user {user_id} error role [{user_role}]')
            return False

    def user_list(self):
        import sqlite3
        local_sql = sqlite3.connect(self.db_file_name)
        user_list_loc = [item[0] for item in local_sql.execute('select user_id from USER;').fetchall()]
        print(f'{self.db_file_name} len user_list:mess:{len(user_list_loc)}')
        for item in user_list_loc:
            print('-->:user_id:', item)
        return user_list_loc

    def user_del(self, user_id: int):
        local_sql = sqlite3.connect(self.db_file_name)
        if user_id in [item[0] for item in local_sql.execute('select user_id from USER;').fetchall()]:
            print(f'TRY DEL {user_id}')
            local_sql.execute(f'delete from USER where user_id = "{user_id}";')
            local_sql.commit()
            return True
        else:
            print(f'user {user_id} not in DB')
            return False

    def user_status(self, user_id: int):
        local_sql = sqlite3.connect(self.db_file_name)
        loc_st = local_sql.execute(
            f"select user_activation, user_last_date_act from USER where user_id = {user_id}").fetchone()
        if loc_st:
            loc_st_l = [item for item in loc_st]
            print(f'user {user_id} status :: [{loc_st_l[0] == True}] active before [{loc_st_l[1]}]')
            # print(datetime.datetime.strptime(loc_st_l[1],"%Y-%m-%d"),datetime.datetime.now())
            return loc_st_l[0] == True, datetime.datetime.strptime(loc_st_l[1], "%Y-%m-%d") > datetime.datetime.now()
        else:
            print(f'user {user_id} not found!!')
            return False, False

    def user_ch_role(self, user_id: int, new_role: str):
        """изменение роли пользователя admin, user"""
        if new_role.lower() in ['admin', 'user']:
            local_sql = sqlite3.connect(self.db_file_name)
            if user_id in [item[0] for item in local_sql.execute('select user_id from USER;').fetchall()]:
                print(f'TRY DEL {user_id}')
                local_sql.execute(f'update USER SET user_group = "{new_role}" where user_id = "{user_id}";')
                local_sql.commit()
                print(local_sql.execute('select * from USER;').fetchall())
                return True
        else:
            print(f'user_add:mess: user {user_id} error role [{new_role}]')
            return False

    def ch_user_date_activation(self, user_id: int, new_date: str):
        """изменение даты активации пользователя """
        try:
            date_loc = datetime.datetime.strptime(new_date, "%Y-%m-%d").date()
        except Exception as _ex:
            print('__SOME ERROR DATE:', _ex)
            return False
        if self.user_chk(user_id):
            local_sql = sqlite3.connect(self.db_file_name)
            # print('Old date::', local_sql.execute(f'select user_last_date_act from USER where user_id ="{user_id}" ;').fetchall()[0][0])
            print(f'TRY SET new date for {user_id}={date_loc}')
            local_sql.execute(f'update USER SET user_last_date_act = "{date_loc}" where user_id = "{user_id}";')
            local_sql.commit()
            # print('any_time',local_sql.execute(f'select * from USER where user_id ="{user_id}";').fetchall())
            return True

    def admin_chk(self, user_id: int):
        local_sql = sqlite3.connect(self.db_file_name)
        print(f'user:{user_id} in admin_list:')
        return user_id in [item[0] for item in
                           local_sql.execute('select user_id from USER where user_group = "admin";').fetchall()]

    def user_chk(self, user_id: int):
        local_sql = sqlite3.connect(self.db_file_name)
        print(f'user:{user_id} in DB:')
        return user_id in [item[0] for item in
                           local_sql.execute('select user_id from USER;').fetchall()]

    def clear(self):
        local_sql = sqlite3.connect(self.db_file_name)
        tab_name = {j for i in local_sql.execute("select name from sqlite_master where type = 'table';").fetchall() for
                    j in i}
        if 'USER' in tab_name:
            local_sql.execute('drop Table USER;')
            local_sql.commit()
            print('table USER droped')
            return True
        return False


def Test_User_Db():
    any = User_Db('aNy')
    any.useradd(12884, 'admin')
    # any.ch_user_date_activation(12884,'2099-1-9')
    # any.user_list()
    # any.user_del(1212)
    # any.user_list()
    any.user_status(124)
    print(any.user_status(12))

    # any.user_ch_role(1212, 'user')
    # print(any.admin_chk(12142))
    # print(any.user_chk(12142342))
    # any.user_list()
    # any.clear()


Test_User_Db()


class Telebot_hadler_func():

    def __init__(self, name: str):
        self.name = name
