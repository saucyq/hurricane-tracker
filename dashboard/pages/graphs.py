from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from core import app

# Load your data
df = pd.read_csv('/Users/cyriltelley/Desktop/MSE/MA-VI/Projet_VI/hurricane-tracker/data/AL.csv')
df['year'] = pd.to_datetime(df['DateTime']).dt.year

# Layout of the app
layout = html.Div(children=[
    html.H1(children="Accident Analysis Dashboard"),

    html.Div(children='''
        Analyzing accident trends and patterns.
    '''),

    # First row of graphs
    html.Div(children=[
        dcc.Graph(id='cases-by-year-bar'),
        dcc.Graph(id='wind-speed-by-year'),
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    # Second row of graphs
    html.Div(children=[
        dcc.Graph(id='lat-lon-scatter'),
        dcc.Graph(id='cases-per-storm-hist'),
    ], style={'display': 'flex', 'flex-direction': 'row'})

])

# Callback to update the 'cases-by-year-bar' graph
@app.callback(
    Output('cases-by-year-bar', 'figure'),
    Input('cases-by-year-bar', 'id'))
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
    Input('wind-speed-by-year', 'id'))
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


# Callback to update the 'lat-lon-scatter' graph
@app.callback(
    Output('lat-lon-scatter', 'figure'),
    Input('lat-lon-scatter', 'id'))
def update_lat_lon_scatter(id):
    fig = px.scatter(df, x="Longitude", y="Latitude", color="Wind", title='Hurricane path by wind speed')
    fig.update_layout(legend=dict(x=0.75, y=-0.2, orientation='h'))
    return fig

# Callback to update the 'cases-per-storm-hist' graph
@app.callback(
    Output('cases-per-storm-hist', 'figure'),
    Input('cases-per-storm-hist', 'id'))
def update_cases_per_storm_hist(id):
    storm_counts = df.groupby('Storm')['DateTime'].count().reset_index(name='count')
    fig = px.histogram(storm_counts, x="count", title='Number of measurements per storm', labels={'count': 'Number of measurements'})
    fig.update_layout(legend=dict(x=0.75, y=-0.2, orientation='h'))
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)