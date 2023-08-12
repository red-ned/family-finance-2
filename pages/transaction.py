from dash import callback
from dash import dash_table
from dash import html
from dash import register_page
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State


from ff2.data_base import DataBase


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


def _make_transaction_tables(transaction_id):
    with DataBase() as db:
        s_lines, d_lines = db.get_transaction_lines(transaction_id)
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

    source_table = dash_table.DataTable(id='source_table',
            data=s_lines,
            columns=columns,
            dropdown=dropdown,
            editable=True,
            row_deletable=True,
            style_as_list_view=True,
            )

    destination_table = dash_table.DataTable(id='destination_table',
            data=d_lines,
            columns=columns,
            dropdown=dropdown,
            editable=True,
            row_deletable=True,
            style_as_list_view=True,
            )

    return source_table, destination_table


def layout(transaction_id=None):
    content = 'This is our Transaction page content.'
    trasaction_str = 'Transaction ID: {}'.format(transaction_id)
    source_table, destination_table = _make_transaction_tables(transaction_id)

    add_source_button = html.Button('Add Source Row', n_clicks=0,
            id='add_source_button')

    add_destination_button = html.Button('Add Destination Row', n_clicks=0,
            id='add_destination_button')

    children = [
            html.H1(children='The Transaction page'),
            html.Div(content),
            html.Div(trasaction_str),
            source_table,
            add_source_button,
            destination_table,
            add_destination_button,
            ]

    return html.Div(children=children)



@callback(Output('source_table', 'data'),
          Input('add_source_button', 'n_clicks'),
          State('source_table', 'data'),
          State('destination_table', 'data'))
def add_source_row(n_clicks, s_data, d_data):
    if n_clicks == 0:
        return s_data

    new_row = dict()
    first_row = data[0]

    for id, value in first_row.items():
        new_value = None
        if id in ('transaction_id', 'date', 'description', 'amount'):
            new_value = value

        new_row[id] = new_value

    data.append(new_row)

    return data

@callback(
    Output('adding-rows-graph', 'figure'),
    Input('adding-rows-table', 'data'),
    Input('adding-rows-table', 'columns'))
def display_output(rows, columns):
    return {
        'data': [{
            'type': 'heatmap',
            'z': [[row.get(c['id'], None) for c in columns] for row in rows],
            'x': [c['name'] for c in columns]
        }]
    }
