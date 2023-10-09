from collections import namedtuple
from enum import Enum

import sqlite3

import pdb


#             | Left    | Right
#             | DEBIT-1 | CREDIT-0
# DEBIT Acc.  |   +     |   -
# CREDIT Acc. |   -     |   +
CREDIT = 0
DEBIT = 1


# Table creation statements
CREATE_ACCOUNT_TYPE_TABLE = '''
    CREATE TABLE account_type(
        id                  INTEGER PRIMARY KEY,
        name                TEXT UNIQUE
        ) STRICT;

    INSERT INTO account_type VALUES (0, " ");
    INSERT INTO account_type VALUES (1, "Income");
    INSERT INTO account_type VALUES (2, "Account");
    INSERT INTO account_type VALUES (3, "Expense");
    '''

CREATE_LINE_TYPE_TABLE = '''
    CREATE TABLE line_type(
        id                  INTEGER PRIMARY KEY,
        name                TEXT UNIQUE
        ) STRICT;

    INSERT INTO line_type VALUES (0, " ");
    INSERT INTO line_type VALUES (1, "Deposit");
    INSERT INTO line_type VALUES (2, "Purchase");
    INSERT INTO line_type VALUES (3, "Transfer");
    INSERT INTO line_type VALUES (4, "Refund");
    INSERT INTO line_type VALUES (5, "Deposit Refund");
    '''

CREATE_LINE_COMPLETE_TABLE = '''
    CREATE TABLE line_complete(
        id                  INTEGER PRIMARY KEY,
        short_name          TEXT UNIQUE,
        name                TEXT UNIQUE
        ) STRICT;

    INSERT INTO line_complete VALUES (0, " ", "Pending");
    INSERT INTO line_complete VALUES (1, "C", "Cleared");
    INSERT INTO line_complete VALUES (2, "R", "Reconciled");
    '''

CREATE_ACCOUNT_TABLE = '''
    CREATE TABLE account(
        id                  INTEGER PRIMARY KEY,
        name                TEXT UNIQUE,
        account_type_id     INTEGER,
        closed              INTEGER,
        credit_debit        INTEGER,
        envelopes           INTEGER
        ) STRICT;

    INSERT INTO account VALUES (0, " ", 0, 0, 0, 0);
    '''

CREATE_ENVELOPE_TABLE = '''
    CREATE TABLE envelope(
        id                  INTEGER PRIMARY KEY,
        name                TEXT UNIQUE,
        favorite_account_id INTEGER,
        closed              INTEGER
        ) STRICT;

    INSERT INTO envelope VALUES (0, " ", 0, 0);
    '''

CREATE_LINE_ITEM_TABLE = '''
    CREATE TABLE line_item(
        id                  INTEGER PRIMARY KEY,
        transaction_id      INTEGER,
        date                TEXT,
        line_type_id        INTEGER,
        account_id          INTEGER,
        description         TEXT,
        confirmation_number TEXT,
        line_complete_id    INTEGER,
        amount              REAL,
        credit_debit        INTEGER
        ) STRICT;
    '''

CREATE_ENVELOPE_ITEM_TABLE = '''
    CREATE TABLE envelope_item(
        id           INTEGER PRIMARY KEY,
        line_item_id INTEGER,
        envelope_id  INTEGER,
        description  TEXT,
        amount       REAL
        ) STRICT;
    '''

CREATE_OFX_ITEM_TABLE = '''
    CREATE TABLE ofx_item(
        id           INTEGER PRIMARY KEY,
        line_item_id INTEGER,
        account_id   INTEGER,
        fit_id       TEXT,
        memo         TEXT,
        data         TEXT
        ) STRICT;
    '''


# Namedtuples for the table rows.
AccountType = namedtuple('AccountType', 'id name')
LineType = namedtuple('LineType', 'id name')
LineComplete = namedtuple('LineComplete', 'id short_name name')
Account = namedtuple('Account', 'id name account_type_id closed credit_debit envelopes')
Envelope = namedtuple('Envelope', 'id name favorite_account_id closed')
LineItem = namedtuple('LineItem', 'id transaction_id date line_type_id account_id description confirmation_number line_complete_id amount credit_debit')
EnvelopeItem = namedtuple('EnvelopeItem', 'id line_item_id envelope_id description amount')
OfxItem = namedtuple('OfxItem', 'id line_item_id account_id fit_id memo data')


# View creation statements
CREATE_ACCOUNT_DETAILS_VIEW = '''
    CREATE VIEW account_details
    AS
    SELECT
        account.id              AS id,
        account.name            AS name,
        account.credit_debit    AS credit_debit,
        account.account_type_id AS account_type_id,
        account.closed          AS closed,
        account.envelopes       AS envelopes,
        account_type.name       AS account_type_name
    FROM
        account
        INNER JOIN account_type ON account.account_type_id = account_type.id
        ;
    '''

CREATE_ENVELOPE_DETAILS_VIEW = '''
    CREATE VIEW envelope_details
    AS
    SELECT
        envelope.id                  AS id,
        envelope.name                AS name,
        envelope.favorite_account_id AS favorite_account_id,
        envelope.closed              AS closed,
        account.name                 AS favorite_account_name
    FROM
        envelope
        INNER JOIN account ON envelope.favorite_account_id = account.id
        ;
    '''

CREATE_LINE_ITEM_DETAILS_VIEW = '''
    CREATE VIEW line_item_details
    AS
    SELECT
        line_item.transaction_id      AS transaction_id,
        line_item.id                  AS id,
        line_item.date                AS date,
        line_item.line_type_id        AS line_type_id,
        line_item.account_id          AS account_id,
        line_item.description         AS description,
        line_item.confirmation_number AS confirmation_number,
        line_item.line_complete_id    AS line_complete_id,
        line_item.amount              AS amount,
        line_item.credit_debit        AS credit_debit,
        line_type.name                AS line_type_name,
        line_complete.short_name      AS complete_short_name,
        account.name                  AS account_name,
        account.credit_debit          AS account_credit_debit
    FROM
        line_item
        INNER JOIN line_type     ON line_item.line_type_id     = line_type.id
        INNER JOIN line_complete ON line_item.line_complete_id = line_complete.id
        INNER JOIN account       ON line_item.account_id       = account.id
        ;
    '''

CREATE_ENVELOPE_ITEM_DETAILS_VIEW = '''
    CREATE VIEW envelope_item_details
    AS
    SELECT
        envelope_item.id          AS id,
        envelope_item.description AS description,
        envelope_item.amount      AS amount,
        line_item.transaction_id  AS transaction_id,
        line_item.id              AS line_item_id,
        line_item.date            AS line_date,
        line_item.description     AS line_description,
        line_item.credit_debit    AS line_credit_debit,
        line_type.id              AS line_type_id,
        line_type.name            AS line_type_name,
        line_complete.id          AS line_complete_id,
        line_complete.short_name  AS line_complete_short_name,
        account.id                AS account_id,
        account.name              AS account_name,
        account.credit_debit      AS account_credit_debit,
        envelope.id               AS envelope_id,
        envelope.name             AS envelope_name
    FROM
        envelope_item
        INNER JOIN line_item     ON envelope_item.line_item_id = line_item.id
        INNER JOIN line_type     ON line_item.line_type_id     = line_type.id
        INNER JOIN account       ON line_item.account_id       = account.id
        INNER JOIN line_complete ON line_item.line_complete_id = line_complete.id
        INNER JOIN envelope      ON envelope_item.envelope_id  = envelope.id
        ;
    '''

# Namedtuples for the view rows
AccountDetails = namedtuple('AccountDetails', 'id name credit_debit account_type_id closed envelopes account_type_name')
EnvelopeDetails = namedtuple('EnvelopeDetails', 'id name favorite_account_id favorite_account_name closed')
LineItemDetails = namedtuple('LineItemDetails', 'transaction_id id date line_type_id account_id description confirmation_number line_complete_id amount credit_debit '
        'line_type_name complete_short_name account_name account_credit_debit')
EnvelopeItemDetails = namedtuple('EnvelopeItemDetails', 'id description amount transaction_id line_item_id line_date line_description line_credit_debit'
        'line_type_id line_type_name line_complete_id line_complete_short_name account_id account_name account_credit_debit envelope_id envelope_name')

# Other generic Namedtuples
IdName = namedtuple('IdName', 'id name')


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


# Threads can not share database connections.
class DataBase():
    def __init__(self, db_file_path):
        self._con = sqlite3.connect(db_file_path)

    def _get_id_value_from_query(self, query, *args):
        cursor = self._con.cursor()
        cursor.row_factory = lambda _, row: IdName(*row)

        result = cursor.execute(query, args)
        records = result.fetchall()

        return records

    def _get_line_items(self, target_account_id=None, target_transaction_id=None):
        lines = list()

        if target_account_id:
            query = 'SELECT * FROM line_item_details WHERE account_id = ?'
            filter_value = target_account_id

        elif target_transaction_id:
            query = 'SELECT * FROM line_item_details WHERE transaction_id = ?'
            filter_value = target_transaction_id

        cursor = self._con.cursor()
        cursor.row_factory = dict_factory
        lines = cursor.execute(query, (filter_value, )).fetchall()

        return lines

    def _get_value_from_query(self, query, *args):
        cursor = self._con.cursor()

        result = cursor.execute(query, args)
        row = result.fetchone()
        value = row[0]

        return value

    def add_account(self, name, account_type_id=0, closed=False, credit_debit=DEBIT,
            envelopes=False, id_=None):
        values = (id_, name, account_type_id, closed, credit_debit, envelopes)

        cursor = self._con.cursor()
        cursor.execute('INSERT INTO account '
                '(id, name, account_type_id, closed, credit_debit, envelopes) '
                'VALUES (?, ?, ?, ?, ?, ?)', values)

    def add_envelope(self, name, favorite_account_id=0, closed=False, id_=None):
        values = (id_, name, favorite_account_id, closed)

        cursor = self._con.cursor()
        cursor.execute('INSERT INTO envelope '
                '(id, name, favorite_account_id, closed) '
                'VALUES (?, ?, ?, ?)', values)

    def add_envelope_item(self, line_item_id, envelope_id, amount,
            description='', id_=None):

        values = (id_, line_item_id, envelope_id, description, amount)

        cursor = self._con.cursor()
        cursor.execute('INSERT INTO envelope_item '
                '(id, line_item_id, envelope_id, description, amount) '
                'VALUES (?, ?, ?, ?, ?)', values)

    def add_line_item(self, transaction_id, date, account_id, amount, credit_debit,
            line_type_id=0, line_complete_id=0,
            description='', confirmation_number='', id_=None):

        values = (id_, transaction_id, date, line_type_id, account_id,
            description, confirmation_number, line_complete_id, amount,
            credit_debit)

        cursor = self._con.cursor()
        cursor.execute('INSERT INTO line_item '
                '(id, transaction_id, date, line_type_id, account_id, description, confirmation_number, line_complete_id, amount, credit_debit) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)

    def add_ofx_item(self, line_item_id, account_id, fit_id, memo, data):
        values = (None, line_item_id, account_id, fit_id, memo, data)

        cursor = self._con.cursor()
        cursor.execute('INSERT INTO ofx_item '
                '(id, line_item_id, account_id, fit_id, memo, data) '
                'VALUES (?, ?, ?, ?, ?, ?)', values)

    def close(self):
        self._con.close()

    def commit(self):
        self._con.commit()

    def get_account_details(self, account_id):
        cursor = self._con.execute(
                'SELECT * FROM account_details WHERE id = ?',
                (account_id, ))

        cursor.row_factory = dict_factory
        account_row = cursor.fetchone()

        credit_balance = self._get_value_from_query(
                'SELECT sum(amount) as sum '
                'FROM line_item '
                'WHERE credit_debit = 0 AND account_id = ?',
                account_id)

        debit_balance = self._get_value_from_query(
                'SELECT sum(amount) as sum '
                'FROM line_item '
                'WHERE credit_debit = 1 AND account_id = ?',
                account_id)

        if account_row['credit_debit'] == DEBIT:
            account_row['balance'] = debit_balance - credit_balance

        else:
            account_row['balance'] = credit_balance - debit_balance

        return account_row

    def get_account_lines(self, account_id):
        return self._get_line_items(target_account_id=account_id)

    def get_id_of_account(self, name):
        id_ = self._get_value_from_query(
                'SELECT id FROM account WHERE name LIKE ?', name)

        return id_

    def get_id_of_line_complete(self, name):
        id_ = self._get_value_from_query(
                'SELECT id FROM line_complete WHERE name LIKE ?', name)

        return id_

    def get_id_of_line_type(self, name):
        id_ = self._get_value_from_query(
                'SELECT id FROM line_type WHERE name LIKE ?', name)

        return id_

    def get_primary_account_options(self):
        query = 'SELECT id, name FROM account WHERE closed=0 AND account_type_id=2 ORDER BY name'
        accounts = self._get_id_value_from_query(query)

        return accounts

    def get_primary_envelope_options(self):
        query = 'SELECT id, name FROM envelope WHERE closed=0 AND id>0 ORDER BY name'
        envelopes = self._get_id_value_from_query(query)

        return envelopes


    def make_tables(self):
        cursor = self._con.cursor()

        # Tables
        cursor.executescript(CREATE_ACCOUNT_TYPE_TABLE)
        cursor.executescript(CREATE_LINE_TYPE_TABLE)
        cursor.executescript(CREATE_LINE_COMPLETE_TABLE)

        cursor.executescript(CREATE_ACCOUNT_TABLE)
        cursor.executescript(CREATE_ENVELOPE_TABLE)

        cursor.executescript(CREATE_ENVELOPE_ITEM_TABLE)
        cursor.executescript(CREATE_LINE_ITEM_TABLE)
        cursor.executescript(CREATE_OFX_ITEM_TABLE)

        # Views
        cursor.executescript(CREATE_ACCOUNT_DETAILS_VIEW)
        cursor.executescript(CREATE_ENVELOPE_DETAILS_VIEW)
        cursor.executescript(CREATE_LINE_ITEM_DETAILS_VIEW)
        cursor.executescript(CREATE_ENVELOPE_ITEM_DETAILS_VIEW)

        self._con.commit()







    def _g_et_options(self, query):
        options = list()
        for id, name in self._con.execute(query):
            options.append(Options(id, name))

        return options

    def _g_et_transaction_lines(self, transaction_id):
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



    def c_heck_connection(self):
        try:
            self._connection.execute('SELECT 1')
            print('Connection to database successful')

        except Exception as e:
            print('Connection to database failed <{}>'.format(e))

    def g_et_account_options(self):
        query = 'SELECT id, name FROM account ORDER BY closed, account_type_id, name'
        return self._get_options(query)

    def g_et_account_type_options(self):
        query = 'SELECT id, name FROM account_type ORDER BY name'
        return self._get_options(query)

    def g_et_envelope_options(self):
        query = 'SELECT id, name FROM envelope ORDER BY closed, name'
        return self._get_options(query)

    def g_et_line_type_options(self):
        query = 'SELECT id, name FROM line_type ORDER BY name'
        return self._get_options(query)

    def g_et_envelope_details(self, envelope_id):
        envelope_q = 'SELECT * FROM envelope WHERE id = ?'
        for row in self._con.execute(envelope_q, (envelope_id, )):
            id = row[0]
            name = row[1]
            favorite_account_id = row[2]
            closed = bool(row[3])

        account_name = self._account_names[favorite_account_id]

        env_lines = list()
        balance = 0.0

        for row in self._con.execute(ENVELOPE_LINES, (envelope_id, )):
            line_item_id = row[0]
            transaction_id = row[1]
            date = row[2]
            line_type_id = row[3]
            account_id = row[4]
            description = row[5]
            confirmation_number = row[6]
            complete_id = row[7]
            amount = row[8]
            cd = CreditDebit(row[9])
            envelope_line_id = row[10]
            line_item_id = row[11]
            envelope_id = row[12]
            envelope_description = row[13]
            envelope_amount = row[14]

            if cd is CreditDebit.DEBIT:
                balance += envelope_amount

            else:
                balance -= envelope_amount

            line_type_name = self._line_type_names[line_type_id]
            complete_name = self._line_complete_names[complete_id]

            env_lines.append(EnvelopeItemDetails(
                    line_item_id, transaction_id, date, line_type_id, line_type_name,
                    account_id, account_name, description, confirmation_number,
                    complete_id, complete_name, amount, cd, envelope_line_id,
                    envelope_description, envelope_amount, balance))

        return EnvelopeDetails(id, name, favorite_account_id, account_name, closed,
                env_lines, balance)

    def g_et_transaction_lines(self, transaction_id):
        return self._get_line_items(target_transaction_id=transaction_id)
