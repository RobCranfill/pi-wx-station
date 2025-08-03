"""
    Pi-WX-Station
    Using a pair of Adafruit Feather RP2040 RFM69
    This is the receiver side
    using an Adafruit 16x8 LED "backpack". 
    (c)2025 rob cranfill
    See https://github.com/RobCranfill/pi-wx-station
"""

# stdlibs
import board
import digitalio
import json
import os
import random
import time
import traceback

# adafruit libs
import adafruit_rfm69
from adafruit_ht16k33 import matrix
import adafruit_vcnl4020
import neopixel

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


def get_message(rfm):
    '''Return the dictionary of values received by the radio, or None'''

    # Look for a new packet - wait up to given timeout
    print("Listening...")
    packet = rfm.receive(timeout=LISTEN_TIMEOUT)
    print(" Got a packet")

    # If no packet was received after the timeout then None is returned.
    result = None
    if packet is None:
        print("No packet?")
    else:
        pstr = packet.decode('utf8')
        # print(f"Rcvd: '{pstr}'")
        data_dict = json.loads(pstr)

        # result = dict["T"] + "F " + data_dict["H"] + "%"
        # print(f"  display: '{result}'")
        result = data_dict

    return result


def init_hardware():

    # Initialize RFM69 radio
    rfm = adafruit_rfm69.RFM69(board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)

    # For fun
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
        vcln.lux_enabled = True
        vcln.proximity_enabled = False
    except:
        print("No light sensor? Continuing....")

    return rfm, leds, vcln


def get_brightness_value(light_sensor):
    """Calculate a value 0-15 for display brighness acccording to ambient light."""

    # TODO: Not sure what max possible lux is.
    #
    if light_sensor is None:
        lux = 1000 # full brightness, sorta
    else:
        lux = light_sensor.lux

    # 1000 lux, "indoors near the windows on a clear day", gets full LED value.
    # This seems OK, but not very scientific
    # 1000 seems low. 4000?
    scaled = lux / 4000
    if scaled > 1:
        scaled = 1

    # Then scale to 0-15, the display's range.
    scaled_int = int(15 * scaled)
    # print(f" Brightness: {lux=} -> {scaled_int=}")
    return scaled_int

def count_to_mph(count):
    """Return integer MPH as a string"""

    mph = int(count / 15)
    print(f" count_to_mph: {count=} -> {mph=}")
    return str(mph)


# ##################################################
# TODO: catch keyboard (or other?) exception and blank the display? or display "??"
#
def run():

    radio, led_matrix, sensor = init_hardware()

    fade_in_and_out = False

    while True:

        max_brightness = get_brightness_value(sensor)

        # Get a radio packet.
        #
        data = get_message(radio)
        print(f" {data=}")
        if data == None:
            # TODO: no fade in/out?
            led_matrix.set_brightness(max_brightness)
            led_matrix.show_chars("??")
        else:
            print(f"Beginning data display, {max_brightness=}...")
            for key in ["T", "C"]:
                display_val = data[key]

                # print(f" {key} = '{display_val}'")

                # led_matrix.brightness = 0
                print(f" display '{display_val}'")

                if key == "C":
                    display_val = count_to_mph(int(display_val))

                if len(display_val) < 2:
                    display_val = " " + display_val
                led_matrix.show_chars(display_val)

                # Must come after char display or it gets stepped on.
                # FIXME?
                if key == "T":
                    led_matrix.set_mode_indicator(True)
                else:
                    led_matrix.set_mode_indicator(False)

                if fade_in_and_out:
                    led_matrix.fade_in(max_brightness)
                else:
                    led_matrix.set_brightness(max_brightness)

                time.sleep(DISPLAY_TIMEOUT)
                
                if fade_in_and_out:
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
