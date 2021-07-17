from rnog_flighttracker.visualization.app import app
import dash_html_components as html
import dash
import argparse
import rnog_flighttracker.visualization.flight_map
import rnog_flighttracker.get_flight_data
import rnog_flighttracker.visualization.flight_time_selector


argparser = argparse.ArgumentParser()
argparser.add_argument('filename')
args = argparser.parse_args()
rnog_flighttracker.get_flight_data.FlightDataProvider().set_filename(args.filename)

app.title = 'RNO-G Flight Tracker'
app.layout = html.Div([
    rnog_flighttracker.visualization.flight_time_selector.layout,
    rnog_flighttracker.visualization.flight_map.layout
])
app.run_server(debug=True, port=8080)

