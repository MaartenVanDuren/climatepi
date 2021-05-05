import pandas as pd
import sys
from influxdb import InfluxDBClient
import traceback


class Database:
    def __init__(self):
        self._database_name = 'cvdata'
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

    def write(self, values):
        try:
            self._db.write_points(values)
        except:
            #print('Error from sensor app while writing humidity to influxdb:')
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            pass
