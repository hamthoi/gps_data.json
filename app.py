from counterfit_connection import CounterFitConnection
CounterFitConnection.init('127.0.0.1', 5000)

import time
import counterfit_shims_serial
import pynmea2
import json
import os
serial = counterfit_shims_serial.Serial('/dev/ttyAMA0')

def send_gps_data(line):
    msg = pynmea2.parse(line)
    if msg.sentence_type == 'GGA':
        lat = pynmea2.dm_to_sd(msg.lat)
        lon = pynmea2.dm_to_sd(msg.lon)

        if msg.lat_dir == 'S':
            lat = lat * -1

        if msg.lon_dir == 'W':
            lon = lon * -1

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(lon,5), round(lat,5)]
            },
            "properties": {}
        }

        file_path = "gps_data.json"

        # Check if file exists and is not empty
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            # Open the file in read mode to read existing content
            with open(file_path, 'r') as file:
                # Read existing JSON content
                data = json.load(file)
            # Append the new feature to the "features" array
            data["features"].append(feature)
            # Open the file in write mode to overwrite existing content
            with open(file_path, 'w') as file:
                # Write updated JSON content
                json.dump(data, file, indent=4)
        else:
            # If file doesn't exist or is empty, create a new JSON structure
            data = {
                "type": "FeatureCollection",
                "features": [feature]
            }
            # Write JSON content to the file
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

while True:
    line = serial.readline().decode('utf-8')

    while len(line) > 0:
        send_gps_data(line)
        line = serial.readline().decode('utf-8')

    time.sleep(5)