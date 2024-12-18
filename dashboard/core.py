import dash
from dash import dcc
from dash import html

app = dash.Dash(__name__, suppress_callback_exceptions=True)  # Keep the app instance creation here