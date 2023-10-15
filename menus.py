#!/usr/bin/env python3

from os import listdir
from os import path

from ff2.data_base.data_base import DataBase
from ff2.data_base.xml_importer import XmlImporter
from ff2.function_menu import FunctionMenu

import pdb


DEFAULT_XML_DATA = 'data/FFdata.xml'



ACCOUNT_LINES_TEMPLATE = '{:10} {:1} {:30} {:>10} {:1} {:>10} {:>10} {:^3}'
ENVELOPE_LINES_TEMPLATE = '{:10} {:1} {:25} {:30} {:30} {:>10} {:1} {:>10} {:>10}'


class Menus():
    def __init__(self, data_dir_path):
        self._data_dir_path = data_dir_path
        self._db_path = ''
        self._db = None

    def _get_db_file_names(self):
        file_paths = list()

        for file_name in listdir(self._data_dir_path):
            if not file_name.endswith(".db"):
                continue

            file_path = path.join(data_dir_path, file_name)
            file_path = path.abspath(file_path)
            file_paths.append(file_path)

        return file_paths

    def _format_account_line(self, line):
        date = line['date'][0:10]
        line_type = line['line_type_short_name']
        description = line['description'][:30]
        d_amount = line['debit_amount']
        d_amount_str = '{:.2f}'.format(d_amount) if d_amount else ''
        complete = line['complete_short_name']
        c_amount = line['credit_amount']
        c_amount_str = '{:.2f}'.format(c_amount) if c_amount else ''
        balance_str = '{:.2f}'.format(line['balance'])
        ofx_item_id = line['ofx_item_id']
        ofx_id_str = '*' if ofx_item_id else ''

        line_str = ACCOUNT_LINES_TEMPLATE.format(date, line_type, description,
                d_amount_str, complete, c_amount_str, balance_str, ofx_id_str)

        return line_str

    def _format_account_title(self, account):
        lines = list()
        lines.append('{} - {} ({})'.format(self._title, account['name'], account['id']))
        lines.append('')
        lines.append('    Balance: ${balance:.2f}  Type: {account_type_name}  Closed: {closed}  Envelopes: {envelopes}'.format_map(account))
        lines.append('')
        lines.append('  ' + ACCOUNT_LINES_TEMPLATE.format('Date', '',
                'Description', 'Debit', '', 'Credit', 'Balance', 'OFX'))

        lines = '\n'.join(lines)

        return lines

    def _format_envelope_line(self, line):
        date = line['line_date'][0:10]
        line_type = line['line_type_short_name']
        account_name = line['account_name'][:25]
        line_description = line['line_description'][:30]
        description = line['description'][:30]
        d_amount = line['debit_amount']
        d_amount_str = '{:.2f}'.format(d_amount) if d_amount else ''
        complete = line['line_complete_short_name']
        c_amount = line['credit_amount']
        c_amount_str = '{:.2f}'.format(c_amount) if c_amount else ''
        balance_str = '{:.2f}'.format(line['balance'])

        line_str = ENVELOPE_LINES_TEMPLATE.format(date, line_type, account_name,
                line_description, description,
                d_amount_str, complete, c_amount_str, balance_str)

        return line_str

    def _format_envelope_title(self, envelope):
        lines = list()
        lines.append('{} - {} ({})'.format(self._title, envelope['name'], envelope['id']))
        lines.append('')
        lines.append('    Balance: ${balance:.2f}  Favorite Account: {favorite_account_name}  Closed: {closed}'.format_map(envelope))
        lines.append('')
        lines.append('  ' + ENVELOPE_LINES_TEMPLATE.format('Date', '', 'Account',
                'Line Description', 'Description', 'Debit', '', 'Credit', 'Balance'))

        lines = '\n'.join(lines)

        return lines

    def _format_transaction_line(self, line):
        print(line)
        line = '{:10} {:1} {:30} {:45} {} {} {: >10.2f}  {}'.format(
                line['date'][:10],
                line['line_type_short_name'],
                line['account_name'][:30],
                line['description'][:30],
                line['credit_debit'],
                line['complete_short_name'],
                line['amount'],
                line['ofx_item_id'])

        return line

    def create_in_memory_db(self):
        print('Building the DB in memory ...')
        db = DataBase(':memory:')
        db.make_tables()

        xml_importer = XmlImporter(db)
        xml_importer.import_from_xml(DEFAULT_XML_DATA)

        db.close()

    def create_new_db(self, import_xml_path=''):
        file_name = input('New DB file name: ')
        file_name += '.db'

        file_path = path.join(self._data_dir_path, file_name)
        file_path = path.abspath(file_path)

        if path.isfile(file_path):
            print('File already exists.')
            return

        print('Building the DB file {}...'.format(file_path))
        db = DataBase(file_path)
        db.make_tables()

        if import_xml_path:
            xml_importer = XmlImporter(db)
            xml_importer.import_from_xml(import_xml_path)

        db.close()

    def edit_tables_menu(self):

        fm = FunctionMenu('Family Finance 2 - "{}" Main : Edit Tables'.format(self._db_path))

        while fm.exit_not_selected:
            fm.clear_entries()

            fm.add_function('Edit Accout Type', None)
            fm.add_function('Edit Line Type', None)
            fm.add_function('Edit Line Complete', None)
            fm.add_function('Edit Account', None)
            fm.add_function('Edit Envelope', None)
            fm.add_exit()

            fm.show()

    def select_account(self, account_id):
        fm = FunctionMenu()

        while fm.exit_not_selected:
            fm.clear_entries()

            account = self._db.get_account_details(account_id)
            fm.set_title(self._format_account_title(account))

            for line in account['lines']:
                fm.add_function(self._format_account_line(line),
                        self.select_transaction, line['transaction_id'], line['id'])

            fm.add_blank()
            fm.add_function('Edit Tables', self.edit_tables_menu)
            fm.add_exit()

            fm.show()

    def select_envelope(self, envelope_id):
        fm = FunctionMenu()

        while fm.exit_not_selected:
            fm.clear_entries()

            envelope = self._db.get_envelope_details(envelope_id)
            fm.set_title(self._format_envelope_title(envelope))

            for line in envelope['lines']:
                fm.add_function(self._format_envelope_line(line),
                        self.select_transaction, line['transaction_id'], line['line_item_id'])

            fm.add_blank()
            fm.add_function('Edit Tables', self.edit_tables_menu)
            fm.add_exit()

            fm.show()

    def select_line_item(self, line_item_id):
        fm = FunctionMenu('Line Item\n')

        while fm.exit_not_selected:
            fm.clear_entries()

            fm.add_blank()
            fm.add_function('Edit Tables', self.edit_tables_menu)
            fm.add_exit()

            fm.show()

    def select_transaction(self, transaction_id, target_line_id):
        fm = FunctionMenu('{} - Transaction ({})\n'.format(self._title, transaction_id))

        while fm.exit_not_selected:
            fm.clear_entries()
            starting_index = None

            for index, line in enumerate(self._db.get_transaction_lines(transaction_id)):
                line_id = line['id']
                fm.add_function(self._format_transaction_line(line),
                        self.select_line_item, line_id)

                if target_line_id == line_id:
                    starting_index = index

            fm.add_blank()
            fm.add_function('Edit Tables', self.edit_tables_menu)
            fm.add_exit()

            fm.show(starting_index)

    def main_menu(self, selected_db_path):
        self._db = DataBase(selected_db_path)
        _, db_file = path.split(selected_db_path)
        self._title = 'Family Finance 2 "{}"'.format(db_file)

        fm = FunctionMenu(self._title + ' - Main\n')

        while fm.exit_not_selected:
            fm.clear_entries()

            fm.add_function('Accounts', None)
            for account in self._db.get_account_options(add_balance_column=True):
                fm.add_function('  {name:30} {balance: >15.2f}'.format_map(account),
                        self.select_account, account['id'])

            fm.add_blank()
            fm.add_function('Envelopes', None)
            for envelope in self._db.get_envelope_options(add_balance_column=True):
                fm.add_function('  {name:30} {balance: >15.2f}'.format_map(envelope),
                        self.select_envelope, envelope['id'])

            fm.add_blank()
            fm.add_function('Edit Tables', self.edit_tables_menu)
            fm.add_function('List All Accounts', None)
            fm.add_function('List All Envelopes', None)
            fm.add_exit()

            fm.show()

    def select_db(self):
        fm = FunctionMenu('Family Finance 2 - Select Database\n')

        while fm.exit_not_selected:
            fm.clear_entries()

            for file_path in self._get_db_file_names():
                fm.add_function(file_path, self.main_menu, file_path)

            fm.add_blank()
            fm.add_function('Create an in memory DataBase and populate with data from FFdata.xml',
                            self.create_in_memory_db)
            fm.add_function('Create a new DataBase (blank)',
                            self.create_new_db)
            fm.add_function('Create a new DataBase and populate with data from FFdata.xml',
                            self.create_new_db, DEFAULT_XML_DATA)
            fm.add_exit()
            fm.show()


if __name__ == "__main__":
    data_dir_path = './data'
    menus = Menus(data_dir_path)
    menus.select_db()
