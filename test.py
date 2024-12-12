import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.express as px
from datetime import date

df = pd.read_csv('data/AL.csv')
df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce').dt.tz_localize(None)
df = df[df['DateTime'] >= '1950-01-01']
#first point of the hurricane
set_df = df.drop_duplicates(subset='Key')
exploitedSet = df
ep = pd.read_csv('data/EP.csv')
ep['DateTime'] = pd.to_datetime(ep['DateTime'], errors='coerce').dt.tz_localize(None)
ep = ep[ep['DateTime'] >= '1950-01-01']
#first point of the hurricane
set_ep = ep.drop_duplicates(subset='Key')
# Create a basic map of the hurricane starting points using Plotly
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
            'Wind: ' + set_df['Wind'].astype(str) + '<br>' +
            'Pressure: ' + set_df['Pressure'].astype(str)
    ),
    hoverinfo='text',
    customdata=set_df[['Key', 'DateTime', 'Wind', 'Pressure']].values,  # Pass custom data for hover
))

# Update layout
fig.update_layout(
    title='Hurricane Starting Points',
    mapbox_style='carto-positron',
    mapbox=dict(center={'lat': 20, 'lon': -60}, zoom=3),
    height=900
)

begin_date = set_df['DateTime'].dt.year.iloc[0]
end_date = set_df['DateTime'].dt.year.iloc[-1]
# "on load" was not working on jupyter so I install dash
app = dash.Dash(__name__)
app.layout = html.Div([
    #time range
    dcc.RangeSlider(begin_date, end_date, step=1,
                    marks={
                        str(begin_date): str(begin_date),
                        str(end_date): str(end_date)
                    },
                    value=[begin_date, end_date],
                    allowCross=False,
                    id="date_select",
                    tooltip={"placement": "bottom", "always_visible": True}),

    html.Button("Clear Selection", id="clear-btn", n_clicks=0),
    dcc.Graph(
        id='map',
        figure=fig,
        config={'scrollZoom': True, 'displayModeBar': True}
    ),
    html.Div(id='output-container-date-picker-range')
])


@app.callback(
    Output('map', 'figure', allow_duplicate=True),
    Input('date_select', 'value'),
    prevent_initial_call=True)
def update_output(value):
    print("slide")
    # Convert the selected range into date objects
    start_date = pd.to_datetime(f"{value[0]}-01-01")
    end_date = pd.to_datetime(f"{value[1]}-12-31")


    # Filter the data based on the selected date range
    choosen_value = set_df[(set_df['DateTime'] >= start_date) & (set_df['DateTime'] <= end_date)]
    # Print the filtered data to check if it's correct
    # Create a new figure to replace the previous one

    updated_fig=drawmap(choosen_value)
    # Update layout, including the title
    updated_fig.update_layout(
        title=f'Hurricane Starting Points: {value[0]} to {value[1]}',
        mapbox_style='carto-positron',
        mapbox=dict(center={'lat': 20, 'lon': -60}, zoom=3),
        height=900
    )
    return updated_fig


# Dash Layout
@app.callback(
    Output('map', 'figure', allow_duplicate=True),
    [Input('map', 'clickData'),
     Input('date_select', 'value')],
    prevent_initial_call=True
)
def display_path_on_click(clickData, value):
    # Default figure
    path_fig = go.Figure(fig)
    if clickData is None:
        return dash.no_update
    print(clickData)
    # Get the selected hurricane's Key from the clickData (extract the first element)
    selected_key = clickData['points'][0]['customdata'][0]  # First element is the Key (e.g., 'AL051874')

    selected_key = str(selected_key).strip()
    print(selected_key)
    df['Key'] = df['Key'].astype(str).str.strip()
    choosen_value = set_df[str(value[0]) + '-01-01' <= set_df['DateTime']]
    choosen_value = choosen_value[choosen_value['DateTime'] <= str(value[1])]
    hurricane_details = df[df['Key'] == selected_key]

    # norm date to get a linear color diff, to know where it begin
    min_time = hurricane_details['DateTime'].min()
    max_time = hurricane_details['DateTime'].max()
    hurricane_details['time_normalized'] = (hurricane_details['DateTime'] - min_time) / (max_time - min_time)
    path_fig=drawmap(choosen_value)
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
        height=900,
        mapbox=dict(
            center={'lat': 20, 'lon': -60},  # Fixed center for the map
            zoom=3  # Fixed zoom level
        ),
        coloraxis_showscale=False
    )
    path_fig.update_layout(mapbox_style='carto-positron')

    return path_fig
@app.callback(
    [Output('map', 'clickData'),Output('map', 'figure', allow_duplicate=True)],
    [Input('clear-btn', 'n_clicks'),
     Input('date_select', 'value')],
    prevent_initial_call=True
)
def clear_click_data(n_clicks,value):
    print(n_clicks)
    if n_clicks > 0:
        choosen_value = set_df[str(value[0]) + '-01-01' <= set_df['DateTime']]
        choosen_value = choosen_value[choosen_value['DateTime'] <= str(value[1])]
        to_ret =drawmap(choosen_value)
        to_ret.update_layout(
            mapbox_style='carto-positron',
            title=f'Hurricane Path',
            height=900,
            mapbox=dict(
                center={'lat': 20, 'lon': -60},  # Fixed center for the map
                zoom=3  # Fixed zoom level
            ),
            coloraxis_showscale=False
        )
        return None,to_ret  # Reset clickData to None when the button is clicked
    return dash.no_update,dash.no_update  # Otherwise, do nothing

def drawmap(dfDraw):
    updated_fig = go.Figure()

    # Clear any previous data from the figure (no traces in this case)
    updated_fig.data = []

    # Add the new data as a trace
    updated_fig.add_trace(go.Scattermapbox(
        mode='markers',
        lon=dfDraw['Lon'],
        lat=dfDraw['Lat'],
        marker=dict(size=7, color='blue'),
        text=(
                'Name: ' + dfDraw['Name'] + '<br>' +
                'Key: ' + dfDraw['Key'] + '<br>' +
                'DateTime: ' + dfDraw['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S') + '<br>' +
                'Wind: ' + dfDraw['Wind'].astype(str) + '<br>' +
                'Pressure: ' + dfDraw['Pressure'].astype(str)
        ),
        hoverinfo='text',  # Display custom hover text,

        customdata=dfDraw[['Key', 'DateTime', 'Wind', 'Pressure']].values
    ))

    # Update layout, including the title

    return updated_fig
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
