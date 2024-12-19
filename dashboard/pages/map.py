import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

dash.register_page(__name__, path='/maps')

# Fusion des DataFrames
dfDevastatorAt = pd.read_csv("data/AL.csv")
dfDevastatorEP = pd.read_csv("data/EP.csv")
df = pd.concat([dfDevastatorAt, dfDevastatorEP])
df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce').dt.tz_localize(None)
df = df[df['DateTime'] >= '1950-01-01']

# Conversion des noeuds (kts) en km/h
df['Wind_kmh'] = df['Wind'] * 1.852

# Points de départ des ouragans
set_df = df.drop_duplicates(subset='Key')

# Création de la carte initiale
fig = go.Figure()

fig.add_trace(go.Scattermapbox(
    mode='markers',
    lon=set_df['Lon'],
    lat=set_df['Lat'],
    marker=dict(size=8, color='blue'),
    text=(
            'Name: ' + set_df['Name'] + '<br>' +
            'Key: ' + set_df['Key'] + '<br>' +
            'DateTime: ' + set_df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S') + '<br>' +
            'Wind: ' + set_df['Wind_kmh'].round(1).astype(str) + ' km/h<br>' +
            'Pressure: ' + set_df['Pressure'].astype(str)
    ),
    hoverinfo='text',
    customdata=set_df[['Key', 'DateTime', 'Wind', 'Pressure']].values,
))

fig.update_layout(
    title='Hurricane Starting Points',
    mapbox_style='carto-positron',
    mapbox=dict(center={'lat': 20, 'lon': -60}, zoom=3),
    height=700
)

begin_date = set_df['DateTime'].dt.year.iloc[0]
end_date = set_df['DateTime'].dt.year.iloc[-1]

# Création du graphique de densité
df_counts = df.groupby(['Lat', 'Lon']).size().reset_index(name='count')
density_fig = px.density_mapbox(df_counts, lat='Lat', lon='Lon', z='count', radius=15,
                            center=dict(lat=20, lon=-60), zoom=3,
                            mapbox_style="open-street-map",
                            height=700,
                            title='Hurricane Density Map')
                            

layout = html.Div(children=[
    html.H3('Hurrican path', className='text-center mt-3'),

    # Date range slider
    html.Div(className='RadioButton mt-3', children=[
        html.P('This section displays the starting points of hurricanes on a map.'),
        html.P('You can select a date range to display the hurricanes that started in that range.'),
        html.P('Click on a hurricane to see its path.'),
        html.P('Click on the "Clear Selection" button to clear the selected hurricane path.'),
        html.Br(),
        html.Label('Select Date Range:', className="label"),
        dcc.RangeSlider(begin_date, end_date, step=1,
                        marks={str(year): str(year) for year in range(begin_date, end_date + 1, 10)},
                        value=[begin_date, end_date], allowCross=False, id='date_select',
                        tooltip={'placement': 'bottom', 'always_visible': True}),
        html.Button("Clear Selection", id="clear-btn", className="btn btn-primary", n_clicks=0),
    ]),

    dcc.Graph(id='map', figure=fig, config={'scrollZoom': True, 'displayModeBar': True}),
    html.Div(id='output-container-date-picker-range'),

    # Conteneur pour le graphique d'évolution du vent
    html.Div(id='hurricane-wind-graph', children=[]),
    
    html.Div(className='separator'),    
    html.H3('Heatmap', className='text-center mt-3'),
    
    html.Div(className='RadioButton mt-3', children=[
        html.P('This section displays the density of hurricanes on a map.'),
        html.P('The color intensity represents the number of hurricanes in a specific area.'),
    ]),
    
    dcc.Graph(id='density-map', figure=density_fig, config={'scrollZoom': True, 'displayModeBar': True}),

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


# Callback pour mettre à jour la carte en fonction de la plage de dates
@dash.callback(
    Output('map', 'figure', allow_duplicate=True),
    [Input('date_select', 'value'),
     Input('map', 'relayoutData')],
    prevent_initial_call=True)
def update_output(value, relayoutData):
    start_date = pd.to_datetime(f"{value[0]}-01-01")
    end_date = pd.to_datetime(f"{value[1]}-12-31")

    if relayoutData is not None and 'mapbox.center' in relayoutData:
        map_center = relayoutData['mapbox.center']
        map_zoom = relayoutData['mapbox.zoom']
    else:
        map_center = {'lat': 20, 'lon': -60}
        map_zoom = 3

    chosen_value = set_df[(set_df['DateTime'] >= start_date) & (set_df['DateTime'] <= end_date)]
    updated_fig = drawmap(chosen_value)
    updated_fig.update_layout(
        title=f'Hurricane Starting Points: {value[0]} to {value[1]}',
        mapbox_style='carto-positron',
        mapbox=dict(center=map_center, zoom=map_zoom),
        height=700
    )
    return updated_fig


# Callback pour afficher le chemin de l'ouragan et le graphique d'évolution du vent
@dash.callback(
    [Output('map', 'figure', allow_duplicate=True),
     Output('hurricane-wind-graph', 'children')],
    [Input('map', 'clickData'),
     Input('date_select', 'value'),
     Input('map', 'relayoutData')],
    prevent_initial_call=True
)
def display_path_and_wind_graph_on_click(clickData, value, relayoutData):
    if clickData is None:
        return dash.no_update, dash.no_update

    selected_key = clickData['points'][0]['customdata'][0]

    if relayoutData is not None and 'mapbox.center' in relayoutData:
        map_center = relayoutData['mapbox.center']
        map_zoom = relayoutData['mapbox.zoom']
    else:
        map_center = {'lat': 20, 'lon': -60}
        map_zoom = 3

    selected_key = str(selected_key).strip()
    df['Key'] = df['Key'].astype(str).str.strip()
    chosen_value = set_df[(set_df['DateTime'] >= pd.to_datetime(f"{value[0]}-01-01")) & (set_df['DateTime'] <= pd.to_datetime(f"{value[1]}-12-31"))]
    hurricane_details = df[df['Key'] == selected_key]

    min_time = hurricane_details['DateTime'].min()
    max_time = hurricane_details['DateTime'].max()
    hurricane_details['time_normalized'] = (hurricane_details['DateTime'] - min_time) / (max_time - min_time)
    path_fig = drawmap(chosen_value)

    for i in range(len(hurricane_details) - 1):
        path_fig.add_trace(go.Scattermapbox(
            mode='lines',
            lon=hurricane_details['Lon'].iloc[i:i + 2],
            lat=hurricane_details['Lat'].iloc[i:i + 2],
            line=dict(
                width=4,
                color='red' if hurricane_details['Status'].iloc[i] == 'HU' else 'blue'
            ),
            hoverinfo='text',
            text=hurricane_details['Name'].iloc[i],
            showlegend=False
        ))

    start_point = hurricane_details.iloc[0]
    end_point = hurricane_details.iloc[-1]

    path_fig.add_trace(go.Scattermapbox(
        mode='markers',
        lon=[start_point['Lon']],
        lat=[start_point['Lat']],
        marker=dict(size=12, color='green', symbol='circle'),
        text='Start',
        hoverinfo='text'
    ))

    path_fig.add_trace(go.Scattermapbox(
        mode='markers',
        lon=[end_point['Lon']],
        lat=[end_point['Lat']],
        marker=dict(size=12, color='red', symbol='x'),
        text='End',
        hoverinfo='text'
    ))

    path_fig.update_layout(
        mapbox_style='carto-positron',
        mapbox=dict(center=map_center, zoom=map_zoom),
        title=f'Hurricane Path for {selected_key}'
    )
        
    path_fig.update_layout(showlegend=False)

    # Graphique des vitesses de vent
    wind_fig = go.Figure()

    wind_fig.add_trace(go.Scatter(
        x=hurricane_details['DateTime'],
        y=hurricane_details['Wind_kmh'],
        mode='lines+markers',
        name='Wind Speed (km/h)',
        line=dict(color='blue')
    ))

    # Ajouter des zones rouges pour chaque ouragan quand le status est HU
    for i in range(len(hurricane_details)):
        if hurricane_details['Status'].iloc[i] == 'HU':
            wind_fig.add_vrect(
                x0=hurricane_details['DateTime'].iloc[i],
                x1=hurricane_details['DateTime'].iloc[i + 1] if i + 1 < len(hurricane_details) else hurricane_details['DateTime'].iloc[i],
                fillcolor='red',
                opacity=0.2,
                layer='below',
                line_width=0
            )
                
    wind_fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        name='Red Zone for Hurricane',
        marker=dict(color='red', size=10),
        showlegend=True
    ))

    wind_fig.update_layout(
        title='Wind Speed Over Time',
        xaxis_title='Date',
        yaxis_title='Wind Speed (km/h)',
        height=400
    )

    return path_fig, dcc.Graph(figure=wind_fig)



# Callback pour effacer les données de clic
@dash.callback(
    [Output('map', 'clickData'), Output('map', 'figure', allow_duplicate=True)],
    [Input('clear-btn', 'n_clicks'),
     Input('date_select', 'value')],
    prevent_initial_call=True
)
def clear_click_data(n_clicks, value):
    if n_clicks > 0:
        chosen_value = set_df[(set_df['DateTime'] >= pd.to_datetime(f"{value[0]}-01-01")) & (
                    set_df['DateTime'] <= pd.to_datetime(f"{value[1]}-12-31"))]
        to_ret = drawmap(chosen_value)
        to_ret.update_layout(
            mapbox_style='carto-positron',
            title=f'Hurricane Path',
            height=700,
            mapbox=dict(
                center={'lat': 20, 'lon': -60},
                zoom=3
            ),
            coloraxis_showscale=False
        )
        return None, to_ret
    return dash.no_update, dash.no_update


# Fonction pour dessiner la carte
def drawmap(dfDraw):
    updated_fig = go.Figure()
    updated_fig.data = []

    dfDraw['Color'] = dfDraw['Status'].apply(
        lambda x: 'red' if x == 'HU' else 'green')

    updated_fig.add_trace(go.Scattermapbox(
        mode='markers',
        lon=dfDraw['Lon'],
        lat=dfDraw['Lat'],
        marker=dict(size=7, color=dfDraw['Color']),
        text=(
                'Name: ' + dfDraw['Name'] + '<br>' +
                'Key: ' + dfDraw['Key'] + '<br>' +
                'DateTime: ' + dfDraw['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S') + '<br>' +
                'Wind: ' + dfDraw['Wind_kmh'].round(1).astype(str) + ' km/h<br>' +
                'Pressure: ' + dfDraw['Pressure'].astype(str)
        ),
        hoverinfo='text',
        customdata=dfDraw[['Key', 'DateTime', 'Wind', 'Pressure']].values
    ))

    return updated_fig
