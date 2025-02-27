import sqlite3
import data.config


class DesksDB:
    '''Низкоуровневый класс для работы с бд Desks (росто ф)'''
    def __init__(self, path_to_db=data.config.path_to_db):
        self.path_to_db = path_to_db
        self.create_table_of_desks()

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()

        connection = self.connection
        # connection.set_trace_callback(logger)
        cursor = connection.cursor()
        cursor.execute(sql, parameters)
        data = None

        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()

        return data

    def create_table_of_desks(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Desks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name varchar unique
            );
            """
        self.execute(sql, commit=True)

    def add_desk(self, name):
        sql = "INSERT INTO Desks(name) VALUES(?)"
        parameters = (name,)
        self.execute(sql, parameters=parameters, commit=True)
        return True

    def select_all_desks(self):
        sql = 'SELECT * FROM Desks'
        return self.execute(sql, fetchall=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        # используется для создания sql команды с нужными параметрами для команды ниже
        sql += ' AND '.join([
            f"{item} = ?" for item in parameters.keys()
        ])
        return sql, tuple(parameters.values())

    def select_desk(self, **kwargs):
        sql = 'SELECT * FROM Desks WHERE '
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters, fetchall=True)
        # пример использования команды select_desk(id=131, name='JoJo')

    def count_desks(self):
        return self.execute("SELECT COUNT(*) FROM Desks;", fetchone=True)[0]

    def update_any_info_about_desk(self, desk_id, thing_to_change, new_data):
        result = self.select_desk(id=desk_id)
        if not result:
            return f'Доски {desk_id} не существует, проверьте правильность id'

        sql = f"UPDATE Desks SET {thing_to_change}=? WHERE id=?"
        self.execute(sql, parameters=(new_data, desk_id), commit=True)
        return


    def del_desk(self, desk_id):
        zxc = self.select_desk(id=desk_id)

        if len(zxc) != 0:
            self.execute("DELETE FROM Desks WHERE id=?", (desk_id,), commit=True)

            columns_id = self.execute("SELECT id FROM Columns WHERE desk_id=?", (desk_id,), fetchall=True)
            columns_id = [i[0] for i in columns_id]  # [10, 11, 12, 13, 14, 17]
            self.execute("DELETE FROM Columns WHERE desk_id=?", (desk_id,), commit=True)

            for i in range(len(columns_id)):
                self.execute("DELETE FROM Cards WHERE column_id=?", (columns_id[i],), commit=True)

            return True
        else:
            return False