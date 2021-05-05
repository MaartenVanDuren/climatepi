#!/usr/bin/python3

import datetime
from database import Database
from weathercalculator import WeatherCalculator
import json
import urllib.request
import time
import sys
import traceback


database = Database()

print('Start weather service')
while True:
    try:
        with urllib.request.urlopen('https://api.buienradar.nl/data/public/1.1/jsonfeed') as url:
            # Parse JSON data.
            data = json.loads(url.read().decode())
            # Get weather data from weather station Herwijnen.
            station = list([s
                            for s in data['buienradarnl']['weergegevens']['actueel_weer']['weerstations']['weerstation']
                            if s['@id'] == '6356'])
            # Calculate temperature and relative humidity.
            weather_time = datetime.datetime.strptime(station[0]['datum'], '%m/%d/%Y %H:%M:%S')
            weather_time = weather_time - datetime.timedelta(seconds=time.localtime().tm_gmtoff)
            weather_time = weather_time.isoformat(sep=' ')
            temperature_outside = float(station[0]['temperatuurGC'])
            humidity_outside = float(station[0]['luchtvochtigheid'])

            humidity_outside_to_inside = WeatherCalculator.inside_relative_humidity_from_conditions(
                outside_humidity=humidity_outside,
                outside_temperature=temperature_outside,
                desired_temperature=database.get_inside_temperature_at(timestamp=weather_time)
            )

            # Write to database.
            database.write(weather_time, humidity_outside, temperature_outside, humidity_outside_to_inside)
    except:
        #print('Error from weather app while reading and parsing weather data:')
        #exc_type, exc_value, exc_traceback = sys.exc_info()
        #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
        pass

    time.sleep(300)  # 5 minutes

print('Stopped weather service')
