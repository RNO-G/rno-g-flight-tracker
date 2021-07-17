import numpy as np
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import rnog_flighttracker.get_flight_data
from rnog_flighttracker.visualization.app import app
from NuRadioReco.utilities import units
import plotly.graph_objs as go
import astropy.time

data_provider = rnog_flighttracker.get_flight_data.FlightDataProvider()
plotlyconfig = {'topojsonURL': 'http://127.0.0.1:8080/assets/'}
layout = html.Div([
    html.Button('Button', id='reload-everything'),
    dcc.Graph(
        id='flight-map-plot',
        config=plotlyconfig
    )
])


@app.callback(
    Output('flight-map-plot', 'figure'),
    [Input('read-time-slider', 'value')]
)
def draw_flight_map(read_time_range):
    hex_codes = data_provider.get_hex_codes()
    plots = []
    min_jd, max_jd = data_provider.get_read_time_range()
    min_time = astropy.time.Time(min_jd + read_time_range[0] * (max_jd - min_jd), format='jd').datetime
    max_time = astropy.time.Time(min_jd + read_time_range[1] * (max_jd - min_jd), format='jd').datetime
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
    summit_lat = 72.580389
    summit_lon = -38.456889
    plots.append(
        dict(
            type='scattergeo',
            lon=[summit_lon],
            lat=[summit_lat],
            mode='markers',
            name='Summit Station',
            marker=dict(
                color=['black'],
                size=10
            )
        )
    )
    fig = go.Figure(
        plots
    )
    fig.update_layout(
        geo=dict(
            scope='world',
            lonaxis_range=[-70, -10],
            lataxis_range=[55, 90],
            projection_type='azimuthal equidistant'
        ),
        # width=1000,
        height=700
    )
    return fig
