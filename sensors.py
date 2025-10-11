"""Class to support different temperature/pressure/humidity sensors.

This will, so far, either be an Adafruit BME280 temperature/pressure/humidity sensor,
or a (slightly cheaper) Adafruit PCT2075 temperature-only sensor.
"""

import board
import math
import traceback


# Use the 'advanced' library - we have lots of RAM - altho do we *need* "advanced"??
import adafruit_bme280.advanced as adafruit_bme280
import adafruit_pct2075


class Sensor():
    """This will try to connnect to either of the two kinds of sensors I have."""
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
            print("BME280 temperature/pressure/humidity sensor OK!")
            self._is_bme280 = True
            self._has_temperature = True
            self._has_pressure = True
            self._has_humidity = True
        except Exception as e:
            print("\n**** No BME280 sensor?")
            traceback.print_exception(e)
            print("  Continuing....")
            sensor = None

        if sensor is None:
            try:
                sensor = adafruit_pct2075.PCT2075(i2c)
                print("PCT2075 temperature sensor OK!")
                self._is_pct2075 = True
                self._has_temperature = True
            except Exception as e:
                print("\n**** No PCT2075 sensor?")
                traceback.print_exception(e)
                print("  Continuing....")

        # This means this could be None if no sensor attached. Makes sense. Or. :-)
        self._sensor = sensor

        if sensor is None:
            self._is_ok = False
            print("\n**** No temperature sensor!\n")
        else:
            self._is_ok = True


    def is_ok(self):
        """Are we initted OK? If this is False, all other values are bogus."""
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

