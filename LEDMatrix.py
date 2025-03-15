"""Module for Adafruit display"""

# stdlibs
import board
import digitalio
import time

# adafruit
from adafruit_ht16k33 import matrix

# mine
import led8x8Font

DISPLAY_HEIGHT =  8
DISPLAY_WIDTH  = 16


FADE_STEPS = [0.0, .05, 0.1, .15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


class LEDMatrix:
    """Implements a quantized brightness, 0-15, with 0 being lowest - but not off!"""
    def __init__(self, delay=0.2):

        # TODO: catch exception?
        self._matrix = matrix.MatrixBackpack16x8(board.I2C())

        self._fade_delay = delay

        self.blank()


    def set_fade_delay(self, delay):
        self._fade_delay = delay


    # def fade_to(self, start, end, step, delay):
    #     b = start
    #     while b < end:
    #         self._matrix.brightness = b
    #         time.sleep(delay)
    #         b += step


    def fade_in(self, max):
        """Increase display brightness *from zero* up to indicated max. Does not pause at max brightness."""
        for b in range(max+1):
            self.set_brightness(b)
            # print(f"{b=}")
            time.sleep(self._fade_delay)
        time.sleep(self._fade_delay)

    def fade_out(self, current):
        """Decrease display brightness from indicated value down to 'zero' (which is not 'off'). Does not pause at 0 brightness."""
        for b in range(current, -1, -1):
            self.set_brightness(b)
            # print(f"{b=}")
            time.sleep(self._fade_delay)
        time.sleep(self._fade_delay)

    def set_brightness(self, i):
        """Int value from 0 to 15"""
        if i < 0 or i > 15:
            print(f"Bad brightness value {i}")
            return
        self._matrix.brightness = i / 16        

    def blank(self):
        """This erases the image data."""
        self._matrix.fill(0)

    def set_mode_indicator(self, is_temperature):
        """Indicate whether we are showing temp or wind. How?"""

        # horizontal line under all digits?
        # for x in range(DISPLAY_WIDTH):
        #     matrix[x, 7] = one_or_zero

        # vertical line to left? that's better
        if is_temperature:
            ys = [0,1,2,3]
        else:
            ys = [4,5,6,7]

        for y in ys:
            self._matrix[0, y] = 1


    def show_chars(self, two_chars):
        """"Display 2 characters on the LED matrix."""

        if len(two_chars) != 2:
            print("HEY DUMMY!")
            return

        # For the given string, create the big list of bit values (columns), left to right.
        #
        rasters = []
        for char in two_chars:

            # bl is the list of *horizontal* rasters for the char.
            # Can this be out of range (missing charater?)?
            bl = led8x8Font.FontData[char]

            for bitIndex in range(DISPLAY_HEIGHT-1,-1,-1):
                thisVR = 0
                for hRasterIndex in range(DISPLAY_HEIGHT-1,-1,-1):
                    bitVal = ((1 << bitIndex) & bl[hRasterIndex])
                    if bitVal > 0:
                        thisVR += (1 << (DISPLAY_HEIGHT-hRasterIndex-1))
                rasters.append(thisVR)
        # print(f"vraster (len {len(vrasters)}): {vrasters}")

        for y in range(DISPLAY_HEIGHT):
            for x in range(len(rasters)):
                self._matrix[x, y] = rasters[x] & (1<<(DISPLAY_HEIGHT-y-1))



# this is how the matrix library calculates brightness.
def brightness(brightness: float) -> None:
    if not 0.0 <= brightness <= 1.0:
        raise ValueError(
            "Brightness must be a decimal number in the range: 0.0-1.0"
        )

    # self._brightness = brightness
    xbright = round(15 * brightness)
    xbright = xbright & 0x0F
    print(f"{brightness} -> {xbright=} = {hex(xbright)}")

    # for index, _ in enumerate(self.i2c_device):
    #     self._write_cmd(_HT16K33_CMD_BRIGHTNESS | xbright, index)



# ##################################################
import random
def test():
    """Test stuff - display timing, etc"""

    lm = LEDMatrix(delay=0.05)

    # kinda like real life:
    while True:
        for s in [("88", True), (" 9", False), ("89", True), ("12", False)]:

            # calculate a brightness 0-15
            max = random.randint(0, 15)
            print(f"setting max brightness to {max}...")

            # lm.blank()
            lm.set_brightness(0)

            lm.show_chars(s[0])
            lm.set_mode_indicator(s[1])

            lm.fade_in(max)
            time.sleep(2)

            # fade out doesn't fade to black!
            lm.fade_out(max)
            lm.blank()
            time.sleep(1)

