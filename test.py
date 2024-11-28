import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

df = pd.read_csv('data/AL.csv')
#first point of the hurricane
set_df = df.drop_duplicates(subset='Key')

# Create a basic map of the hurricane starting points using Plotly
fig = px.scatter_mapbox(
    set_df,
    lat='Lat',
    lon='Lon',
    hover_name='Name',
    hover_data={'Key': True, 'DateTime': True, 'Wind': True, 'Pressure': True},
    title='Hurricane Starting Points',
    zoom=3,
    height=600
)
fig.update_layout(mapbox_style='carto-positron')

# "on load" was not working on jupyter so I install dash
app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Graph(
        id='map',
        figure=fig,
        config={'scrollZoom': True, 'displayModeBar': True}
    )
])
# Dash Layout
@app.callback(
    Output('map', 'figure'),
    Output('hurricane-info', 'children'),
    Input('map', 'clickData')
)
def display_path_on_click(clickData):
    # Default figure
    path_fig = go.Figure(fig)

    if clickData is None:
        return path_fig, 'Click on a point to see the full path.'

    # Get the selected hurricane's Key from the clickData (extract the first element)
    selected_key = clickData['points'][0]['customdata'][0]  # First element is the Key (e.g., 'AL051874')

    selected_key = str(selected_key).strip()
    df['Key'] = df['Key'].astype(str).str.strip()

    hurricane_details = df[df['Key'] == selected_key]
    hurricane_details['DateTime'] = pd.to_datetime(hurricane_details['DateTime'])

    # norm date to get a linear color diff, to know where it begin
    min_time = hurricane_details['DateTime'].min()
    max_time = hurricane_details['DateTime'].max()
    hurricane_details['time_normalized'] = (hurricane_details['DateTime'] - min_time) / (max_time - min_time)

    # draw line, purple with a marker for the beggining and one for the end
    path_fig.add_trace(go.Scattermapbox(
        mode='lines',
        lon=hurricane_details['Lon'],
        lat=hurricane_details['Lat'],
        line=dict(
            width=4,
            color='purple',
        ),
        hoverinfo='text',
        customdata=hurricane_details['Key'],
        text=hurricane_details['Name'],
        showlegend=False  # No legend for individual segments
    ))

    start_point = hurricane_details.iloc[0]
    end_point = hurricane_details.iloc[-1]

    path_fig.add_trace(go.Scattermapbox(
        mode='markers',
        lon=[start_point['Lon'], end_point['Lon']],
        lat=[start_point['Lat'], end_point['Lat']],
        marker=dict(
            size=10,
            color=['green', 'red'],
            symbol='circle'
        ),
        text=['Start', 'End'],
        hoverinfo='text',
        showlegend=False
    ))
    path_fig.update_layout(
        mapbox_style='carto-positron',
        title=f'Hurricane Path: {selected_key}',
        height=600,
        mapbox=dict(
            center={'lat': 20, 'lon': -60},  # Fixed center for the map
            zoom=3  # Fixed zoom level
        ),
        coloraxis_showscale=False
    )

    hurricane_info = f'Selected Hurricane: {selected_key}'
    #seems to need 2 parameters
    return path_fig, hurricane_info

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)