"""
    Pi-WX-Station
    Using a pair of Adafruit Feather RP2040 RFM69
    w/ BME280 xducer and an anemomter.

    Sending side.

    (c)2025 rob cranfill
    see https://github.com/RobCranfill/pi-wx-station
"""

# region imports

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
# from adafruit_bme280 import basic as adafruit_bme280
import neopixel

# my code
import anemom

# endregion imports

# region defines
MAX_RFM_MSG_LEN = 60

# Define some stuff
COLLECTION_TIME = 1 # collect anemometer data for this many seconds at a time
LED_PRE_SEND_COLOR  = 0x00_FF_00
LED_PRE_SEND_BLINK  = 0.5
LED_POST_SEND_COLOR = 0x00_00_FF
LED_DATA_SEND_COLOR = 0xFF_00_00
LED_POST_SEND_BLINK = 0.5
LED_COLOR_OFF = 0x00_00_00

# Don't change this!
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM_CS)
RESET = digitalio.DigitalInOut(board.RFM_RST)

# just test the sensors and data packing?
ACTUALLY_SEND = True

# Read 16-character encryption key.
# TODO: can this fail?
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# endregion defines

# region functions
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
    """ Just for fun """
    print("-------------- RFM Radio info --------------")
    print(f"temperature: {rfm.temperature}C")
    print(f"{rfm.ack_delay=}")
    # print(f"{rfm.__dict__=}")
    print("--------------------------------------------")

# endregion functions


# region main

# A watchdog timer doesn't seem to be as useful as it sounded. :-/
# wdt = setup_watchdog()
wdt = None
print("\n****WATCHDOG MODE OVERRIDDEN****\n")

# send delay in seconds 
# TODO: how should this relate to rcv.LISTEN_TIMEOUT?
SEND_PERIOD = 4
print(f"Sending data every {SEND_PERIOD} seconds")

# Initialize RFM69 radio

radio = None # why is the board getting corrupted so often?
if ACTUALLY_SEND:
    radio = adafruit_rfm69.RFM69(board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)
    show_rfm_info(radio)

if radio is None:
    print("\n\n****************** NOT USING RADIO!!!!! \n\n")


# # The temperature/humidity/pressure sensor, if any.
# bme280 = None
# try:
#     i2c = board.I2C()  # uses board.SCL and board.SDA
#     bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
#     print("Temperature/pressure/humidity sensor OK!")
# except:
#     print("No temp sensor? Continuing....")

import sensors
sensor = sensors.Sensor()
if sensor is None:
    print("**** No p/t/h sensor???")


neo = neopixel.NeoPixel(board.NEOPIXEL, 1)
neo.fill(0)


# Our anemometer interface class.
anemometer = anemom.Anemom(board.D12, LED_DATA_SEND_COLOR, debug=False, neopixel=neo)


packet_count = 0
time_start = time.time() # seconds

while True:

    if wdt is not None:
        wdt.feed()  # feed the watchdog timer so it doesn't timeout

    data_dict = {}

    if sensor.is_ok():

        temp = sensor.temperature()
        t_F = (temp * 9 / 5) + 32
        data_dict['T'] = f"{t_F:2.0f}"

        if sensor.has_humidity():
            hum  = sensor.humidity()
            data_dict['H'] = f"{hum:2.0f}"
        else:
            data_dict['H'] = "?H"

        if sensor.has_pressure():
            pres = sensor.pressure()
            data_dict['P'] = f"{pres:2.0f}"
        else:
            data_dict['P'] = "?P"

    else:
        data_dict['T'] = "T?"
        data_dict['H'] = "H?"
        data_dict['P'] = "P?"

    # Before sending the packet, blink the LED.
    neo.fill(LED_PRE_SEND_COLOR)
    time.sleep(LED_POST_SEND_BLINK)
    neo.fill(LED_COLOR_OFF)

    # Now just get the raw count from the anemomoter;
    # calculate MPH on this side.
    #
    # wind = anemometer.get_mph(COLLECTION_TIME)
    anemom_count = anemometer.get_raw(COLLECTION_TIME)

    # Send the raw anemometer count, to be intrepreted by the rcv side.
    print(f"  {anemom_count=}")
    data_dict['C'] = f"{anemom_count:2.0f}"

    # if we don't do this we exceed 60 chars!
    msg_to_send = json.dumps(data_dict).replace(" ", "")


    # FIXME
    # augmented packet can be too large:
        #   0.0 MPH
        # Data packet too large!
        #  Uptime: 1033139 seconds
        #  CPU: 23C; radio: 19C


    # Augment with some status data?
    # TODO: also send CPU temperature? (that is, device temp)

    uptime = time.time() - time_start
    data_dict['U'] = uptime

    # packet count is kinda redundant w/ uptime, so removed.
    # data_dict['C'] = packet_count

    # remove spaces
    msg_augmented = json.dumps(data_dict).replace(" ", "")

    if len(msg_augmented) <= MAX_RFM_MSG_LEN:
        msg_to_send = msg_augmented
    else:
        print(f"Full data packet too large! {len(msg_augmented)=}")
        print(f"{msg_augmented}")

    packet_count += 1
    print(f"({ACTUALLY_SEND=}) Sending packet #{packet_count}, {len(msg_to_send)} chars: {msg_to_send}")
    try:

        neo.fill(LED_POST_SEND_COLOR)
        if radio is not None:
            radio.send(msg_to_send)
        time.sleep(LED_POST_SEND_BLINK)
    
    except AssertionError:
        print(f"*** Sending packet failed: {AssertionError}")
    finally:
        neo.fill(LED_COLOR_OFF)

    print(f" Uptime: {uptime} seconds")
    if radio is not None:
        print(f" CPU: {microcontroller.cpu.temperature:1.0f}C; radio: {radio.temperature:1.0f}C")
    time.sleep(SEND_PERIOD)

    # we never exit the send loop.

# endregion main

