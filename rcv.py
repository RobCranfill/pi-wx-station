# PiWX receiver code
# 
# Using an Adafruit 16x8 LED "backpack". For now, simplistic code - no object wrapper for display.
# 
# No scrolling, just fading in and out?

# TODO: send/rcv a packet number, just for fun?


# stdlibs
import board
import digitalio
import json
import os
import random
import time

# adafruit
import neopixel
import adafruit_rfm69
from adafruit_ht16k33 import matrix
import adafruit_vcnl4020

# mine
import led8x8Font

DISPLAY_HEIGHT =  8
DISPLAY_WIDTH  = 16


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
LISTEN_TIMEOUT = 8
DISPLAY_TIMEOUT = 2


def get_ambient_lux(light_sensor):
    # print(f"Proximity is: {light_sensor.proximity}")
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


# def fade_to(m, start, end, step, delay):
#     b = start
#     while b < end:
#         m.brightness = b
#         time.sleep(delay)
#         b += step

FADE_STEP = 0.1
FADE_SLEEP_TIME = 0.05

def fade_in(m, max=1):
    b = 0
    while b <= max:
        m.brightness = b
        time.sleep(FADE_SLEEP_TIME)
        b += FADE_STEP
    m.brightness = max
    time.sleep(FADE_SLEEP_TIME)

def fade_out(m, start=1):
    b = start
    while b >= 0:
        m.brightness = b
        time.sleep(FADE_SLEEP_TIME)
        b -= FADE_STEP
    m.brightness = 0
    time.sleep(FADE_SLEEP_TIME)

# For the string, create the big list of bit values (columns), left to right.
#
def make_V_rasters(string):

    if len(string) == 0: # is there a better way to handle this null-input case?
        string = "(no input given!)"

    vrasters = []
    for char in string:
        # bl is the list of *horizontal* rasters for the char
        bl = byte_list_for_char(char)
        for bitIndex in range(DISPLAY_HEIGHT-1,-1,-1):
            thisVR = 0
            for hRasterIndex in range(DISPLAY_HEIGHT-1,-1,-1):
                bitVal = ((1 << bitIndex) & bl[hRasterIndex])
                if bitVal > 0:
                    thisVR += (1 << (DISPLAY_HEIGHT-hRasterIndex-1))
            vrasters.append(thisVR)

    # print(f"vraster (len {len(vrasters)}): {vrasters}")
    return vrasters


# Display the given raster lines - full display width.
#
def display_rasters(matrix, rasters):
    for y in range(DISPLAY_HEIGHT):
        for x in range(len(rasters)):
            matrix[x, y] = rasters[x] & (1<<(DISPLAY_HEIGHT-y-1))

def blank(matrix):
    for y in range(DISPLAY_HEIGHT):
        for x in range(DISPLAY_WIDTH):
            matrix[x, y] = 0

def set_mode_indicator(matrix, is_temperature):
    """What?"""

    # horizontal line under all digits?
    # for x in range(DISPLAY_WIDTH):
    #     matrix[x, 7] = one_or_zero

    # vertical line to left? that's better
    if is_temperature:
        ys = [0,1,2,3]
    else:
        ys = [4,5,6,7]
    for y in ys:
        matrix[0, y] = 1
    
# Return a list of the bytes for the given character.
# TODO: catch missing chars?
#
def byte_list_for_char(char):
    bits = led8x8Font.FontData[char]
    return bits


# ##################################################
def run():

    # Initialize RFM69 radio
    radio = adafruit_rfm69.RFM69(board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)

    print(f"  {radio.bitrate=}")
    print(f"  {radio.encryption_key=}")
    print(f"  {radio.frequency_deviation=}")
    print(f"  {radio.rssi=}")
    print(f"  {radio.temperature=}")
    print()

    mx = matrix.MatrixBackpack16x8(board.STEMMA_I2C())


    # Initialize VCNL4020
    sensor = None
    try:
        sensor = adafruit_vcnl4020.Adafruit_VCNL4020(board.I2C())
    except:
        print("No light sensor? Continuing....")


    while True:

        # adjust display brighness acccording to ambient light
        lux = get_ambient_lux(sensor)
        # print(f"Adjust to {lux}")

        max_brightness = lux / 1000
        if max_brightness > 1:
            max_brightness = 1
        # print(f"Setting max brightness to {max_brightness}")

        data = get_message(radio)
        print(f"{data=}")
        if data == None:
            mx.brightness = .5
            display_rasters(mx, make_V_rasters("??"))
        else:
            print("Beginning data display...")
            for key in ["T", "W"]:
                val = data[key]
                if len(val) < 2:
                    val = " " + val
                # print(f" {key} = '{val}'")

                mx.brightness = 0
                print(f" display '{val}'")
                display_rasters(mx, make_V_rasters(val))

                if key == "T":
                    set_mode_indicator(mx, True)
                else:
                    set_mode_indicator(mx, False)

                fade_in(mx, max = max_brightness)
                time.sleep(DISPLAY_TIMEOUT)
                fade_out(mx, start = max_brightness)
            print("End data display.\n")


def test():
    """Test stuff - display timing, etc"""
    mx = matrix.MatrixBackpack16x8(board.STEMMA_I2C())
    while True:
        for s in ["64", " 0", "66", "12"]:

            mx.brightness = 0
            display_rasters(mx, make_V_rasters(s))

            fade_in(mx)
            time.sleep(1)
            fade_out(mx)

        blank(mx)

# test()

while True:
    try:
        run()
    except KeyboardInterrupt:
        break
    except:
        print("Got exception; going around again!")

print("DONE!")
# while True:
#     pass
