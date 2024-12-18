import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Load your data
df = pd.read_csv('./data/AL.csv')
df['year'] = pd.to_datetime(df['DateTime']).dt.year

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children="Accident Analysis Dashboard"),

    html.Div(children='''
        Analyzing accident trends and patterns.
    '''),

    dcc.Graph(id='cases-by-year-bar'),

    dcc.Graph(id='wind-speed-by-year'),

])

# Callback to update the 'cases-by-year-bar' graph
@app.callback(
    Output('cases-by-year-bar', 'figure'),
    Input('cases-by-year-bar', 'id'))  # This input isn't used but is required for a callback
def update_cases_by_year_bar(id):
    count = df.groupby('year').size().reset_index(name='count')

    fig = go.Figure()
    fig.add_trace(go.Bar(x=count['year'], y=count['count'], name='Number of cases by year'))
    fig.update_layout(title='Number of cases by year', xaxis_title='Year', yaxis_title='Number of cases')

    # Add rolling mean
    count['rolling_mean'] = count['count'].rolling(window=10).mean()
    fig.add_trace(go.Scatter(x=count['year'], y=count['rolling_mean'], mode='lines', name='Rolling mean of cases (10 years window)'))
    fig.update_layout(legend=dict(x=0.35, y=-0.75, orientation='h'))

    # Time series range slider
    fig.update_xaxes(rangeslider_visible=True)
    return fig

# Callback to update the 'wind-speed-by-year' graph
@app.callback(
    Output('wind-speed-by-year', 'figure'),
    Input('wind-speed-by-year', 'id'))  # This input isn't used but is required for a callback
def update_wind_speed_by_year(id):
    fig = go.Figure()
    # Maximum wind speed by year
    df_grouped_by_year_wind = df.groupby('year')['Wind'].max().reset_index(name='max_wind')
    fig.add_trace(go.Scatter(x=df_grouped_by_year_wind['year'], y=df_grouped_by_year_wind['max_wind'], mode='lines', name='Max wind speed by year', line=dict(color='blue')))

    # Minimum wind speed by year
    df_grouped_by_year_wind_min = df.groupby('year')['Wind'].min().reset_index(name='min_wind')
    fig.add_trace(go.Scatter(x=df_grouped_by_year_wind_min['year'], y=df_grouped_by_year_wind_min['min_wind'], mode='lines', name='Min wind speed by year', line=dict(color='green')))

    # Rolling mean max
    df_grouped_by_year_wind['rolling_mean'] = df_grouped_by_year_wind['max_wind'].rolling(window=10).mean()
    fig.add_trace(go.Scatter(x=df_grouped_by_year_wind['year'], y=df_grouped_by_year_wind['rolling_mean'], mode='lines', name='Rolling mean of max wind speed (10 years window)', line=dict(color='red')))

    # Rolling mean min
    df_grouped_by_year_wind_min['rolling_mean_min'] = df_grouped_by_year_wind_min['min_wind'].rolling(window=10).mean()
    fig.add_trace(go.Scatter(x=df_grouped_by_year_wind_min['year'], y=df_grouped_by_year_wind_min['rolling_mean_min'], mode='lines', name='Rolling mean of min wind speed (10 years window)', line=dict(color='orange')))

    fig.update_layout(legend=dict(x=0.4, y=-0.75, orientation='h'))
    fig.update_layout(title='Wind speed by year')
    fig.update_xaxes(title_text='Year')
    fig.update_yaxes(title_text='Wind speed (mph)')

    fig.update_xaxes(rangeslider_visible=True)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)