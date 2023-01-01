#!/usr/bin/env python

from  xml.etree import ElementTree

import pdb
import sqlite3
from datetime import datetime


SQL_CREATE_TABLES = '''
CREATE TABLE account_type(
    id                  INTEGER PRIMARY KEY,
    name                TEXT
    );
-- Add the accout type (old catagory) values.
INSERT INTO account_type VALUES (0, "NONE");
INSERT INTO account_type VALUES (1, "Income");
INSERT INTO account_type VALUES (2, "Account");
INSERT INTO account_type VALUES (3, "Expense");

CREATE TABLE line_type(
    id                  INTEGER PRIMARY KEY,
    name                TEXT
    );
INSERT INTO line_type VALUES (0, "NONE");
INSERT INTO line_type VALUES (1, "Deposit");
INSERT INTO line_type VALUES (2, "Purchase");
INSERT INTO line_type VALUES (4, "Transfer");
INSERT INTO line_type VALUES (8, "Refund");

CREATE TABLE account(
    id                  INTEGER PRIMARY KEY,
    name                TEXT,
    account_type_id     INTEGER,
    closed              INTEGER,
    cd                  INTEGER,
    envelopes           INTEGER,
    FOREIGN KEY(account_type_id) REFERENCES account_type(id)
    );

CREATE TABLE envelope(
    id                  INTEGER PRIMARY KEY,
    name                TEXT,
    favorite_account_id INTEGER,
    closed              INTEGER,
    FOREIGN KEY(favorite_account_id) REFERENCES account(id)
    );

CREATE TABLE line_item(
    id                  INTEGER PRIMARY KEY,
    transaction_id      INTEGER,
    date                ,
    line_type_id        INTEGER,
    account_id          INTEGER,
    description         TEXT,
    confirmation_number TEXT,
    complete            INTEGER,
    amount              REAL,
    cd                  INTEGER,
    FOREIGN KEY(line_type_id) REFERENCES line_type(id),
    FOREIGN KEY(account_id) REFERENCES account(id)
    );

CREATE TABLE envelope_item(
    id                  INTEGER PRIMARY KEY,
    line_item_id        INTEGER,
    envelope_id         INTEGER,
    description         TEXT,
    amount              REAL,
    FOREIGN KEY(line_item_id) REFERENCES line_item(id),
    FOREIGN KEY(envelope_id) REFERENCES envelope(id)
    );

CREATE TABLE ofx_item(
    id                  INTEGER PRIMARY KEY,
    line_item_id        INTEGER,
    account_id          INTEGER,
    fit_id              TEXT,
    name                TEXT,
    data                TEXT,
    FOREIGN KEY(line_item_id) REFERENCES line_item(id),
    FOREIGN KEY(account_id) REFERENCES account(id)
    );

-- CREATE TABLE ofx_statment(id, data)
-- CREATE TABLE receipt(id, line_item_id, image);
-- CREATE TABLE goals(id, envelope_id, priority, description, target_amount, step_amount);
'''

class DataBase():
    def __init__(self, db_file_path):
        self._cx = sqlite3.connect(db_file_path)
        self._cu = self._cx.cursor()

        self._ofx_id = 0


    def _add_account(self, values):
        id = int(values['id'])
        name = values['name']
        # Ignore the origional type id. Use catagory as the new type id.
        #type_id = int(values['typeID'])
        type_id = int(values['catagory'])
        closed = bool(values['closed'])
        cd = bool(values['creditDebit'])
        envelopes = bool(values['envelopes'])

        values = (id, name, type_id, closed, cd, envelopes)
        self._cu.execute('INSERT INTO account VALUES (?, ?, ?, ?, ?, ?)', values)

    def _add_account_type(self, values):
        id = int(values['id'])
        name = values['name']

        values = (id, name)
        self._cu.execute('INSERT INTO account_type VALUES (?, ?)', values)

    def _add_envelope(self, values):
        id = int(values['id'])
        name = values['name']
        group_id = int(values['groupID'])
        favorite_account_id = 0
        closed = bool(values['closed'])

        values = (id, name, favorite_account_id, closed)
        self._cu.execute('INSERT INTO envelope VALUES (?, ?, ?, ?)', values)

    def _add_envelope_item(self, values):
        id = int(values['id'])
        line_item_id = int(values['lineItemID'])
        envelope_id = int(values['envelopeID'])
        description = values['description']
        amount = float(values['amount'])

        values = (id, line_item_id, envelope_id, description, amount)
        self._cu.execute('INSERT INTO envelope_item VALUES (?, ?, ?, ?, ?)', values)

    def _add_line_type(self, values):
        id = int(values['id'])
        name = values['name']

        values = (id, name)
        self._cu.execute('INSERT INTO line_type VALUES (?, ?)', values)

    def _add_line_item(self, values):
        id = int(values['id'])
        transaction_id = int(values['transactionID'])
        date = values['date']
        type_id = int(values['typeID'])
        account_id = int(values['accountID'])
        description = values['description']

        if type_id == 9:
            # Skip lines with Value 9 - "Erase me".
            return

        try:
            confirmation_number = values['confirmationNumber']
        except Exception as e:
            confirmation_number = None

        envelope_id = int(values['envelopeID'])
        complete = values['complete']
        amount = float(values['amount'])
        cd = bool(values['creditDebit'])

        values = (id, transaction_id, date, type_id, account_id, description, confirmation_number, complete, amount, cd)
        self._cu.execute('INSERT INTO line_item VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)

    def _add_ofx_item(self, values):
        self._ofx_id += 1
        line_item_id = int(values['lineItemID'])
        account_id = int(values['accountID'])
        fit_id = values['fitID']

        data = values['data']
        data_dict = self._convert_ofx_string_to_dict_str(data)
        data_str = str(data_dict)
        name = data_dict['NAME']

        values = (self._ofx_id, line_item_id, account_id, fit_id, name, data_str)
        self._cu.execute('INSERT INTO ofx_item VALUES (?, ?, ?, ?, ?, ?)', values)

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

    def _get_tag(self, element):
        # Remove the annoying Namespace from every tag.
        tag = element.tag
        if tag.startswith('{http://tempuri.org/ExportDS.xsd}'):
            return tag[33:]

        raise Exception('Unexpected namespace in the tag <{}>'.format(tag))

    def _parse_element(self, element):
        table_name = self._get_tag(element)
        values = {}

        for leaf in element:
            value = leaf.text
            name = self._get_tag(leaf)
            values[name] = value

        if table_name == 'OFXLineItem':
            self._add_ofx_item(values)

        elif table_name == 'LineType':
            self._add_line_type(values)

        elif table_name == 'LineItem':
            self._add_line_item(values)

        elif table_name == 'EnvelopeLine':
            self._add_envelope_item(values)

        elif table_name == 'Account':
            self._add_account(values)

        elif table_name == 'Envelope':
            self._add_envelope(values)

        #elif table_name == 'EnvelopeGroup':
            #self._add_account_type(values)

        #elif table_name == 'AccountType':
            #self._add_account_type(values)


    def close(self):
        self._cx.close()

    def make_tables(self):
        self._cx.executescript(SQL_CREATE_TABLES)
        self._cx.commit()

    def populate_db_with_xml(self, xml_path):
        tree = ElementTree.parse(xml_path)
        root = tree.getroot()

        for element in root:
            self._parse_element(element)

        self._cx.commit()


if __name__ == '__main__':
    db = DataBase('data/test.db')

    db.make_tables()
    db.populate_db_with_xml('data/FFdata.xml')

    db.close()
