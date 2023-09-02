#!/usr/bin/env python

from datetime import datetime
from sqlite3 import connect
from xml.etree import ElementTree


CREATE_ACCOUNT_TYPE_TABLE = '''
    CREATE TABLE account_type(
        id                  INTEGER PRIMARY KEY,
        name                TEXT
        );

    INSERT INTO account_type VALUES (0, "-Select Account Type-");
    INSERT INTO account_type VALUES (1, "Income");
    INSERT INTO account_type VALUES (2, "Account");
    INSERT INTO account_type VALUES (3, "Expense");
    '''

CREATE_LINE_TYPE_TABLE = '''
    CREATE TABLE line_type(
        id                  INTEGER PRIMARY KEY,
        name                TEXT
        );

    INSERT INTO line_type VALUES (0, " ");
    INSERT INTO line_type VALUES (1, "Deposit");
    INSERT INTO line_type VALUES (2, "Purchase");
    INSERT INTO line_type VALUES (3, "Transfer"); -- Old value 4
    INSERT INTO line_type VALUES (4, "Refund");   -- Old value 8
    INSERT INTO line_type VALUES (5, "Deposit Refund");
    '''

CREATE_LINE_COMPLETE_TABLE = '''
    CREATE TABLE line_complete(
        id                  INTEGER PRIMARY KEY,
        short_name          TEXT,
        name                TEXT
        );

    INSERT INTO line_complete VALUES (0, " ", "NONE");
    INSERT INTO line_complete VALUES (1, "C", "Cleared");
    INSERT INTO line_complete VALUES (2, "R", "Reconciled");
    '''

CREATE_ACCOUNT_TABLE = '''
    CREATE TABLE account(
        id                  INTEGER PRIMARY KEY,
        name                TEXT,
        account_type_id     INTEGER,
        closed              INTEGER,
        credit_debit        INTEGER,
        envelopes           INTEGER
        );

    INSERT INTO account VALUES (0, "-Select Account-", 0, 0, 0, 0);
    '''

CREATE_ENVELOPE_TABLE = '''
    CREATE TABLE envelope(
        id                  INTEGER PRIMARY KEY,
        name                TEXT,
        favorite_account_id INTEGER,
        closed              INTEGER
        );

    INSERT INTO envelope VALUES (0, "-Select Envelope-", 0, 0);
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
        complete_id         INTEGER,
        amount              REAL,
        credit_debit        INTEGER
        );
    '''

CREATE_ENVELOPE_ITEM_TABLE = '''
    CREATE TABLE envelope_item(
        id                  INTEGER PRIMARY KEY,
        line_item_id        INTEGER,
        envelope_id         INTEGER,
        description         TEXT,
        amount              REAL
        );
    '''

CREATE_OFX_ITEM_TABLE = '''
    CREATE TABLE ofx_item(
        id                  INTEGER PRIMARY KEY,
        line_item_id        INTEGER,
        account_id          INTEGER,
        fit_id              TEXT,
        memo                TEXT,
        data                TEXT
        );
    '''

CREATE_OTHER_TABLE = '''
    -- CREATE TABLE ofx_statment(id, data)
    -- CREATE TABLE receipt(id, line_item_id, image);
    -- CREATE TABLE goals(id, envelope_id, priority, description, target_amount, step_amount);
    '''

class DataBaseBuiler():
    def __init__(self, db_file_path):
        self._cx = connect(db_file_path)
        self._cu = self._cx.cursor()

        self._ofx_id = 0

    def _add_account(self, values):
        id = int(values['id'])
        name = values['name']
        # Ignore the origional type id. Use catagory as the new type id.
        #type_id = int(values['typeID'])
        account_type_id = int(values['catagory'])
        closed = self._fix_bool(values['closed'])
        cd = self._fix_bool(values['creditDebit'])
        envelopes = self._fix_bool(values['envelopes'])

        if id <= 0:
            # Skip the old special accounts.
            # Only using the new special 0 NONE account.
            return

        values = (id, name, account_type_id, closed, cd, envelopes)
        self._cu.execute('INSERT INTO account VALUES (?, ?, ?, ?, ?, ?)', values)

    def _add_envelope(self, values):
        id = int(values['id'])
        name = values['name']
        #group_id = int(values['groupID'])
        favorite_account_id = 0
        closed = self._fix_bool(values['closed'])

        if id <= 0:
            # Skip the old special envelopes.
            # Only using the new special 0 NONE envelope.
            return

        values = (id, name, favorite_account_id, closed)

        self._cu.execute('INSERT INTO envelope VALUES (?, ?, ?, ?)', values)

    def _add_envelope_item(self, values):
        id = int(values['id'])
        line_item_id = int(values['lineItemID'])
        envelope_id = int(values['envelopeID'])
        description = values.get('description', '')
        amount = float(values['amount'])

        if description is None:
            description = ''

        row = (id, line_item_id, envelope_id, description, amount)
        self._cu.execute('INSERT INTO envelope_item VALUES (?, ?, ?, ?, ?)', row)

    def _add_line_item(self, values):
        id = int(values['id'])
        transaction_id = int(values['transactionID'])
        date = values['date']
        line_type_id = self._fix_line_type_id(values['typeID'])
        account_id = self._fix_account_id(values['accountID'])
        description = values.get('description', '')
        confirmation_number = values.get('confirmationNumber', '')
        #envelope_id = values['envelopeID']
        complete = self._int_from_complete(values['complete'])
        amount = float(values['amount'])
        cd = self._fix_bool(values['creditDebit'])

        if description is None:
            description = ''

        if confirmation_number is None:
            confirmation_number = ''

        row = (id, transaction_id, date, line_type_id, account_id, description, confirmation_number, complete, amount, cd)

        self._cu.execute('INSERT INTO line_item VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', row)

    def _add_ofx_item(self, values):
        self._ofx_id += 1
        line_item_id = int(values['lineItemID'])
        account_id = int(values['accountID'])
        fit_id = values['fitID']

        data_dict = self._convert_ofx_string_to_dict(values['data'])
        data_str = str(data_dict)

        memo = data_dict.get('NAME', '') + data_dict.get('MEMO', '')

        row = (self._ofx_id, line_item_id, account_id, fit_id, memo, data_str)
        self._cu.execute('INSERT INTO ofx_item VALUES (?, ?, ?, ?, ?, ?)', row)

    def _convert_ofx_string_to_dict(self, ofx_str):
        ofx_str = ofx_str.replace('\n', '')
        ofx_str = ofx_str.replace('<STMTTRN>', '')
        ofx_str = ofx_str.replace('</STMTTRN>', '')

        ofx_values = dict()
        for segment in ofx_str.split('<'):
            if segment == '' or segment.startswith('/'):
                continue

            name, value = segment.split('>')
            ofx_values[name] = value

        return ofx_values

    def _fix_account_id(self, value):
        value = int(value)

        if value == -1:
            return 0

        return value

    def _fix_bool(self, value):
        if value == 'true':
            return 1

        if value == 'false':
            return 0

        raise Exception('Unexpected bool <{}>'.format(value))

    def _fix_complete(self, value):
        if value == ' ':
            return 0

        if value == 'C':
            return 1

        if value == 'R':
            return 2

        raise Exception('Unexpected bool <{}>'.format(value))

    def _fix_line_type_id(self, value):
        value = int(value)

        if value in (-1, 9):
            # Change old type_id -1 (NULL) and 9 (Erase Me) to new 0 (NONE)
            return 0

        if value == 8:
            # Change old type_id 8 (Refund) to new 4
            return 4

        if value == 4:
            # Change old type_id 4 (Transfer) to new 3
            return 3

        return value

    def _get_tag(self, element):
        # Remove the annoying Namespace from every tag.
        tag = element.tag
        if tag.startswith('{http://tempuri.org/ExportDS.xsd}'):
            return tag[33:]

        raise Exception('Unexpected namespace in the tag <{}>'.format(tag))

    def _get_values_from_element(self, element):
        values = dict()

        for leaf in element:
            value = leaf.text
            name = self._get_tag(leaf)
            values[name] = value

        return values

    def _int_from_complete(self, value):
        if value == 'R':
            # Reconsiled
            return 2

        if value == 'C':
            # Complete
            return 1

        if value == ' ':
            # Incomplete
            return 0

        return value

    def _parse_element(self, element):
        table_name = self._get_tag(element)
        values = self._get_values_from_element(element)

        if table_name == 'LineItem':
            self._add_line_item(values)

        elif table_name == 'EnvelopeLine':
            self._add_envelope_item(values)

        elif table_name == 'Account':
            self._add_account(values)

        elif table_name == 'Envelope':
            self._add_envelope(values)

        #elif table_name == 'LineType':
            #self._add_line_type(values)

        #elif table_name == 'EnvelopeGroup':
            #self._add_account_type(values)

        #elif table_name == 'AccountType':
            #self._add_account_type(values)

        elif table_name == 'OFXLineItem':
            self._add_ofx_item(values)

        else:
            print(table_name, values)

    def close(self):
        self._cx.close()

    def make_tables(self):
        self._cx.executescript(CREATE_ACCOUNT_TYPE_TABLE)
        self._cx.executescript(CREATE_LINE_TYPE_TABLE)
        self._cx.executescript(CREATE_LINE_COMPLETE_TABLE)

        self._cx.executescript(CREATE_ACCOUNT_TABLE)
        self._cx.executescript(CREATE_ENVELOPE_TABLE)

        self._cx.executescript(CREATE_ENVELOPE_ITEM_TABLE)
        self._cx.executescript(CREATE_LINE_ITEM_TABLE)
        self._cx.executescript(CREATE_OFX_ITEM_TABLE)

        self._cx.commit()

    def populate_db_with_xml(self, xml_path):
        tree = ElementTree.parse(xml_path)
        root = tree.getroot()

        print('Populating DB with data from data/FFdata.xml')
        for element in root:
            self._parse_element(element)

        self._cx.commit()
