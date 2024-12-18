import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from core import app  
from pages import graphs, map  


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/graphs':
        return graphs.layout
    elif pathname == '/map':
        return map.layout
    else:
        return html.Div([
            html.H1(children="Home Page"),
            dcc.Link('Go to Graphs Page', href='/graphs'),
            html.Br(),
            dcc.Link('Go to Map Page', href='/map'),
        ])

if __name__ == '__main__':
    app.run_server(debug=True)