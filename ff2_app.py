#!/usr/bin/env python

from dash import Dash
from dash import dcc
from dash import html
from dash import page_container
from dash import page_registry


app = Dash(__name__, use_pages=True, pages_folder="pages")

def _make_links_segment():
    links = list()
    for page in page_registry.values():
        text = '{} - {}'.format(page['name'], page['path'])
        link = dcc.Link(text, href=page["relative_path"])
        links.append(html.Div(link))

    return links


def layout():
    links_segment = _make_links_segment()
    page_layout = [
            html.H1('Multi-page app with Dash Pages'),
            html.Div(links_segment),
            page_container
            ]

    return html.Div(page_layout)


app.layout = layout()


if __name__ == '__main__':
    app.run_server(debug=True)
