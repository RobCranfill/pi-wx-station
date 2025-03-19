"""
    Pi-WX-Station
    Using a pair of Adafruit Feather RP2040 RFM69
    sending side
    w/ BME280 xducer
    and an anemomter
    (c)2025 rob cranfill
"""

# stdlibs
import board
import digitalio
import json
import os
import time

import microcontroller

# adafruit libs
import adafruit_rfm69
from adafruit_bme280 import basic as adafruit_bme280
import neopixel

# my code
import anemom


MAX_RFM_MSG_LEN = 60

# Define some stuff
COLLECTION_TIME = 1 # collect anemometer data for this many seconds at a time
LED_PRE_SEND_COLOR  = 0x00FF00
LED_PRE_SEND_BLINK  = 0.2
LED_POST_SEND_COLOR = 0x0000FF
LED_POST_SEND_BLINK = 0.05

# Don't change this!
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM_CS)
RESET = digitalio.DigitalInOut(board.RFM_RST)


# Read 16-character encryption key.
# TODO: can this fail?
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# send delay in seconds 
# TODO: how should this relate to rcv.LISTEN_TIMEOUT?
SEND_PERIOD = 4
print(f"Sending data every {SEND_PERIOD} seconds")

# Initialize RFM69 radio
rfm69 = adafruit_rfm69.RFM69(board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)

# Just for fun
print(f"  RFM temp: {rfm69.temperature}C")

# The temperature/humidity/pressure sensor, if any.
bme280 = None
try:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    print("THP sensor OK!")
except:
    print("No temp sensor? Continuing....")


neo = neopixel.NeoPixel(board.NEOPIXEL, 1)
neo.fill(0)

anemometer = anemom.anemom(board.D12, debug=False, neopixel=neo)

packet_count = 0
time_start = time.time() # seconds

while True:

    dict = {}

    if bme280 is not None:
        temp = bme280.temperature
        hum  = bme280.humidity
        pres = bme280.pressure

        t_F = (temp * 9 / 5) + 32

        dict['T'] = f"{t_F:2.0f}"
        dict['H'] = f"{hum:2.0f}"
        dict['P'] = f"{pres:2.0f}"
    else:
        dict['T'] = "?"
        dict['H'] = "?"
        dict['P'] = "?"


    neo.fill(LED_PRE_SEND_COLOR)
    time.sleep(LED_POST_SEND_BLINK)
    neo.fill(0)
    wind = anemometer.get_mph(COLLECTION_TIME)

    print(f"  {wind} MPH")
    dict['W'] = f"{wind:2.0f}"


    # Some status data
    uptime = time.time()-time_start
    dict['U'] = uptime
    dict['C'] = packet_count

    # if we don't do this we exceed 60 chars!
    msg = json.dumps(dict).replace(" ", "")
    if len(msg) > MAX_RFM_MSG_LEN:
        print("Data packet too large!")
    else:
        packet_count += 1
        print(f"Sending packet #{packet_count}, {len(msg)} chars: {msg}")
        try:
            neo.fill(LED_POST_SEND_COLOR)
            rfm69.send(msg)
            time.sleep(LED_POST_SEND_BLINK)
        except Exception as e:
            print(f"*** Sending packet failed: {e}")
        finally:
            neo.fill(0)

    print(f" Uptime: {uptime} seconds")
    print(f" CPU: {microcontroller.cpu.temperature:1.0f}C; radio: {rfm69.temperature:1.0f}C")
    time.sleep(SEND_PERIOD)

# we never exit the send loop, above. 

