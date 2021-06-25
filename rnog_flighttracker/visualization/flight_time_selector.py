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

layout = html.Div([
    dcc.RangeSlider(
        id='read-time-slider',
        min=0,
        max=1,
        value=[0, 1],
        step=0.001
    )
])


@app.callback(
    Output('read-time-slider', 'marks'),
    [Input('reload-everything', 'n_clicks')]
)
def set_time_slider_marks(n_clicks):
    min_jd, max_jd = data_provider.get_read_time_range()
    time_marks = astropy.time.Time(np.linspace(min_jd, max_jd, 10), format='jd')
    marks = {}
    for i_mark, time_mark in enumerate(time_marks):
        marks[i_mark * .1] = time_mark.strftime('%H:%M %d %b %Y')
    return marks
