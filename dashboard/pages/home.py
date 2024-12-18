from dash import html
import dash

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('Home'),    
    html.Div(className='Info', children=[
        html.P('Welcome to Hurrican Tracker.'),
        html.Label('Navigation: ', className='label'),
        html.Div(className='navigation', children=[
            html.A('Graphs', href='/graphs', className='nav-link'),
            html.A('Maps', href='/maps', className='nav-link'),
        ]),
    ]),
    html.Footer(className='home-footer', children=[
        html.Div(className='separator'),
        html.Div(className='container', children=[
            html.P('© 2024 - HES-SO Master. All rights reserved.', className='text-center'),
            html.Div(className='text-center', children=[                
                html.Img(src='/assets/images/HES_SO_Logo.png', className='hesso-logo-footer'),
            ]),
            html.P('MA-VI Project - Telley Cyril / Saucy Quentin / Altin Hajda', className='text-center'),
        ]),
    ]),
])