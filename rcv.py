# PiWX receiver code
# 
# Using an Adafruit 16x8 LED "backpack". For now, simplistic code - no object wrapper for display.
# 
# No scrolling, just fading in and out?

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


def get_message(rfm):
    '''Return the dictionary of values, or None'''

    # Look for a new packet - wait up to given timeout
    packet = rfm.receive(timeout=LISTEN_TIMEOUT)

    # If no packet was received after the timeout then None is returned.
    result = None
    if packet is None:
        print("No packet?")
    else:
        pstr = packet.decode('utf8')
        print(f"Rcvd: '{pstr}'")
        dict = json.loads(pstr)

        # result = dict["T"] + "F " + dict["H"] + "%"
        # print(f"  display: '{result}'")
        result = dict

    return result


def fade_to(m, start, end, step, delay):
    b = start
    while b < end:
        m.brightness = b
        time.sleep(delay)
        b += step

def fade_in(m, max=1):
    # fade_to(m, 0, 1, 0.01, 0.1)
    b = 0
    while b <= max:
        m.brightness = b
        time.sleep(0.01)
        b += 0.01
    m.brightness = max

def fade_out(m, start=1):
    # fade_to(m, 1, 0, -0.01, 0.1)
    b = start
    while b >= 0:
        m.brightness = b
        time.sleep(0.01)
        b -= 0.01
    m.brightness = 0


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
def display_initial_rasters(matrix, rasters):
    for y in range(DISPLAY_HEIGHT):
        for x in range(len(rasters)):
            matrix[x, y] = rasters[x] & (1<<(DISPLAY_HEIGHT-y-1))

def blank(matrix):
    for y in range(DISPLAY_HEIGHT):
        for x in range(DISPLAY_WIDTH):
            matrix[x, y] = 0

def set_wind_indicator(matrix, one_or_zero):
    """What?"""

    # horizontal line under all digits?
    # for x in range(DISPLAY_WIDTH):
    #     matrix[x, 7] = one_or_zero

    # vertical line to left?
    if one_or_zero == 0:
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

    while True:

        # TODO: calculate this from light sensor
        max_brightness = 0.5

        data = get_message(radio)
        print(f"{data=}")
        if data == None:

            mx.brightness = .5
            display_initial_rasters(mx, make_V_rasters("??"))

        else:
            for k in ["T", "W"]:
                v = data[k]
                if len(v) < 2:
                    v = " " + v
                print(f" {k} = '{v}'")
                
                mx.brightness = 0
                display_initial_rasters(mx, make_V_rasters(v))

                if k == "T":
                    set_wind_indicator(mx, 0)
                else:
                    set_wind_indicator(mx, 1)

                fade_in(mx, max = max_brightness)
                time.sleep(1)
                fade_out(mx, start = max_brightness)

def test():
    mx = matrix.MatrixBackpack16x8(board.STEMMA_I2C())
    while True:
        for s in ["AB", "cd", "Ef", "gH"]:
            mx.brightness = 0
            display_initial_rasters(mx, make_V_rasters(s))
            fade_in(mx)
            time.sleep(1)
            fade_out(mx)
        blank(mx)

run()
# test()

print("DONE!")
while True:
    pass
