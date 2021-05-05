import sys
from influxdb import InfluxDBClient
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

    def write(self, mode, tag_source):
        try:
            self._db.write_points(
                [{
                    'measurement': 'mode',
                    'fields': {
                        'value': int(mode)
                    },
                    'tags': {
                        'source': tag_source
                    }
                }])
        except:
            #print('Error from perilexcontroller app while writing mode to influxdb:')
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            pass
