import numpy as np
import plotly.graph_objs as go
import astropy.time

from dash import dcc, html
from dash.dependencies import Input, Output, State
import rnog_flighttracker.get_flight_data
from rnog_flighttracker.visualization.app import app


data_provider = rnog_flighttracker.get_flight_data.FlightDataProvider()
plotlyconfig = {'topojsonURL': 'http://127.0.0.1:8080/assets/'}
layout = html.Div([
    html.Button('Reload', id='reload-everything'),
    dcc.Graph(
        id='flight-map-plot',
        # config=plotlyconfig
    )
])


@app.callback(
    Output('flight-map-plot', 'figure'),
    [Input('read-time-slider', 'value')])
def draw_flight_map(read_time_range):

    hex_codes = data_provider.get_hex_codes()
    min_jd, max_jd = data_provider.get_read_time_range()
    min_time = astropy.time.Time(min_jd + read_time_range[0] * (max_jd - min_jd), format='jd').datetime
    max_time = astropy.time.Time(min_jd + read_time_range[1] * (max_jd - min_jd), format='jd').datetime

    summit_lat = 72.580389
    summit_lon = -38.456889
    plots = [dict(type='scattergeo',
            lon=[summit_lon],
            lat=[summit_lat],
            mode='markers',
            name='Summit Station',
            marker=dict(color=['black'], size=10))]
    
    for i_hex, hex_code in enumerate(hex_codes):
        flight_data = np.array(data_provider.get_flight_paths(hex_code, min_time, max_time))

        flight_number = data_provider.get_flight_number(hex_code)
        if len(flight_data) == 0:
            continue
        
        path = np.array(flight_data[:, : 2], dtype=float)
        invalid_value_filter = path[:, 0] > -999.
        plots.append(dict(
            type='scattergeo',
            lon=path[:, 1][invalid_value_filter],
            lat=path[:, 0][invalid_value_filter],
            mode='markers',
            name='{} [{}]'.format(flight_number, hex_code)
        ))
    
    fig = go.Figure(plots)
    
    fig.update_layout(
        geo=dict(
            scope='world',
            projection_type='azimuthal equidistant',
            lonaxis = dict(
                showgrid = True,
                gridwidth = 0.5,
                range= [-60, -20],
                dtick = 10
            ),
            lataxis = dict(
                showgrid = True,
                gridwidth = 0.5,
                range= [60, 85],
                dtick = 5
            )
        ),
        height=700)

    return fig
