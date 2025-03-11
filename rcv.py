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

    leds = LEDMatrix()

    # Initialize VCNL4020
    sensor = None
    try:
        vcln = adafruit_vcnl4020.Adafruit_VCNL4020(board.I2C())
    except:
        print("No light sensor? Continuing....")

    return rfm, leds, vcln


# ##################################################
def run():

    radio, led_matrix, sensor = init_hardware()

    while True:

        # adjust display brighness acccording to ambient light
        lux = get_ambient_lux(sensor)
        print(f"Adjust to {lux}")

        # 1000 lux, "indoors near the windows on a clear day", gets full LED value.
        # This seems OK, but not very scientific
        max_brightness = lux / 1000
        if max_brightness > 1:
            max_brightness = 1
        # print(f"Setting max brightness to {max_brightness}")

        data = get_message(radio)
        print(f"{data=}")
        if data == None:
            led_matrix.set_brightness(.5)
            led_matrix.show_chars("??")
        else:
            print("Beginning data display...")
            for key in ["T", "W"]:
                val = data[key]
                if len(val) < 2:
                    val = " " + val
                # print(f" {key} = '{val}'")

                led_matrix.brightness = 0
                print(f" display '{val}'")
                led_matrix.show_chars(val)

                if key == "T":
                    led_matrix.set_mode_indicator(True)
                else:
                    led_matrix.set_mode_indicator(False)

                led_matrix.fade_in(max = max_brightness)
                time.sleep(DISPLAY_TIMEOUT)
                led_matrix.fade_out(start = max_brightness)

            print("End data display.\n")


def test():
    """Test stuff - display timing, etc"""
    mx = matrix.MatrixBackpack16x8(board.STEMMA_I2C())
    while True:
        for s in ["64", " 0", "66", "12"]:

            mx.brightness = 0
            
            mx.show_chars(s)

            mx.fade_in(mx)
            time.sleep(1)
            mx.fade_out(mx)

        mx.blank(mx)


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
