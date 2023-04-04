from get_flight_data import FlightDataProvider
import sys
import re
import gzip
import shutil
import os
import numpy as np
import json
import astropy.time
import argparse

"""
This script can be used to parse through flight-tracker DB files and filter out all flights with a flightnumber following the pattern "SKIER*".
A json file is created with the timing information of these flights.
"""


parser = argparse.ArgumentParser(description='Filter SKIER* flights and store time into json')   

parser.add_argument('inputfilename', type=str, nargs="*", help='path to flight-tracker db file(s)')
parser.add_argument('--json_file', type=str, help='File name for .json', default="selected_flights.json")

args = parser.parse_args()


fdp = FlightDataProvider()

data = []


for path in args.inputfilename:
    
    if path.endswith(".gz"):

        # On-the-fly unzipping 
        with gzip.open(path, 'rb') as f_in:
            file_name = os.path.join("/tmp/", os.path.basename(path).replace(".gz", ""))
            if not os.path.exists(file_name):
                with open(file_name, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                
            path = file_name

    fdp.set_filename(path)
    
    numbers = fdp.get_flight_numbers(unique=False)
    codes = fdp.get_hex_codes(unique=False)

    mask = np.array([re.search("SKIER", ele) != None for ele in numbers], dtype=bool)
        
    if not np.any(mask):
        continue

    selected_codes = np.unique(codes[mask])    
    print(f"Found {len(selected_codes)} flights in {path}")
    
    for code in selected_codes:
        selected_flight_numbers = np.unique(numbers[codes == code])
        t_min, t_max = fdp.get_time_stamps(hex_code=code)
        
        flight = {"hexcode": code, "t_min": t_min, "t_max": t_max, "flightnumbers": list(selected_flight_numbers)}
        
        print("Found flight {} ({}) from {} - {} ({:.2f}d)".format(
            code, ",".join(selected_flight_numbers),
            astropy.time.Time(t_min, format="unix").to_value("iso", subfmt="date_hm"), astropy.time.Time(t_max, format="unix").to_value("iso", subfmt="date_hm"), (t_max - t_min) / (24 * 3600)))
        
        data.append(flight)
        
        
with open(args.json_file, "w") as f:
    json.dump(data, f)