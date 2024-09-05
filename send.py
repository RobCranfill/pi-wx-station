"""
Pi-WX-Station
Using a pair of Adafruit Feather RP2040 RFM69
sending side
 w/ BME280 xducer
(c)2024 rob cranfill
"""

# stdlibs
import board
import digitalio
import json
import os
import time

# adafruit libs
import adafruit_rfm69
from adafruit_bme280 import basic as adafruit_bme280


# Define some stuff
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM_CS)
RESET = digitalio.DigitalInOut(board.RFM_RST)

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")



# Initialise RFM69 radio
rfm69 = adafruit_rfm69.RFM69(
    board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)

print(f"RFM temp: {rfm69.temperature}C")

# init the sensor
i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

dict = {}

while True:

    temp = bme280.temperature
    hum  = bme280.humidity
    pres = bme280.pressure

    t_F = (temp * 9 / 5) + 32
    dict['T'] = f"{t_F:2.0f}"
    dict['H'] = f"{hum:2.0f}"
    dict['P'] = f"{pres:2.0f}"

    msg = json.dumps(dict)

    print(f"sending: {len(msg)} chars: {msg}")
    try:
        rfm69.send(msg)
    except:
        print("failed!")

    time.sleep(1)

print("done!")

