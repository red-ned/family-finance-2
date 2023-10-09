#!/usr/bin/env python3

from os import listdir
from os import path

#from ff2.db_builder import DataBaseBuiler
from ff2.data_base.data_base import DataBase
from ff2.data_base.xml_importer import XmlImporter
from ff2.function_menu import FunctionMenu


DEFAULT_XML_DATA = 'data/FFdata.xml'


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
        account = self._db.get_account_details(account_id)

        fm = FunctionMenu()

        while fm.exit_not_selected:
            fm.clear_entries()
            fm.set_title('{}\n'
                         '    {} ({})\n'
                         '    Type: {}    Balance: ${:.2f}    Closed: {}    Envelopes: {}\n'
                         .format(self._title, account['name'], account['id'],
                                 account['account_type_name'], account['balance'],
                                 account['closed'], account['envelopes']))

            for line in self._db.get_account_lines(account_id):
                fm.add_function('{} {:30} {:15} {} {} {}'.format(
                        line.date[0:10], line.description[:30], line.confirmation_number[:15], line.cd, line.complete_name, line.amount),
                        self.select_transaction, line.transaction_id)

            fm.add_blank()
            fm.add_function('Edit Tables', self.edit_tables_menu)
            fm.add_exit()

            fm.show()

    def select_envelope(self, envelope_id):
        pass

    def select_line_item(self, line_item_id):
        fm = FunctionMenu('Line Item\n')

        while fm.exit_not_selected:
            fm.clear_entries()

            fm.add_blank()
            fm.add_function('Edit Tables', self.edit_tables_menu)
            fm.add_exit()

            fm.show()

    def select_transaction(self, transaction_id):
        fm = FunctionMenu('Transaction\n')

        while fm.exit_not_selected:
            fm.clear_entries()

            for line in self._db.get_transaction_lines(transaction_id):
                fm.add_function('{} {} {} {} {} {} {}'
                                .format(line.date[0:10], line.id, line.transaction_id, line.account_name,
                                line.description, line.confirmation_number, line.amount),
                                self.select_line_item, line.id)

            fm.add_blank()
            fm.add_function('Edit Tables', self.edit_tables_menu)
            fm.add_exit()

            fm.show()

    def main_menu(self, selected_db_path):
        self._db = DataBase(selected_db_path)
        _, db_file = path.split(selected_db_path)
        self._title = 'Family Finance 2 - "{}"'.format(db_file)

        fm = FunctionMenu(self._title + ' Main\n')

        while fm.exit_not_selected:
            fm.clear_entries()

            fm.add_function('Accounts', None)
            for account in self._db.get_primary_account_options():
                fm.add_function('  ' + account.name, self.select_account, account.id)

            fm.add_blank()
            fm.add_function('Envelopes', None)
            for envelope in self._db.get_primary_envelope_options():
                fm.add_function('  ' + envelope.name, self.select_envelope, envelope.id)

            fm.add_blank()
            fm.add_function('Edit Tables', self.edit_tables_menu)
            fm.add_function('List All Accounts', None)
            fm.add_function('List All Envelopes', None)
            fm.add_exit()

            fm.show()

    def select_db(self):
        tlm = FunctionMenu('Family Finance 2 - Select Database\n')

        while tlm.exit_not_selected:
            tlm.clear_entries()

            for file_path in self._get_db_file_names():
                tlm.add_function(file_path,
                        self.main_menu, file_path)

            tlm.add_blank()
            tlm.add_function('Create an in memory DataBase and populate with data from FFdata.xml',
                            self.create_in_memory_db)
            tlm.add_function('Create a new DataBase (blank)',
                            self.create_new_db)
            tlm.add_function('Create a new DataBase and populate with data from FFdata.xml',
                            self.create_new_db, DEFAULT_XML_DATA)
            tlm.add_exit()
            tlm.show()


if __name__ == "__main__":
    data_dir_path = './data'
    menus = Menus(data_dir_path)
    menus.select_db()
