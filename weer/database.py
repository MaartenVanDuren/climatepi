import sys
from influxdb import InfluxDBClient
import datetime
import traceback


class Database:
    def __init__(self):
        self._database_name = 'sensordata'
        self._db = InfluxDBClient('localhost', 8086, 'root', 'root')
        if self._database_name not in self._db.get_list_database():
            self._db.create_database(self._database_name)
            self._db.create_retention_policy(
                name=self._database_name + '_retention_12weeks',
                duration='12w',
                replication='1',
                database=self._database_name,
                default=True)
        self._db.switch_database(self._database_name)

    def write(self, weather_time, humidity_outside, temperature_outside, humidity_outside_to_inside):
        try:
            self._db.write_points(
                [{
                    'measurement': 'humidity_outside',
                    'fields': {
                        'value': humidity_outside
                    },
                    'time': weather_time
                }])
        except:
            #print('Error from weather app while writing humidity outside to influxdb:')
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            pass

        try:
            self._db.write_points(
                [{
                    'measurement': 'temperature_outside',
                    'fields': {
                        'value': temperature_outside
                    },
                    'time': weather_time
                }])
        except:
            #print('Error from weather app while writing temperature outside to influxdb:')
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            pass

        try:
            self._db.write_points(
                [{
                    'measurement': 'humidity_outside_to_inside',
                    'fields': {
                        'value': humidity_outside_to_inside
                    },
                    'time': weather_time
                }])
        except:
            #print('Error from weather app while writing humidity outside to inside to influxdb:')
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            pass

    def get_inside_temperature_at(self, timestamp=datetime.datetime.now().isoformat()):
        try:
            return(list(
                self._db.query('SELECT last("value") FROM "temperature" WHERE time <= \'{0}\' ORDER BY DESC LIMIT 1'
                               .format(timestamp)).get_points())[0]['last'])
        except:
            #print('Error from weather app while querying inside temperature from influxdb:')
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            return None
