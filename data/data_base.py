from collections import namedtuple
import sqlite3
import pandas as pd


DB_FILE_PATH = 'data/test.db'


_Table = namedtuple('_Table', 'columns data')


LABEL = 'label'
VALUE = 'value'


#@retry(wait=wait_exponential(multiplier=2, min=1, max=10), stop=stop_after_attempt(5))
def try_connection():
    with DataBase() as db:
        db.check_connection()

# Threads can not share database connections.
class DataBase():
    #def __add__(self, other):

    def __init__(self):
        self._con = None

    def __enter__(self):
        self._con = sqlite3.connect(DB_FILE_PATH)
        #self._con.execute('PRAGMA foreign_keys = ON;')
        return self

    def __exit__(self, type, value, traceback):
        self._con.close()
        #print()
        #print('EXIT DataBase: Type <{}>, Value <{}>'.format(type, value))
        #print('     Traceback:', traceback)
        #print()


    def _get_options(self, query):
        options = list()
        for id, name in self._con.execute(query):
            options.append({VALUE: id, LABEL: name})

        return options


    def get_transaction_lines(self, transaction_id):
        try:
            transaction_id = int(transaction_id)

        except Exception as e:
            transaction_id = 1164

        query = ('SELECT * FROM line_item '
                 'WHERE transaction_id = {}'.format(transaction_id))

        df = pd.read_sql_query(query, self._con)

        data = df.to_dict('records')
        return data

    def get_account_options(self):
        query = 'SELECT id, name FROM account ORDER BY closed, type_id, name'
        return self._get_options(query)

    def get_account_type_options(self):
        query = 'SELECT id, name FROM account_type ORDER BY name'
        return self._get_options(query)

    def get_envelope_options(self):
        query = 'SELECT id, name FROM envelope ORDER BY closed, name'
        return self._get_options(query)

    def get_line_type_options(self):
        query = 'SELECT id, name FROM line_type ORDER BY name'
        return self._get_options(query)


    def check_connection(self):
        try:
            self.con.execute("SELECT 1")
            print("Connection to database successful")

        except Exception as e:
            print("Connection to database failed <{}>".format(e))
