from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import dash

df_AL = pd.read_csv('data/AL.csv')
df_EP = pd.read_csv('data/EP.csv')
df_global = pd.read_csv('data/GlobalTemperatures.csv')

df_AL['DateTime'] = pd.to_datetime(df_AL['DateTime'])
df_EP['DateTime'] = pd.to_datetime(df_EP['DateTime'])
df_global['dt'] = pd.to_datetime(df_global['dt'])

df_AL['year'] = df_AL['DateTime'].dt.year
df_EP['year'] = df_EP['DateTime'].dt.year

df_AL = df_AL[df_AL['DateTime'].dt.year >= 1950]
df_EP = df_EP[df_EP['DateTime'].dt.year >= 1950]
df_global = df_global[df_global['dt'].dt.year >= 1950]

df_AL = df_AL.reset_index(drop=True)
df_EP = df_EP.reset_index(drop=True)
df_global = df_global.reset_index(drop=True)

df = pd.concat([df_AL, df_EP])

df = df.reset_index(drop=True)

df['year'] = df['DateTime'].dt.year

def knots_to_kmh(knots):
    return knots * 1.852

dash.register_page(__name__, path='/graphs')

# Callback to update the 'cases-by-year-bar' graph
@dash.callback(
    Output('cases-by-year-bar', 'figure'),
    Input('cases-by-year-bar', 'id'))
def update_cases_by_year_bar(id):
    count = df.groupby('year').size().reset_index(name='count')

    fig = go.Figure()
    fig.add_trace(go.Bar(x=count['year'], y=count['count'], name='Number of cases by year'))
    fig.update_layout(
        title='Number of cases by year',
        xaxis_title='Year',
        yaxis_title='Number of cases',
        height=450
    )

    # Add rolling mean
    count['rolling_mean'] = count['count'].rolling(window=10).mean()
    fig.add_trace(go.Scatter(x=count['year'], y=count['rolling_mean'], mode='lines', name='Rolling mean of cases (10 years window)'))
    fig.update_layout(legend=dict(x=0.05, y=-1.25, orientation='h'))

    # Time series range slider
    fig.update_xaxes(rangeslider_visible=True)
    return fig

# Callback to update the 'wind-speed-by-year' graph
@dash.callback(
    Output('wind-speed-by-year', 'figure'),
    Input('wind-speed-by-year', 'id'))
def update_wind_speed_by_year(id):
    fig = go.Figure()
    # Maximum wind speed by year
    df['Wind_kmh'] = knots_to_kmh(df['Wind'])
    df_grouped_by_year_wind = df.groupby('year')['Wind_kmh'].max().reset_index(name='max_wind')
    fig.add_trace(go.Scatter(x=df_grouped_by_year_wind['year'], y=df_grouped_by_year_wind['max_wind'], mode='lines', name='Max wind speed by year', line=dict(color='blue')))

    # Minimum wind speed by year
    df_grouped_by_year_wind_min = df.groupby('year')['Wind_kmh'].min().reset_index(name='min_wind')
    fig.add_trace(go.Scatter(x=df_grouped_by_year_wind_min['year'], y=df_grouped_by_year_wind_min['min_wind'], mode='lines', name='Min wind speed by year', line=dict(color='green')))

    # Rolling mean max
    df_grouped_by_year_wind['rolling_mean'] = df_grouped_by_year_wind['max_wind'].rolling(window=10).mean()
    fig.add_trace(go.Scatter(x=df_grouped_by_year_wind['year'], y=df_grouped_by_year_wind['rolling_mean'], mode='lines', name='Rolling mean of max wind speed (10 years window)', line=dict(color='red')))

    # Rolling mean min
    df_grouped_by_year_wind_min['rolling_mean_min'] = df_grouped_by_year_wind_min['min_wind'].rolling(window=10).mean()
    fig.add_trace(go.Scatter(x=df_grouped_by_year_wind_min['year'], y=df_grouped_by_year_wind_min['rolling_mean_min'], mode='lines', name='Rolling mean of min wind speed (10 years window)', line=dict(color='orange')))

    fig.update_layout(
        legend=dict(x=0, y=-1.25, orientation='h'),
        title='Wind speed by year',
        xaxis_title='Year',
        yaxis_title='Wind speed (km/h)',
        height=450  # Fixed height
    )

    fig.update_xaxes(rangeslider_visible=True)
    return fig

# Callback to update the 'correlation-graph' graph
@dash.callback(
    Output('correlation-graph', 'figure'),
    Input('correlation-graph', 'id'))

def update_correlation_graph(id):

    df_global['year'] = pd.to_datetime(df_global['dt']).dt.year

    df_global_grouped = df_global.groupby('year')['LandAverageTemperature'].mean().reset_index(name='mean_temp')
    df_global_grouped['rolling_mean_temp'] = df_global_grouped['mean_temp'].rolling(window=10).mean()

    count = df.groupby('year').size().reset_index(name='count')
    count['rolling_mean'] = count['count'].rolling(window=10).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_global_grouped['year'], y=df_global_grouped['rolling_mean_temp'], mode='lines', name='Trend of temperature',))

    fig.add_trace(go.Scatter(x=count['year'], y=count['rolling_mean'], mode='lines', name='Trend of cases', yaxis='y2', line=dict(color='red')))

    fig.update_layout(
        title='Correlation of the Trend Temperature and Trend of Cases by Year',
        xaxis=dict(title='Year'),
        yaxis=dict(
            title='Temperature (°C)',
            range=[df_global_grouped['mean_temp'].min(), df_global_grouped['mean_temp'].max()]
        ),
        yaxis2=dict(
            title='Number of Cases',
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0, y=-1, orientation='h'),
        height=450
    )

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_xaxes(range=[1959, count['year'].max()])
    return fig

# Callback to update the 'cases-by-year-al-ep' graph
@dash.callback(
    Output('cases-by-year-al-ep', 'figure'),
    Input('cases-by-year-al-ep', 'id'))
def update_cases_by_year_al_ep(id):
    count_AL = df_AL.groupby('year').size().reset_index(name='count')
    count_EP = df_EP.groupby('year').size().reset_index(name='count')

    fig = make_subplots(rows=1, cols=2, subplot_titles=('Number of cases by year in AL', 'Number of cases by year in EP'))

    fig.add_trace(go.Bar(x=count_AL['year'], y=count_AL['count'], name='Number of cases by year in AL'), row=1, col=1)
    count_AL['rolling_mean'] = count_AL['count'].rolling(window=10).mean()
    fig.add_trace(go.Scatter(x=count_AL['year'], y=count_AL['rolling_mean'], mode='lines', name='Trend of cases in AL'), row=1, col=1)

    fig.add_trace(go.Bar(x=count_EP['year'], y=count_EP['count'], name='Number of cases by year in EP'), row=1, col=2)
    count_EP['rolling_mean'] = count_EP['count'].rolling(window=10).mean()
    fig.add_trace(go.Scatter(x=count_EP['year'], y=count_EP['rolling_mean'], mode='lines', name='Trend of cases in EP'), row=1, col=2)

    fig.update_layout(
        title_text='Number of cases by year in AL and EP',
        xaxis_title='Year',
        yaxis_title='Number of cases',
        legend=dict(x=0, y=-0.25, orientation='h'),
        height=450  # Hauteur fixe
    )
    return fig

# Callback to update the 'trends-graph' graph
@dash.callback(
    Output('trends-graph', 'figure'),
    Input('trends-graph', 'id'))
def update_trends_graph(id):
    count = df.groupby('year').size().reset_index(name='count')
    count['rolling_mean'] = count['count'].rolling(window=10).mean()
    count_AL = df_AL.groupby('year').size().reset_index(name='count')
    count_AL['rolling_mean'] = count_AL['count'].rolling(window=10).mean()
    count_EP = df_EP.groupby('year').size().reset_index(name='count')
    count_EP['rolling_mean'] = count_EP['count'].rolling(window=10).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=count['year'], y=count['rolling_mean'], mode='lines', name='Trend of cases'))
    fig.add_trace(go.Scatter(x=count_AL['year'], y=count_AL['rolling_mean'], mode='lines', name='Trend of cases in AL'))
    fig.add_trace(go.Scatter(x=count_EP['year'], y=count_EP['rolling_mean'], mode='lines', name='Trend of cases in EP'))
    fig.update_layout(
        title='Trends of cases by year',
        xaxis_title='Year',
        yaxis_title='Number of cases',
        legend=dict(x=0, y=-0.25, orientation='h'),
        height=450
    )    
    fig.update_xaxes(range=[1959, count['year'].max()])     # 1959: Due to the rolling mean
    
    return fig

# Callback to update the 'correlation-temp-hurricane-scatter' graph
@dash.callback(
    Output('correlation-temp-hurricane-scatter', 'figure'),
    Input('correlation-temp-hurricane-scatter', 'id'))
def update_correlation_temp_hurricane_scatter(id):
    df_global['year'] = pd.to_datetime(df_global['dt']).dt.year
    df_global_grouped = df_global.groupby('year')['LandAverageTemperature'].mean().reset_index(name='mean_temp')
    count = df.groupby('year').size().reset_index(name='count')
    df_corr = pd.merge(df_global_grouped, count, on='year')

    fig = px.scatter(df_corr, x='mean_temp', y='count', 
                     title='Correlation between temperature and number of hurricanes (trend)',
                     trendline="ols", trendline_color_override="red")
    fig.update_layout(
        xaxis_title='Tempurature (°C)',
        yaxis_title='Number of hurrican',
        height=450
    )
    return fig

# Callback to update the 'correlation-temp-hurricane-line' graph
@dash.callback(
    Output('correlation-temp-hurricane-line', 'figure'),
    Input('correlation-temp-hurricane-line', 'id'))
def update_correlation_temp_hurricane_line(id):
    df_global['year'] = pd.to_datetime(df_global['dt']).dt.year
    df_global_grouped = df_global.groupby('year')['LandAverageTemperature'].mean().reset_index(name='mean_temp')
    df_global_grouped['rolling_mean_temp'] = df_global_grouped['mean_temp'].rolling(window=10).mean()

    count = df.groupby('year').size().reset_index(name='count')
    count['rolling_mean_count'] = count['count'].rolling(window=10).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_global_grouped['year'], y=df_global_grouped['rolling_mean_temp'],
                             mode='lines', name='Temperature mean (trend)'))
    fig.add_trace(go.Scatter(x=count['year'], y=count['rolling_mean_count'],
                             mode='lines', name='Number of hurrican (trend)', yaxis='y2'))

    fig.update_layout(
        title='Correlation between temperature and number of hurricanes (trend)',
        xaxis_title='Year',
        yaxis_title='Temperature (°C)',
        yaxis2=dict(title='Number of hurrican', overlaying='y', side='right'),
        legend=dict(x=0, y=-0.75, orientation='h'),
        height=450
    )
    fig.update_xaxes(range=[1959, count['year'].max()])     # 1959: Due to the rolling mean
    fig.update_xaxes(rangeslider_visible=True)
    return fig


# Layout of the app
layout = html.Div(children=[
    html.H3(children="Number of case / Wind speeds", className='text-center mt-3'),

    # Première ligne avec deux graphiques
    html.Div(children=[
        # Premier graphique
        dcc.Graph(id='cases-by-year-bar'),

        # Deuxième graphique
        dcc.Graph(id='wind-speed-by-year'),
    ], style={'display': 'flex', 'width': '100%', 'margin-top': '20px'}),


    html.Div(className='separator'),

    # Section 2: Corrélation
    html.Div(children=[
        html.H3(children="Correlation Temperature / Number of Hurricanes", className='text-center mt-3'),
        html.Div(children=[
            # Premier graphique de corrélation (nuage de points)
            html.Div([
                dcc.Graph(id='correlation-temp-hurricane-scatter'),
            ], style={'width': '50%', 'display': 'inline-block'}),

            # Deuxième graphique de corrélation (lignes)
            html.Div([
                dcc.Graph(id='correlation-temp-hurricane-line'),
            ], style={'width': '50%', 'display': 'inline-block'}),
        ], style={'width': '100%'}),
    ]),

    html.Div(className='separator'),

    # Section 3: Comparaison AL et EP
    html.Div(children=[
        html.H3(children="Comparaison AL and EP", className='text-center mt-3'),
        html.Div(children=[
            dcc.Graph(id='cases-by-year-al-ep'),
        ], style={'width': '100%'}),
    ]),

    html.Div(className='separator'),

    # Section 4: Tendances
    html.H3(children="Trends", className='text-center mt-3'),
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(id='trends-graph'),
        ], style={'width': '100%'}),
    ]),

    # Footer
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