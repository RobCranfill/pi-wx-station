# PiWX receiver code
# 
# Using an Adafruit 16x8 LED "backpack". For now, simplistic code - no object wrapper for display.
# 


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


# Define some stuff
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM_CS)
RESET = digitalio.DigitalInOut(board.RFM_RST)

# Read 16-character encryption key.
# TODO: can this fail?
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# TODO: this is probably important.
# We send every X seconds, we should probably wait for 2X seconds??
LISTEN_TIMEOUT = 10 


class radio_getter:
    def __init__(self):
        print(f"created {__name__}...")

        # Initialize RFM69 radio
        radio = adafruit_rfm69.RFM69(board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)
        self.radio_ = radio

        print(f"\t{radio.bitrate=}")
        print(f"\t{radio.encryption_key=}")
        print(f"\t{radio.frequency_deviation=}")
        print(f"\t{radio.rssi=}")
        print(f"\t{radio.temperature=}")


    def get_message(self):
        '''Return the string to display, or None'''

        # Look for a new packet - wait up to given timeout
        packet = self.radio_.receive(timeout=LISTEN_TIMEOUT)

        # If no packet was received after the timeout then None is returned.
        result = None
        if packet is None:
            print("No packet?")
        else:
            pstr = packet.decode('utf8')
            print(f"Rcvd: '{pstr}'")

            dict = json.loads(pstr)
            result = dict["T"] + "F " + dict["H"] + "%"
            print(f"  display: '{result}'")

        return result

def fade_to(m, start, end, step, delay):
    b = start
    while b < end:
        m.brightness = b
        time.sleep(delay)
        b += step

def fade_in(m):
    # fade_to(m, 0, 1, 0.01, 0.1)
    b = 0
    while b <= 1:
        m.brightness = b
        time.sleep(0.01)
        b += 0.01
    m.brightness = 1

def fade_out(m):
    # fade_to(m, 1, 0, -0.01, 0.1)
    b = 1
    while b >= 0:
        m.brightness = b
        time.sleep(0.01)
        b -= 0.01
    m.brightness = 0


class main_handler:
    '''Display on an Adafruit 16x8 display backpack - based on adafruit_ht16k33 module.'''
    DISPLAY_HEIGHT = 8
    DISPLAY_WIDTH  = 16

    def __init__(self, getter, i2c, delay, brightness=1.0):
        '''Initialize by giving us the I2C bus object, display string, and column delay.'''

        self.radio_getter_ = getter
        self.matrix_ = matrix.MatrixBackpack16x8(i2c)
        self.delay_ = delay
        self.matrix_.brightness = brightness

        self.matrix_.fill(0)

    def set_brightness(self, b):
        self.matrix_.brightness = b


    # Rotate the list of vertical rasters thru the display, forever.
    # The input data already has the first 2 chars duplicated at the end, for ease of rotation.
    # Uses global displayDelay_ so we can change that after creating the thread.
    #
    def display_loop(self):

        while True:

            # TODO: adjust display brightness according to ambient light.

            msg = self.radio_getter_.get_message()
            print(f" display_loop got '{msg}'")
            if msg is None:
                msg = "?No data?"

            msg += "  "

            vrs = self.make_V_rasters(msg)

            # Initially, render leftmost DISPLAY_WIDTH columns.
            #
            self.display_initial_rasters(vrs[0:self.DISPLAY_WIDTH])
            fade_in(self.matrix_)
            time.sleep(self.delay_)

            # Now just left-shift the existing pixels, and paint the new rightmost column, forever.

            for c in range(self.DISPLAY_WIDTH, len(vrs)):
                self.matrix_.shift(-1, 0)
                for y in range(self.DISPLAY_HEIGHT):
                    self.matrix_[self.DISPLAY_WIDTH-1, y] = vrs[c] & (1<<(self.DISPLAY_HEIGHT-y-1))
                time.sleep(self.delay_)

            fade_out(self.matrix_)

    # For the string, create the big list of bit values (columns), left to right.
    #
    def make_V_rasters(self, string):

        if len(string) == 0: # is there a better way to handle this null-input case?
            string = "(no input given!)"

        # duplicate the first 2 chars onto the end of the data for easier scrolling.
        string += string[0]

        string += string[1] # duplicate the 2nd char onto the end of the data for easier scrolling.
        print(f" Input string now '{string}'")

        vrasters = []
        for char in string:
            # bl is the list of *horizontal* rasters for the char
            bl = byte_list_for_char(char)
            for bitIndex in range(self.DISPLAY_HEIGHT-1,-1,-1):
                thisVR = 0
                for hRasterIndex in range(self.DISPLAY_HEIGHT-1,-1,-1):
                    bitVal = ((1 << bitIndex) & bl[hRasterIndex])
                    if bitVal > 0:
                        thisVR += (1 << (self.DISPLAY_HEIGHT-hRasterIndex-1))
                vrasters.append(thisVR)

        # print(f"vraster (len {len(vrasters)}): {vrasters}")
        return vrasters


    # Display the given raster lines - full display width.
    #
    def display_initial_rasters(self, rasters):
        
        for y in range(self.DISPLAY_HEIGHT):

            # TODO: I was hoping i could do like this, but no.
            # matrix[x] = rasters[x]

            for x in range(len(rasters)):
                self.matrix_[x, y] = rasters[x] & (1<<(self.DISPLAY_HEIGHT-y-1))


# Return a list of the bytes for the given character.
# TODO: catch missing chars?
#
def byte_list_for_char(char):
    bits = led8x8Font.FontData[char]
    return bits


# ##################################################

rg = radio_getter()
mh = main_handler(rg, board.STEMMA_I2C(), 0.0, brightness=0.2)
mh.display_loop()
