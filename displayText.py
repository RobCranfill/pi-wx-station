# New version for CircuitPython on a microcontroller - (c)2024
# Now packaged as a class, with single-character mode

# based on
# displayText.py
# (c)2020 robcranfill@gmail.com
#

import board
import time
from adafruit_ht16k33.matrix import Matrix8x8

import led8x8Font


class LEDMatrixDisplay:
    
    def __init__(self) -> None:
        
        pass


    # For the string, create the big list of bit values (columns), left to right.
    #
    def makeVRasters(self, string):

        if len(string) == 0: # is there a better way to handle this null-input case? needed?
            string = " "
        else:
            # duplicate the first char onto the end of the data for easier scrolling. TODO: needed?
            string += string[0]

        bits = []
        for char in string:

            # bl is the list of *horizontal* rasters for the char
            bl = self.byteListForChar(char)
            for bitIndex in range(7,-1,-1):
                thisVR = 0
                for hRasterIndex in range(7,-1,-1):
                    bitVal = ((1 << bitIndex) & bl[hRasterIndex])
                    if bitVal > 0:
                        thisVR += (1 << (7-hRasterIndex))
                bits.append(thisVR)

        # print(f"vraster (len {len(bits)}): {bits}")
        return bits


    # Rotate the list of vertical rasters thru the display, forever.
    # The input data already has the first char duplicated at the end, for ease of rotation.
    #
    def display_forever(self, matrix, vrs, delay):

        # display all 8 of the first char; after that, 
        # rotate old ones and repaint only the new, rightmost, raster.

        self.display_raster(matrix, vrs[0:8])

        while True:

            # this is dependent on the display rotation. FIXME
            matrix.shift(0, -1)

            # get the proper 8x8 bits to display
            for i in range(len(vrs)-8):
                self.display_raster(matrix, vrs[i:i+8])
                time.sleep(delay)


    # Shift the existing pixels left 1, then paint the new rightmost raster.
    # This is slightly funky because I have my 8x8 matrix mounted sideways - YMMV!
    #
    def display_raster(self, matrix, rasters):

        matrix.shift(0, -1)
        i = 7 # the rightmost scanline
        for j in range(8):
            matrix[j, i] = rasters[i] & (1<<j)


    # Return a list of the bytes for the given character.
    # TODO: catch missing chars?
    #
    def byteListForChar(self, char):
        bits = led8x8Font.FontData[char]
        return bits


    # The money method.
    # This method never returns.
    # NOT SURE HOW DO MAKE THIS UPDATE-ABLE.
    # FIXME TODO
    #
    def display_scrolling_text(self, string, delay):

        i2c = board.STEMMA_I2C()
        matrix = Matrix8x8(i2c)
        matrix.brightness = 1

        matrix.fill(1)
        time.sleep(1)
        matrix.fill(0)
        time.sleep(1)

        rasters = self.makeVRasters(string)
        print(f"vertical rasters: {rasters}")

        self.display_forever(matrix, rasters, delay)


    # Display a single character and return.
    #
    def display_single_char(self, char):

        i2c = board.STEMMA_I2C()
        matrix = Matrix8x8(i2c)
        matrix.brightness = 1

        rasters = self.makeVRasters(char)
        # print(f"vertical rasters: {rasters}")

        for i in range(8):
            for j in range(8):
                matrix[j, i] = rasters[i] & (1<<j)



# for command-line testing.
# for testing in CP, just do the following in code.py.
#
if __name__ == "__main__":

    # scrolling
    lmd = LEDMatrixDisplay()
    lmd.display_scrolling_text(" Wind 8MPH; Temp 64F - ", 0.01)

    # single char at a time
    import time, random
    while True:
        c = str(random.choice(range(10)))
        lmd.display_single_char(c)
        time.sleep(1)