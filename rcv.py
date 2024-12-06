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

LISTEN_TIMEOUT = 1 # seconds


class radio_getter:
    def __init__(self):
        print(f"created {__name__}...")

        # Initialize RFM69 radio
        radio = adafruit_rfm69.RFM69(board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)

        print(f"\t{radio.bitrate=}")
        print(f"\t{radio.encryption_key=}")
        print(f"\t{radio.frequency_deviation=}")
        print(f"\t{radio.rssi=}")
        print(f"\t{radio.temperature=}")

        self.radio_ = radio

    def get_message(self):
        '''Or None'''
        r = random.randrange(0, 100)
        msg = None
        if r > 75:
            msg = f"Hello {r}!"
        return msg


class station_display:

    def __init__(self, radio, display):

        print(f"init {__name__}")


class main_handler:
    '''Display for Adafruit 16x8 display backpack based on adafruit_ht16k33 module.'''
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

        msg = self.radio_getter_.get_message()
        print(f"GOT {msg}!")
        # TODO unpack dict and make string
        vrs = self.make_V_rasters(msg)


        # Initially, render leftmost DISPLAY_WIDTH columns.
        #
        self.display_initial_rasters(vrs[0:self.DISPLAY_WIDTH])
        time.sleep(self.delay_)

        # Now just left-shift the existing pixels, and paint the new rightmost column, forever.
        c = self.DISPLAY_WIDTH
        while True:
            c += 1
            if c >= len(vrs):
                c = self.DISPLAY_WIDTH

            self.matrix_.shift(-1, 0)

            for y in range(self.DISPLAY_HEIGHT):
                self.matrix_[self.DISPLAY_WIDTH-1, y] = vrs[c] & (1<<(self.DISPLAY_HEIGHT-y-1))

            time.sleep(self.delay_)


    def show_once(self, str):
        print(f"show_once: '{str}'")
        vr = self.make_V_rasters(str)
        self.display_forever(vr, 0, True) # FIXME: delay


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
# ##################################################


rg = radio_getter()
mh = main_handler(rg, board.STEMMA_I2C(), 0.0, brightness=0.2)
mh.display_loop()


# sd = station_display(rfm69, d)



# while True:

#     # Look for a new packet - wait up to given timeout
#     packet = rfm69.receive(timeout=LISTEN_TIMEOUT)

#     # If no packet was received after the timeout then None is returned.
#     if packet is None:
#         print("No packet")

#         # lmd.display_single_char("?")

#     else:
#         pstr = packet.decode('utf8')
#         print(f"Rcvd: '{pstr}'")

#         dict = json.loads(pstr)
#         display_message = dict["T"] + "F "
#         print(f"  display: '{display_message}'")

#         # lmd.display_scrolling_text(display_message, 0.01, 10)

