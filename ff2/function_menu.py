from simple_term_menu import TerminalMenu


class FunctionMenu():
    def __init__(self, title=''):
        self._title = title
        self.clear_entries()

    def _select_exit(self):
        self._exit_not_selected = False


    @property
    def exit_not_selected(self):
        return self._exit_not_selected


    def add_function(self, text, function, *args):
        self._texts.append(text)
        self._function_and_args.append((function, args))

    def add_blank(self):
        self.add_function('', None)

    def add_exit(self):
        self.add_function('EXIT', self._select_exit)

    def clear_entries(self):
        self._texts = list()
        self._function_and_args = list()
        self._exit_not_selected = True

    def set_title(self, title):
        self._title = title

    def show(self):
        menu = TerminalMenu(
                title=self._title,
                menu_entries=self._texts,
                clear_screen=True,
                skip_empty_entries=True,
                )

        selection_index = menu.show()
        if selection_index is None:
            self._select_exit()
            return

        func, args = self._function_and_args[selection_index]
        if func:
            func(*args)

