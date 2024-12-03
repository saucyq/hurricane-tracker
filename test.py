import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.express as px
from datetime import date

from narwhals import Datetime

df = pd.read_csv('data/AL.csv')
df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce').dt.tz_localize(None)
df  = df[df['DateTime'] >= '1950-01-01']
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
begin_date = set_df['DateTime'].dt.year.iloc[0]
end_date = set_df['DateTime'].dt.year.iloc[-1]
# "on load" was not working on jupyter so I install dash
app = dash.Dash(__name__)
app.layout = html.Div([
#time range
dcc.RangeSlider(begin_date, end_date,step=1,
                marks={
                    str(begin_date): str(begin_date),
                    str(end_date): str(end_date)
                },
                value=[begin_date, end_date],
                allowCross=False,
                id="date_select",
                tooltip={"placement": "bottom", "always_visible": True}),
    dcc.Graph(
        id='map',
        figure=fig,
        config={'scrollZoom': True, 'displayModeBar': True}
    ),
    html.Div(id='output-container-date-picker-range')
])


@callback(
    Input('date_select', 'value'))
def update_output(value):
    print( 'You have selected "{}"'.format(value))
# Dash Layout
@app.callback(
    Output('map', 'figure'),
    Input('map', 'clickData')
)

def display_path_on_click(clickData):
    # Default figure
    path_fig = go.Figure(fig)

    if clickData is None:
        return path_fig

    # Get the selected hurricane's Key from the clickData (extract the first element)
    selected_key = clickData['points'][0]['customdata'][0]  # First element is the Key (e.g., 'AL051874')

    selected_key = str(selected_key).strip()
    df['Key'] = df['Key'].astype(str).str.strip()

    hurricane_details = df[df['Key'] == selected_key]

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

    return path_fig
@callback(
    Output('output-container-date-picker-range', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'Start Date: ' + start_date_string + ' | '
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%B %d, %Y')
        string_prefix = string_prefix + 'End Date: ' + end_date_string
    if len(string_prefix) == len('You have selected: '):
        return 'Select a date to see it displayed here'
    else:
        return string_prefix
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)