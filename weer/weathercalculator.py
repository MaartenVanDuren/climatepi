import math


class WeatherCalculator:
    @staticmethod
    def inside_relative_humidity_from_conditions(outside_humidity, outside_temperature, desired_temperature):
        absolute_moisture = outside_humidity * 0.42 * math.exp(outside_temperature * 10 * 0.006235398) / 10
        return absolute_moisture * 10 / (0.42 * math.exp(desired_temperature * 10 * 0.006235398))
