"""
    Pi-WX-Station
    Using a pair of Adafruit Feather RP2040 RFM69
    sending side
    w/ BME280 xducer
    and an anemomter
    (c)2025 rob cranfill
    see https://github.com/RobCranfill/pi-wx-station
"""

# stdlibs
import board
import digitalio
import json
import os
import time

import microcontroller
import watchdog
from digitalio import DigitalInOut, Pull

# adafruit libs
import adafruit_rfm69
from adafruit_bme280 import basic as adafruit_bme280
import neopixel

# my code
import anemom


MAX_RFM_MSG_LEN = 60

# Define some stuff
COLLECTION_TIME = 1 # collect anemometer data for this many seconds at a time
LED_PRE_SEND_COLOR  = 0x00_FF_00
LED_PRE_SEND_BLINK  = 0.2
LED_POST_SEND_COLOR = 0x00_00_FF
LED_POST_SEND_BLINK = 0.05

# Don't change this!
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM_CS)
RESET = digitalio.DigitalInOut(board.RFM_RST)


# Read 16-character encryption key.
# TODO: can this fail?
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")


def setup_watchdog():

    print("Hold BUTTON to disable WDT")
    time.sleep(2)

    # configure onboard button as a pulled up input
    button = DigitalInOut(board.BUTTON)
    button.switch_to_input(Pull.UP)

    wdt = microcontroller.watchdog

    # Disable WDT by pressed onboard button at start up.
    if button.value:  # if the button is NOT pressed then...
        wdt.timeout = 8  # max time for RP2040
        wdt.mode = watchdog.WatchDogMode.RESET  # RAISE or RESET
        print("WatchDogMode enabled!\n")
    else:  # if the button is pressed then...
        print("WatchDogMode disabled\n")
        wdt = None

    return wdt


def show_rfm_info(rfm):
    # Just for fun
    print("-------------- RFM Radio info --------------")
    print(f"temperature: {rfm.temperature}C")
    print(f"{rfm.ack_delay=}")
    print(f"{rfm.__dict__=}")    
    print("--------------------------------------------")


# wdt = setup_watchdog()
wdt = None
print("\n****WATCHDOG MODE OVERRIDDEN****\n")

# send delay in seconds 
# TODO: how should this relate to rcv.LISTEN_TIMEOUT?
SEND_PERIOD = 4
print(f"Sending data every {SEND_PERIOD} seconds")

# Initialize RFM69 radio
rfm69 = adafruit_rfm69.RFM69(board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)

show_rfm_info(rfm69)


# The temperature/humidity/pressure sensor, if any.
bme280 = None
try:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    print("Temperature/pressure/humidity sensor OK!")
except:
    print("No temp sensor? Continuing....")


neo = neopixel.NeoPixel(board.NEOPIXEL, 1)
neo.fill(0)


# Our anemometer interface class.
anemometer = anemom.anemom(board.D12, debug=False, neopixel=neo)


packet_count = 0
time_start = time.time() # seconds

while True:

    if wdt is not None:
        wdt.feed()  # feed the watchdog timer so it doesn't timeout

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

    # if we don't do this we exceed 60 chars!
    msg_to_send = json.dumps(dict).replace(" ", "")


    # FIXME
    # augmented packet can be too large:
        #   0.0 MPH
        # Data packet too large!
        #  Uptime: 1033139 seconds
        #  CPU: 23C; radio: 19C


    # Augment with some status data?
    # TODO: also send CPU temperature? (that is, device temp)

    uptime = time.time() - time_start
    dict['U'] = uptime

    # packet count is kinda redundant w/ uptime, so removed.
    # dict['C'] = packet_count

    msg_augmented = json.dumps(dict).replace(" ", "")

    if len(msg_augmented) <= MAX_RFM_MSG_LEN:
        msg_to_send = msg_augmented
    else:
        print(f"Full data packet too large! {len(msg_augmented)=}")
        print(f"{msg_augmented}")

    packet_count += 1
    print(f"Sending packet #{packet_count}, {len(msg_to_send)} chars: {msg_to_send}")
    try:
        neo.fill(LED_POST_SEND_COLOR)
        rfm69.send(msg_to_send)
        time.sleep(LED_POST_SEND_BLINK)
    except Exception as e:
        print(f"*** Sending packet failed: {e}")
    finally:
        neo.fill(0)

    print(f" Uptime: {uptime} seconds")
    print(f" CPU: {microcontroller.cpu.temperature:1.0f}C; radio: {rfm69.temperature:1.0f}C")
    time.sleep(SEND_PERIOD)

# we never exit the send loop, above.
