from dash import html, dcc
from dash import Dash
import dash

external_stylesheets = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
    'https://fonts.googleapis.com/css2?family=Rubik:ital,wght@0,300..900;1,300..900&display=swap'
    ]

app = Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

navbar = html.Nav(
    className='navbar navbar-expand-lg navbar-light bg-light',
    children=[        
        html.A(
            className='navbar-brand',
            children=[html.Img(src='/assets/images/logo.png', className='logo')],
            href='/'
        ),        
        html.Div(
            className='collapse navbar-collapse',
            children=[
                html.Ul(
                    className='navbar-nav mr-auto',
                    children=[
                        html.Li(className='nav-item', children=[
                            html.A('Graphs', className='nav-link', href='/graphs')
                        ]),
                        html.Li(className='nav-item', children=[
                            html.A('Maps', className='nav-link', href='/maps')
                        ]),                    
                    ],
                ),
            ],
        ),
    ],
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(className='separator'),    
    dash.page_container,
])

if __name__ == '__main__':
    app.run_server(debug=True)