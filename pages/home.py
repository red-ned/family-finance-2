from dash import html
from dash import register_page


register_page(__name__, path='/',
        title='Family Finance 2',
        name='Family Finance 2')


def layout():
    children = [
            html.H1('This is our Home page'),
            html.Div('This is our Home page content.'),
            ]

    return html.Div(children)
