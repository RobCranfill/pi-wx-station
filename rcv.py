# PiWX receiver code
# 
# Using an Adafruit 16x8 LED "backpack". For now, simplistic code - no object wrapper for display.
# 
# No scrolling - just fading in and out.

# stdlibs
import board
import digitalio
import json
import os
import random
import time
import traceback

# adafruit libs
import neopixel
import adafruit_rfm69
from adafruit_ht16k33 import matrix
import adafruit_vcnl4020

# mine
import LEDMatrix


# Define some stuff
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM_CS)
RESET = digitalio.DigitalInOut(board.RFM_RST)

########################################################

# Read 16-character encryption key.
# TODO: can this fail?
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# TODO: this may be important.
# We send every X seconds, we should probably wait for 2X seconds??
LISTEN_TIMEOUT  = 8
DISPLAY_TIMEOUT = 2


def get_ambient_lux(light_sensor):

    # print(f"Proximity is: {light_sensor.proximity}")

    if light_sensor is None:
        return 1000 # full brightness, sorta

    lux = light_sensor.lux
    # print(f"Ambient is: {lux}")
    return lux


def get_message(rfm):
    '''Return the dictionary of values received by the radio, or None'''

    # Look for a new packet - wait up to given timeout
    print("Listening...")
    packet = rfm.receive(timeout=LISTEN_TIMEOUT)
    print("  Got a packet")

    # If no packet was received after the timeout then None is returned.
    result = None
    if packet is None:
        print("No packet?")
    else:
        pstr = packet.decode('utf8')
        # print(f"Rcvd: '{pstr}'")
        dict = json.loads(pstr)

        # result = dict["T"] + "F " + dict["H"] + "%"
        # print(f"  display: '{result}'")
        result = dict

    return result


def init_hardware():

    # Initialize RFM69 radio
    rfm = adafruit_rfm69.RFM69(board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)

    print(f"  {rfm.bitrate=}")
    print(f"  {rfm.encryption_key=}")
    print(f"  {rfm.frequency_deviation=}")
    print(f"  {rfm.rssi=}")
    print(f"  {rfm.temperature=}")
    print()

    leds = LEDMatrix.LEDMatrix()

    # Initialize VCNL4020
    sensor = None
    try:
        vcln = adafruit_vcnl4020.Adafruit_VCNL4020(board.I2C())
    except:
        print("No light sensor? Continuing....")

    return rfm, leds, vcln


# ##################################################
# TODO: catch keyboard (or other?) exception and blank the display? or display "??"
#
def run():

    radio, led_matrix, sensor = init_hardware()

    while True:

        # adjust display brighness acccording to ambient light
        # First get a value 0 to 1.0
        #
        lux = get_ambient_lux(sensor)

        # 1000 lux, "indoors near the windows on a clear day", gets full LED value.
        # This seems OK, but not very scientific
        # 1000 seems low. 4000?
        max_brightness = lux / 4000

        if max_brightness > 1:
            max_brightness = 1

        # Then scale to 0-15, the display's range.
        max_brightness = int(15 * max_brightness)
        print(f" Brightness: {lux=} -> {max_brightness=}")

        # Get a radio packet.
        #
        data = get_message(radio)
        print(f"{data=}")
        if data == None:
            # TODO: no fade in/out?
            led_matrix.set_brightness(max_brightness)
            led_matrix.show_chars("??")
        else:
            print("Beginning data display...")
            for key in ["T", "W"]:
                val = data[key]
                if len(val) < 2:
                    val = " " + val
                # print(f" {key} = '{val}'")

                # led_matrix.brightness = 0
                print(f" display '{val}'")
                led_matrix.show_chars(val)

                if key == "T":
                    led_matrix.set_mode_indicator(True)
                else:
                    led_matrix.set_mode_indicator(False)

                led_matrix.fade_in(max_brightness)
                time.sleep(DISPLAY_TIMEOUT)
                led_matrix.fade_out(max_brightness)

            print("End data display.\n")


# If we just import this module, this code runs.
# Is this the best way to do this???
#
while True:
    try:
        run()
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Got exception {e}; going around again!")
        traceback.print_exception(e)


print("DONE!")
# while True:
#     pass


def test():
    LEDMatrix.test()
