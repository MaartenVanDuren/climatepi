#!/usr/bin/python3

import requests
from database import Database
import urllib.request
import time
import sys
import traceback
import pandas as pd
import datetime


database = Database()
interval = 5  # in seconds, check each interval what to do

api_endpoint = 'http://climatepi:8080/api/'

temperature_to_cool = 22.0  # in Celsius, whenever the thermostat temperature is above this threshold, and outside is colder than inside, keep ventilation on to cool down inside

def mode_off():
    requests.post(api_endpoint + 'mode-off')

def mode_1():
    requests.post(api_endpoint + 'mode-1')

def mode_2():
    requests.post(api_endpoint + 'mode-2')

def mode_3():
    requests.post(api_endpoint + 'mode-3')


def startup():
    # Turn ventilation on.
    # For some reason, the unit itself goes into mode 2. So, start to mode 2, give it a second, and immediately switch to mode 1.
    mode_2()
    time.sleep(1)  # Give the unit 1 second to start.
    # Immediately (during spinning up), switch to mode 1.
    mode_1()
    time.sleep(120)  # 2 minutes to get reliable readings from the sensors.


mode_to_int = {
    'RelayMode.OFF': 0,
    'RelayMode.ONE': 1,
    'RelayMode.TWO': 2,
    'RelayMode.THREE': 3,
}


print('Start ventilatie controller')
startup()
while True:
    try:
        # Get current mode from the controller.
        current_mode = None
        # Get current mode.
        with urllib.request.urlopen(api_endpoint + 'mode') as url:
            # Parse data.
            current_mode = url.read().decode()
        
        # If the controller is off, that was for a reason, so do not turn it on.
        if 'RelayMode.OFF' in current_mode:
            continue


        # Get humidity of the last few seconds.
        humidity = database.get_inside_humidity_features(timespan=900)
        # Require a minimum of 5 data points, else change nothing.
        if humidity is None or humidity.shape[0] < 5:
            time.sleep(interval)
            continue

        # Get CV samples of the last few seconds.
        cv = database.get_cv_features(timespan=60)

        # Get temperature outside of the last hour.
        outside = database.get_outside_temperature_features(timespan=3600)

        # Decide desired mode for controlling temperature. First, check if all data is available to make the decision.
        desired_mode_cooling = None
        if cv is not None and not cv.empty and outside is not None and not outside.empty:
            # If inside is 'hot', and outside is cooler than inside.
            if cv['ruimte_temp'][-1] >= temperature_to_cool + .2 and outside['temperature_outside'][-1] < cv['ruimte_temp'][-1]:
                # Desire to cool a bit.
                desired_mode_cooling = 2
            # If inside is cool enough, or outside is hotter than inside.
            elif cv['ruimte_temp'][-1] < temperature_to_cool - .2 or outside['temperature_outside'][-1] >= cv['ruimte_temp'][-1]:
                # Desire to not cool.
                desired_mode_cooling = 1
        
        
        # Decide desired mode for controlling humidity.
        # Primary desire is to stay at the current mode, unless there is reason to increase or decrease the mode.
        desired_mode_humidity = mode_to_int.get(current_mode, 1)

        if 'RelayMode.ONE' in current_mode:
            if humidity['derivative1'][-1] >= 0.05 and humidity['derivative2'][-1] >= 0.0007:
                # Humidity is climbing at an increasing rate.
                if cv is not None and not cv.empty:
                    # CV samples are available.
                    if cv['ww_warmtevraag'][-1]:# and cv['tapdebiet'][-1] >= 5.0:
                        # Hot water is requested.
                        desired_mode_humidity = 2
                else:
                    # If no cv sample is available, change mode anyway.
                    desired_mode_humidity = 2

        if 'RelayMode.TWO' in current_mode:
            if humidity['derivative1'][-1] >= 0.05 and humidity['derivative2'][-1] >= 0.0007:
                # Humidity is climbing at an increasing rate.
                if cv is not None and not cv.empty:
                    # CV samples are available.
                    if cv['ww_warmtevraag'][-1]:# and cv['tapdebiet'][-1] >= 5.0:
                        # Hot water is requested.
                        desired_mode_humidity = 3
                else:
                    # If no cv sample is available, change mode anyway.
                    desired_mode_humidity = 3
            elif -0.02 <= humidity['derivative1'][-1] <= 0.01 and -0.00003 <= humidity['derivative2'][-1] <= 0.0003:
                # Humidity is fairly stable.
                desired_mode_humidity = 1

        if 'RelayMode.THREE' in current_mode:
            if humidity['derivative1'][-1] <= -0.01 and humidity['derivative2'][-1] >= 0.0007:
                # Humidity is decreasing at an increasing rate.
                desired_mode_humidity = 2
            if cv is not None and not cv.empty:
                # CV samples are available.
                if not cv['ww_warmtevraag'][-1]:# and cv['tapdebiet'][-1] <= 5.0:
                    # No hot water is requested.
                    if -0.02 <= humidity['derivative1'][-1] <= 0.01 and -0.00003 <= humidity['derivative2'][-1] <= 0.0003:
                        # Humidity is fairly stable.
                        desired_mode_humidity = 2
        

        # Actually switch modes, if needed.
        desired_mode = max([i for i in [desired_mode_humidity, desired_mode_cooling] + [1] if i])
        if desired_mode == 1 and 'RelayMode.ONE' not in current_mode:
            mode_1()
        elif desired_mode == 2 and 'RelayMode.TWO' not in current_mode:
            mode_2()
        elif desired_mode == 3 and 'RelayMode.THREE' not in current_mode:
            mode_3()

    except:
        # print('At {0}:'.format(datetime.datetime.now().isoformat()))
        # print('Error from ventilatie controller:')
        # exc_type, exc_value, exc_traceback = sys.exc_info()
        # traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
        pass

    time.sleep(interval)

print('Stopped ventilatie controller')
