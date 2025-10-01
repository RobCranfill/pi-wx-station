"""Class to support different non-windspeed sensors.

This will, so far, either be an Adafruit BME280 temperature/pressure/humidity sensor,
or a (much cheaper) Adafruit PCT2075 temperature-only sensor.
"""

import board
import math
import traceback


# TODO: how to support one but not the other? dunno.
import adafruit_bme280
import adafruit_pct2075


class Sensor():

    def __init__(self):
        self._has_temperature = False
        self._has_pressure = False
        self._has_humidity = False

        self._is_bme280 = False
        self._is_pct2075 = False
        
        i2c = board.I2C()  # uses board.SCL and board.SDA

        # The temperature/humidity/pressure sensor, if any.
        sensor = None
        try:
            sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
            print("BME280: temperature/pressure/humidity sensor OK!")
            self._is_bme280 = True
            self._has_temperature = True
            self._has_pressure = True
            self._has_humidity = True
        except:
            print("No BME280 sensor? Continuing....")

        if sensor is None:
            try:
                sensor = adafruit_pct2075.PCT2075(i2c)
                print("PCT2075: temperature sensor OK!")
                self._is_pct2075 = True
                self._has_temperature = True
            except Exception as e:
                traceback.print_exception(e)
                print("No PCT2075 sensor? Continuing....")

        # This means this could be None if no sensor attached. Makes sense. Or. :-)
        self._sensor = sensor

        if sensor is None:
            self._is_ok = False
        else:
            self._is_ok = True


    def is_ok(self):
        """Are we initted OK?"""
        return self._is_ok

    def has_temperature(self):
        """Does this sensor sense temp?"""
        return self._has_temperature

    def has_pressure(self):
        """Does this sensor sense pressure?"""
        return self._has_pressure

    def has_humidity(self):
        """Does this sensor sense humidity?"""
        return self._has_humidity

    def temperature(self):
        if not self._has_temperature:
            print("Sensor has no temperature???")
            return math.NaN # FIXME
        return self._sensor.temperature

    def pressure(self):
        if not self.has_pressure:
            print("Sensor has no pressure???")
            return None # FIXME
        return self._sensor.pressure

    def humidity(self):
        if not self._has_humidity:
            print("Sensor has no humidity???")
            return None # FIXME
        return self._sensor.humidity

