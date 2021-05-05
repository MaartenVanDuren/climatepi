import sys
from influxdb import DataFrameClient
import traceback
import datetime
import pandas as pd
import numpy as np


class Database:
    def __init__(self):
        self._database_name = 'sensordata'
        self._db = DataFrameClient('localhost', 8086, 'root', 'root')
        if self._database_name not in self._db.get_list_database():
            self._db.create_database(self._database_name)
            self._db.create_retention_policy(
                name=self._database_name + '_retention_12weeks',
                duration='12w',
                replication='1',
                database=self._database_name,
                default=True)
        self._db.switch_database(self._database_name)

    def get_inside_humidity_features(self, timespan=150):
        try:
            res = self._db.query('SELECT moving_average(derivative(moving_average(mean("value"), 30), 10s), 30) AS "derivative1", '
                                 'moving_average(derivative(derivative(moving_average(mean("value"), 30), 10s), 10s), 30) AS "derivative2" '
                                 'FROM "humidity" WHERE time >= now()-{0}s GROUP BY time(10s)'.format(timespan), database='sensordata')
            res = res['humidity']
            res['time'] = pd.Series((datetime.datetime.strptime(str(value)[:26], '%Y-%m-%dT%H:%M:%S.%f').timestamp()
                                     for value in res.index.values), index=res.index)
            return res
        except:
            #print('Error from ventilatie controller app while querying inside humidity features from influxdb:')
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            return None

    def get_cv_features(self, timespan=150):
        try:
            res = self._db.query('SELECT "value" FROM "ww_warmtevraag", "tapdebiet", "ruimte_temp" WHERE time >= now()-{0}s'.format(timespan), database='cvdata')
            if not res:
                return None
            df = None
            for key in res.keys():
                if df is None:
                    df = res[key].rename(columns={'value': key})
                else:
                    df = pd.merge(df, res[key].rename(columns={'value': key}), left_index=True, right_index=True, how='outer')
            df['time'] = pd.Series((datetime.datetime.strptime(str(value)[:26], '%Y-%m-%dT%H:%M:%S.%f').timestamp()
                                    for value in df.index.values), index=df.index)
            return df
        except:
            # print('Error from ventilatie controller app while querying cv features from influxdb:')
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            return None

    def get_outside_temperature_features(self, timespan=3600):
        try:
            res = self._db.query('SELECT "value" AS "temperature_outside"'
                                 'FROM "temperature_outside" WHERE time >= now()-{0}s'.format(timespan), database='sensordata')
            res = res['temperature_outside']
            res['time'] = pd.Series((datetime.datetime.strptime(str(value)[:26], '%Y-%m-%dT%H:%M:%S.%f').timestamp()
                                     for value in res.index.values), index=res.index)
            return res
        except:
            #print('Error from ventilatie controller app while querying outside temperature features from influxdb:')
            #exc_type, exc_value, exc_traceback = sys.exc_info()
            #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
            return None