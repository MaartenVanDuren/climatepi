#!/usr/bin/python3

import sys
import time
from database import Database
import serial
from datamap import datamap, fmt
import struct
import traceback


def parse_data(data):
    for n, x in enumerate(data):
        value = datamap[n][1](x)
        if isinstance(value, list) or isinstance(value, map):
            for i in zip(datamap[n][2], value, datamap[n][5]):
                if i[0]:
                    yield i
        elif datamap[n][2]:
            if value < 0:
                yield datamap[n][2], 0, datamap[n][5]
            yield datamap[n][2], value, datamap[n][5]

database = Database()

print('Start cv controller')
#port='/dev/ttyAMA0',
serialInterface = serial.Serial(port='/dev/serial0',
                                baudrate=9600,
                                timeout=0,
                                parity='N',
                                bytesize=8,
                                stopbits=1)
serialInterface.flushInput()
serialInterface.flushOutput()

print('Serial interface connected')  # Debug

while True:
    try:
        time.sleep(1) # second

        print('Requesting data from serial interface...')  # Debug

        # Request Remeha CV for information.
        #serialInterface.write(bytearray.fromhex('02FE000508010BD49C03')) # identification 1
        #serialInterface.write(bytearray.fromhex('02FE010508010BE95C03')) # identification 2
        
        serialInterface.write(bytearray.fromhex('02FE010508020169AB03')) # sample

        time.sleep(1) # second

        print('Reading data from serial interface...')  # Debug

        # Read response.
        line = serialInterface.read(serialInterface.inWaiting())

        print('Parsing data from serial interface...')  # Debug
        
        # Convert to parsed hex representation with leading start byte.
        #line = (bytearray.fromhex('02') + line).hex()
        line = line.hex()

        # If the response was not complete, try again.
        if len(line) != 148:
            print('Received data not 148 bytes long, resetting serial interface...')  # Debug
            print('len(line) = ' + str(len(line)))  # DEBUG
            print('line = ' + str(line))  # DEBUG
            serialInterface.close()
            serialInterface.open()
            serialInterface.flushInput()
            serialInterface.flushOutput()
            continue

        print('Parsing received data...')  # Debug

        # Convert to bytes array.
        line = bytearray.fromhex(line)

        # Parse data.
        unpacked = struct.unpack(fmt, line)

        stats = list(parse_data(unpacked))

        cv_stats = [{'measurement': s[0], 'fields': {'value': s[1]}} for s in stats if s[0] in
            ['ww_warmtevraag', 'ventilator_setpoint', 'ventilator_toeren',
            'beschikbaar_vermogen', 'pomp', 'gewenst_vermogen', 'geleverd_vermogen',
            'anti_legionella', 'ww_blokkering', 'ww_eco', 'vorstbeveiliging', 'mod_warmtevraag',
            'mod_regelaar', 'ww_vrijgave', 'cv_vrijgave', 'min_gasdruk', 'tapschakelaar', 'ionisatie',
            'vrijgave_ingang', 'blokkerende_ingang', 'status', 'substatus']]
        cv_stats += [{'measurement': s[0], 'fields': {'value': float(s[1])}} for s in stats if s[0] in
            ['ruimte_setpoint', 'ionisatie_stroom']]
        cv_stats += [{'measurement': s[0], 'fields': {'value': float(round(s[1], 1))}} for s in stats if s[0] in
            ['waterdruk', 'cv_setpoint', 'ww_setpoint', 'intern_setpoint']]
        cv_stats += [{'measurement': s[0], 'fields': {'value': float(round(s[1], 2))}} for s in stats if s[0] in
            ['ruimte_temp', 'aanvoer_temp', 'retour_temp', 'automaat_temp', 'regel_temp', 'tapdebiet']]

        database.write(cv_stats)

        print('Data written to database')  # Debug
    except Exception as e:
        print('Exception, resetting serial interface. Exception: ' + str(e))  # Debug

        #print('Error from cv controller app while reading cv sample:')
        #exc_type, exc_value, exc_traceback = sys.exc_info()
        #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

        time.sleep(10) # seconds
        serialInterface.close()
        time.sleep(10) # seconds
        serialInterface.open()
        serialInterface.flushInput()
        serialInterface.flushOutput()
        time.sleep(2) # seconds

serialInterface.close()
print('Stopped cv controller')
