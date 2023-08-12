#!/usr/bin/env python3

from os import listdir
from os import path

from simple_term_menu import TerminalMenu

from ff2.db_builder import DataBaseBuiler
from ff2.data_base import DataBase


def new_db_menu(data_dir_path, xml=False):
    file_name = input('New DB file name: ')
    file_name += '.db'

    file_path = path.abspath(path.join(data_dir_path, file_name))

    if path.isfile(file_path):
        print('File already exists.')
        return

    print('Building the DB file {}...'.format(file_path))
    db_builder = DataBaseBuiler(file_path)
    db_builder.make_tables()

    if xml is True:
        db_builder.populate_db_with_xml('data/FFdata.xml')

    db_builder.close()

def program_menu(data_base):
    entries = data_base.get_account_options()

    entries.append('')
    entries.append('Show Deleted Accounts')
    entries.append('Back')
    back_index = len(entries) - 1

    menu = TerminalMenu(
            title='Family Finance 2 - Main:Open Menu\n',
            menu_entries=entries,
            clear_screen=True,
            skip_empty_entries=True,
            status_bar='Select the DB file'
            )

    selection = menu.show()
    if selection in (back_index, None):
        return None

    return entries[selection]

def opening_menu(data_dir_path):
    exit_menu = False
    while exit_menu is False:

        entries = []
        for file_name in listdir(data_dir_path):
            if not file_name.endswith(".db"):
                continue

            file_path = path.abspath(path.join(data_dir_path, file_name))
            entries.append(file_path)

        entries.append('')
        entries.append('Create a new DataBase (blank)')
        entries.append('Create a new DataBase and populate with data from FFdata.xml')
        entries.append('Exit')

        exit_selection = len(entries) - 1
        new_db_mxl_selection = exit_selection - 1
        new_db_selection = exit_selection - 2

        menu = TerminalMenu(
                title='Family Finance 2 - Main\n',
                menu_entries=entries,
                clear_screen=True,
                skip_empty_entries=True,
                )

        selection = menu.show()

        if selection in (exit_selection, None):
            exit_menu = True

        elif selection == new_db_selection:
            new_db_menu(data_dir_path)

        elif selection == new_db_mxl_selection:
            new_db_menu(data_dir_path, xml=True)

        else:
            db_file_path = entries[selection]
            data_base = DataBase(db_file_path)
            program_menu(data_base)
            exit_menu = True


if __name__ == "__main__":
    data_dir_path = './data'
    opening_menu(data_dir_path)
