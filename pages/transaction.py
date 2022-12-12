from dash import html
from dash import register_page



register_page(__name__,
        title='Family Finance 2',
        name='Family Finance 2 - Transactions',
        path_template="/transaction/<transaction_id>")


def layout(transaction_id=None):
    content = 'This is our Transaction page content.'
    trasaction_str = 'Transaction ID: {}'.format(transaction_id)

    children = [html.H1(children='The Transaction page'),
            html.Div(content),
            html.Div(trasaction_str),
            ]

    return html.Div(children)
