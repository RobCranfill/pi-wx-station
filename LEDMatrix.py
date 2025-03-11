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


# TODO: add methods to set/change these?
FADE_STEP = 0.1
FADE_SLEEP_TIME = 0.05


class LEDMatrix:

    def __init__(self):
        self._matrix = matrix.MatrixBackpack16x8(board.I2C())

    # def fade_to(self, start, end, step, delay):
    #     b = start
    #     while b < end:
    #         self._matrix.brightness = b
    #         time.sleep(delay)
    #         b += step

    def fade_in(self, max=1):
        """Increase display brightness from zero up to max."""
        b = 0
        while b <= max:
            self._matrix.brightness = b
            # print(f"{b=}")
            time.sleep(FADE_SLEEP_TIME)
            b += FADE_STEP
        self._matrix.brightness = max
        time.sleep(FADE_SLEEP_TIME)

    def fade_out(self, start=1):
        """Reduce display brightness from current value down to zero."""
        b = start
        while b >= 0:
            self._matrix.brightness = b
            # print(f"{b=}")
            time.sleep(FADE_SLEEP_TIME)
            b -= FADE_STEP
        self._matrix.brightness = 0
        time.sleep(FADE_SLEEP_TIME)

    def set_brightness(self, b):
        self._matrix.brightness = b

    def blank(self):
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
            print("HEY!")
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


# ##################################################

def test():
    """Test stuff - display timing, etc"""

    lm = LEDMatrix()

    while True:
        for s in [("88", True), (" 9", False), ("89", True), ("12", False)]:

            lm.set_brightness(0)
            time.sleep(.5)

            lm.show_chars(s[0])
            lm.set_mode_indicator(s[1])

            lm.fade_in()
            time.sleep(2)
            lm.fade_out()
            lm.blank()
