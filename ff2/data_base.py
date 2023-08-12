from collections import namedtuple
import sqlite3
import pandas as pd


_Table = namedtuple('_Table', 'columns data')


LABEL = 'label'
VALUE = 'value'


#@retry(wait=wait_exponential(multiplier=2, min=1, max=10), stop=stop_after_attempt(5))
def try_connection():
    with DataBase() as db:
        db.check_connection()

# Threads can not share database connections.
class DataBase():
    def __init__(self, db_file_path):
        self._con = sqlite3.connect(db_file_path)


    def _get_options(self, query):
        options = list()
        for id, name in self._con.execute(query):
            options.append({VALUE: id, LABEL: name})

        return options


    def get_transaction_lines(self, transaction_id):
        try:
            transaction_id = int(transaction_id)

        except Exception as e:
            transaction_id = 16291

        query = ('SELECT * FROM line_item '
                 'WHERE transaction_id = {}'.format(transaction_id))

        df = pd.read_sql_query(query, self._con)

        data = df.to_dict('records')
        s_lines = list()
        d_lines = list()

        for line in data:
            if line['cd'] == 0:
                s_lines.append(line)

            else:
                d_lines.append(line)

        return s_lines, d_lines

    def get_account_options(self):
        query = 'SELECT id, name FROM account ORDER BY closed, account_type_id, name'
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
