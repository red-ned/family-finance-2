from dash import html
from dash import register_page
from dash import dash_table
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State


from data.data_base import DataBase


CLEARABLE = 'clearable'
ID = 'id'
NAME = 'name'
PRESENTATION = 'presentation'
OPTIONS = 'options'
EDITABLE = 'editable'
TYPE = 'type'
DATETIME = 'datetime'
NUMERIC= 'numeric'
TEXT = 'text'
DROPDOWN = 'dropdown'


register_page(__name__,
        title='Family Finance 2',
        name='Family Finance 2 - Transactions',
        path_template="/transaction/<transaction_id>")


def _make_transaction_table(transaction_id):

    with DataBase() as db:
        lines = db.get_transaction_lines(transaction_id)
        line_type_options = db.get_line_type_options()
        account_options = db.get_account_options()

    columns = [
            {ID: 'id',                  NAME: 'Line Item ID',           TYPE:NUMERIC, EDITABLE:False},
            {ID: 'transaction_id',      NAME: 'Transaction',            TYPE:NUMERIC, EDITABLE:False},
            {ID: 'date',                NAME: 'Date',                   TYPE:DATETIME, },
            {ID: 'type_id',             NAME: 'Type',                   PRESENTATION: DROPDOWN},
            {ID: 'account_id',          NAME: 'Account',                PRESENTATION: DROPDOWN},
            {ID: 'description',         NAME: 'Description',            TYPE:TEXT, },
            {ID: 'confirmation_number', NAME: 'Confirmation Number',    TYPE:TEXT, },
            #{ID: 'complete',            NAME: 'C',                      TYPE:TEXT, EDITABLE:False},
            {ID: 'amount',              NAME: 'Amount',                 TYPE:NUMERIC, },
            #{ID: 'cd',                  NAME: 'CD',                     TYPE:NUMERIC, EDITABLE:False},
            ]

    dropdown = {
            'type_id':    {OPTIONS: line_type_options, CLEARABLE:False},
            'account_id': {OPTIONS: account_options,   CLEARABLE:False}
            }

    transaction_table = dash_table.DataTable(id='transaction_table',
            data=lines,
            columns=columns,
            dropdown=dropdown,
            editable=True,
            row_deletable=True,
            style_as_list_view=True,
            )

    return transaction_table


def layout(transaction_id=None):
    content = 'This is our Transaction page content.'
    trasaction_str = 'Transaction ID: {}'.format(transaction_id)
    transaction_table = _make_transaction_table(transaction_id)

    children = [
            html.H1(children='The Transaction page'),
            html.Div(content),
            html.Div(trasaction_str),
            transaction_table,
            html.Button('Add Line Item Row', id='editing-rows-button', n_clicks=0),
            ]

    return html.Div(children=children)



@app.callback(
    Output('adding-rows-table', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('adding-rows-table', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})

    return rows
