#!/usr/bin/python2

import sys
import Adafruit_DHT
import time
from database import Database


database = Database()

print('Start reading sensor')
while True:
    # Signal connector at GPIO4
    humidity, temperature = Adafruit_DHT.read_retry(sensor=Adafruit_DHT.common.DHT22, pin=4)
    if humidity is not None and 0 <= humidity <= 100 and temperature is not None and -10 <= temperature <= 50:
        database.write(humidity, temperature)
    time.sleep(2) # seconds

print('Stopped reading sensor')
