import sqlite3

import pdb


# Instead of using the None value in sqlite3, we use special records in the
# various tables that all use 0 as the record id.
NONE_ID = 0

#             | Left    | Right
#             | DEBIT-1 | CREDIT-0
# DEBIT Acc.  |   +     |   -
# CREDIT Acc. |   -     |   +
CREDIT = 0
DEBIT = 1

# Table creation statements
CREATE_ACCOUNT_TYPE_TABLE = '''
    CREATE TABLE account_type (
        id   INTEGER PRIMARY KEY,
        name TEXT UNIQUE
        ) STRICT;

    INSERT INTO account_type VALUES (0, " ");
    INSERT INTO account_type VALUES (1, "Income");
    INSERT INTO account_type VALUES (2, "Account");
    INSERT INTO account_type VALUES (3, "Expense");
    '''

CREATE_LINE_TYPE_TABLE = '''
    CREATE TABLE line_type(
        id         INTEGER PRIMARY KEY,
        short_name TEXT UNIQUE,
        name       TEXT UNIQUE
        ) STRICT;

    INSERT INTO line_type VALUES (0, " ", " ");
    INSERT INTO line_type VALUES (1, "D", "Deposit");
    INSERT INTO line_type VALUES (2, "P", "Purchase");
    INSERT INTO line_type VALUES (3, "T", "Transfer");
    INSERT INTO line_type VALUES (4, "R", "Refund");
    INSERT INTO line_type VALUES (5, "U", "Return");
    '''

CREATE_LINE_COMPLETE_TABLE = '''
    CREATE TABLE line_complete(
        id         INTEGER PRIMARY KEY,
        short_name TEXT UNIQUE,
        name       TEXT UNIQUE
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
        line_item.line_complete_id    AS line_complete_id,
        line_item.amount              AS amount,
        line_item.credit_debit        AS credit_debit,
        line_type.short_name          AS line_type_short_name,
        line_type.name                AS line_type_name,
        line_complete.short_name      AS complete_short_name,
        line_complete.name            AS complete_name,
        account.name                  AS account_name,
        account.credit_debit          AS account_credit_debit,
        ofx_item.id                   AS ofx_item_id
    FROM
        line_item
        INNER JOIN line_type     ON line_item.line_type_id     = line_type.id
        INNER JOIN line_complete ON line_item.line_complete_id = line_complete.id
        INNER JOIN account       ON line_item.account_id       = account.id
        LEFT  JOIN ofx_item      ON line_item.id               = ofx_item.line_item_id
        ;
    '''

CREATE_ENVELOPE_ITEM_DETAILS_VIEW = '''
    CREATE VIEW envelope_item_details
    AS
    SELECT
        envelope_item.id           AS id,
        envelope_item.line_item_id AS line_item_id,
        envelope_item.envelope_id  AS envelope_id,
        envelope_item.description  AS description,
        envelope_item.amount       AS amount,
        envelope.name              AS envelope_name,
        line_item.transaction_id   AS transaction_id,
        line_item.date             AS line_date,
        line_item.line_type_id     AS line_type_id,
        line_item.account_id       AS account_id,
        line_item.description      AS line_description,
        line_item.line_complete_id AS line_complete_id,
        line_item.credit_debit     AS line_credit_debit,
        line_type.short_name       AS line_type_short_name,
        line_type.name             AS line_type_name,
        line_complete.short_name   AS line_complete_short_name,
        line_complete.name         AS line_complete_name,
        account.name               AS account_name,
        account.credit_debit       AS account_credit_debit
    FROM
        envelope_item
        INNER JOIN line_item     ON envelope_item.line_item_id = line_item.id
        INNER JOIN envelope      ON envelope_item.envelope_id  = envelope.id
        INNER JOIN line_type     ON line_item.line_type_id     = line_type.id
        INNER JOIN account       ON line_item.account_id       = account.id
        INNER JOIN line_complete ON line_item.line_complete_id = line_complete.id
        ;
    '''

CREATE_ENVELOPE_BALANCE_VIEW = '''
    CREATE VIEW envelope_balance
    AS
    SELECT
        line_item.account_id       AS account_id,
        line_item.credit_debit     AS line_credit_debit,
        envelope_item.envelope_id  AS envelope_id,
        account.credit_debit       as account_credit_debit,
        sum(envelope_item.amount)  AS amount_sum
    FROM
        envelope_item
        INNER JOIN line_item ON line_item.id = envelope_item.line_item_id
        INNER JOIN account   ON account.id   = line_item.account_id
    GROUP BY
        account_id, envelope_id, line_credit_debit;
    '''

CREATE_ACCOUNT_BALANCE_VIEW = '''
    CREATE VIEW account_balance
    AS
    SELECT
        line_item.account_id    AS account_id,
        line_item.credit_debit  AS credit_debit,
        sum(line_item.amount)   AS amount_sum
    FROM
        line_item
    GROUP BY
        account_id, credit_debit;
    '''

DROP_VIEWS = '''
    DROP VIEW IF EXISTS account_details;
    DROP VIEW IF EXISTS envelope_details;
    DROP VIEW IF EXISTS line_item_details;
    DROP VIEW IF EXISTS envelope_item_details;
'''


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


class DataBase():
    def __init__(self, db_file_path):
        # Threads can not share database connections.
        self._con = sqlite3.connect(db_file_path)

    def _add_account_credit_debit_balance_columns(self, account_lines, account_cd):
        balance = 0

        for line in account_lines:
            line_amount = line['amount']
            line_cd = line['credit_debit']
            debit_amount = None
            credit_amount = None

            if line_cd == DEBIT:
                debit_amount = line_amount

            elif line_cd == CREDIT:
                credit_amount = line_amount

            if line_cd == account_cd:
                balance = balance + line_amount

            else:
                balance = balance - line_amount

            line['credit_amount'] = credit_amount
            line['debit_amount'] = debit_amount
            line['balance'] = balance

    def _add_envelope_credit_debit_balance_columns(self, envelope_lines):
        balance = 0

        for line in envelope_lines:
            line_amount = line['amount']
            line_cd = line['line_credit_debit']
            account_cd = line['account_credit_debit']
            debit_amount = None
            credit_amount = None

            if line_cd == DEBIT:
                debit_amount = line_amount

            elif line_cd == CREDIT:
                credit_amount = line_amount

            if line_cd == account_cd:
                balance = balance + line_amount

            else:
                balance = balance - line_amount

            line['credit_amount'] = credit_amount
            line['debit_amount'] = debit_amount
            line['balance'] = balance

    def _calculate_account_balance(self, account_id, account_cd, account_balances=None):
        if account_balances is None:
            account_balances = self._get_records(
                    'SELECT * FROM account_balance WHERE account_id = ? ',
                    account_id)

        credit_balance = 0.0
        debit_balance = 0.0
        for record in account_balances:
            if record['account_id'] == account_id:
                if record['credit_debit'] == CREDIT:
                    credit_balance = record['amount_sum']

                if record['credit_debit'] == DEBIT:
                    debit_balance = record['amount_sum']

        if account_cd == DEBIT:
            balance = debit_balance - credit_balance

        elif account_cd == CREDIT:
            balance = credit_balance - debit_balance

        return balance

    def _calculate_envelope_balance(self, envelope_id, envelope_balances=None):
        if envelope_balances is None:
            envelope_balances = self._get_records(
                    'SELECT * FROM envelope_balance WHERE envelope_id = ? ',
                    envelope_id)

        balance = 0.0
        for record in envelope_balances:
            if record['envelope_id'] == envelope_id:
                if record['line_credit_debit'] == record['account_credit_debit']:
                    balance += record['amount_sum']

                else:
                    balance -= record['amount_sum']

        return balance

    def _get_records(self, query, *args):
        cursor = self._con.cursor()
        cursor.row_factory = dict_factory

        result = cursor.execute(query, args)
        records = result.fetchall()

        return records

    def _get_record(self, query, *args):
        cursor = self._con.cursor()
        cursor.row_factory = dict_factory

        result = cursor.execute(query, args)
        record = result.fetchone()

        return record

    def _get_value(self, query, *args):
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
            description='', id_=None):

        values = (id_, transaction_id, date, line_type_id, account_id,
            description, line_complete_id, amount,
            credit_debit)

        cursor = self._con.cursor()
        cursor.execute('INSERT INTO line_item '
                '(id, transaction_id, date, line_type_id, account_id, description, line_complete_id, amount, credit_debit) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', values)

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
        account_details = self._get_record(
                'SELECT * FROM account_details WHERE id = ?',
                account_id)

        account_lines = self._get_records(
                'SELECT * FROM line_item_details '
                'WHERE account_id = ? '
                'ORDER BY date',
                account_id)

        account_cd = account_details['credit_debit']

        self._add_account_credit_debit_balance_columns(account_lines, account_cd)

        account_details['balance'] = self._calculate_account_balance(account_id, account_cd)
        account_details['lines'] = account_lines

        return account_details

    def get_envelope_details(self, envelope_id):
        envelope_details = self._get_record(
                'SELECT * FROM envelope_details WHERE id = ?',
                envelope_id)

        envelope_lines = self._get_records(
                'SELECT * FROM envelope_item_details '
                'WHERE envelope_id = ? '
                'ORDER BY line_date',
                envelope_id)

        self._add_envelope_credit_debit_balance_columns(envelope_lines)

        envelope_details['balance'] = self._calculate_envelope_balance(envelope_id)
        envelope_details['lines'] = envelope_lines

        return envelope_details

    def get_id_of_account(self, name):
        id_ = self._get_value('SELECT id FROM account WHERE name LIKE ?', name)

        return id_

    def get_id_of_line_complete(self, name):
        id_ = self._get_value(
                'SELECT id FROM line_complete WHERE name LIKE ?', name)

        return id_

    def get_id_of_line_type(self, name):
        id_ = self._get_value(
                'SELECT id FROM line_type WHERE name LIKE ?', name)

        return id_

    def get_account_options(self, add_balance_column=False):
        accounts = self._get_records(
                'SELECT * FROM account_details '
                'WHERE closed = 0 AND account_type_id = 2 '
                'ORDER BY closed, account_type_id, name')

        if add_balance_column:
            account_balances = self._get_records('SELECT * FROM account_balance')

            for account in accounts:
                id_ = account['id']
                cd = account['credit_debit']
                account['balance'] = self._calculate_account_balance(id_, cd,
                        account_balances)

        return accounts

    def get_envelope_options(self, add_balance_column=False):
        envelopes = self._get_records(
                'SELECT * FROM envelope_details '
                'WHERE closed = 0 '
                'ORDER BY name')

        if add_balance_column:
            envelope_balances = self._get_records('SELECT * FROM envelope_balance')
            for envelope in envelopes:
                id_ = envelope['id']
                envelope['balance'] = self._calculate_envelope_balance(id_,
                        envelope_balances)

        return envelopes

    def get_transaction_lines(self, transaction_id):
        transaction_lines = self._get_records(
                'SELECT * FROM line_item_details '
                'WHERE transaction_id = ? '
                'ORDER BY credit_debit, id',
                transaction_id)

        return transaction_lines


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

        ### Make a real method of thracking schema versions and updating them.
        cursor.executescript(CREATE_ACCOUNT_DETAILS_VIEW)
        cursor.executescript(CREATE_ENVELOPE_DETAILS_VIEW)
        cursor.executescript(CREATE_LINE_ITEM_DETAILS_VIEW)
        cursor.executescript(CREATE_ENVELOPE_ITEM_DETAILS_VIEW)
        cursor.executescript(CREATE_ENVELOPE_BALANCE_VIEW)
        cursor.executescript(CREATE_ACCOUNT_BALANCE_VIEW)

        self._con.commit()






    def c_heck_connection(self):
        try:
            self._connection.execute('SELECT 1')
            print('Connection to database successful')

        except Exception as e:
            print('Connection to database failed <{}>'.format(e))
