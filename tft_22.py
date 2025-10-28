"""
    Code for PiWX display using 2.2" TFT display via SPI.
    Since the RFM radio also uses SPI, we need a different chip select line.

    Fonts generated with
        otf2bdf {font_name}.ttf -p {point_size} -o {font_name}-{point_size}.bdf
      like
        otf2bdf LeagueGothic-Regular.ttf -p 220 -o LeagueGothic-Regular-220.bdf
    
    Also, only required glyphs ([0-9], [' '], [MTW?]) are kept in the font file, to keep it small.

"""
import random
import time

import board
import displayio
import fourwire
import pwmio
import terminalio

from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font
import adafruit_imageload
import adafruit_ili9341


DEFAULT_FONT_PATH = "fonts/LeagueSpartanBold-piwx.bdf"

DISPLAY_HEIGHT = 240
DISPLAY_WIDTH  = 320


class tft_22():
    """"Driver for an Adafruit 2.2" TFT display.
    Features one big text area, and one little 'status' line at the bottom.
    YOu can set the color of the text, and control the display's backlight."""

    def __init__(self, rgb_background, flip_vertical=True, font_path=DEFAULT_FONT_PATH):

        # Release any resources currently in use for the displays.
        displayio.release_displays()

        spi = board.SPI()

        tft_dc = board.D6
        tft_reset = board.D9
        tft_tcs = board.D11 # LCD CS = display chip select
        tft_bl = board.D12 # we need a PWM-capable pin
        # tft_sdcs = board.D10 # SD card chip select (unused so far, probably will never use)

        # rotate = 180 if flip_vertical else 0

        display_bus = fourwire.FourWire(spi, command=tft_dc, chip_select=tft_tcs, reset=tft_reset)
        display = adafruit_ili9341.ILI9341(display_bus, 
            width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotation=180 if flip_vertical else 0)
        self._display = display

        # we need to do manual refresh or the display gets all wonky
        display.auto_refresh = False

        # We control the backlight brightness with this.
        self._backlight = pwmio.PWMOut(tft_bl, duty_cycle=2**16-1, frequency=1000, variable_frequency=True)


        # Make the display context
        splash = displayio.Group()
        display.root_group = splash

        color_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = rgb_background

        background_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        splash.append(background_sprite)

        # Create the main text label.
        # TODO: catch missing file?
        display_font = bitmap_font.load_font(font_path)

        # for LeagueSpartanBold-220-digits
        text_area = bitmap_label.Label(display_font, color=0xFFFFFF, x=-5, y=100)

        splash.append(text_area)
        self._text_area = text_area

        # Nice little status line at the bottom.
        self._text_area_status = bitmap_label.Label(terminalio.FONT, text=f"{__name__} OK",
                                             color=0xFFFFFF, x=10, y=DISPLAY_HEIGHT-6)
        splash.append(self._text_area_status)


    def set_backlight(self, duty_cycle_percent):
        """duty_cycle_percent is 0 thru 100, but 0 is rather low."""

        f_dc = int(65535 * duty_cycle_percent / 100)
        # print(f"Setting set_backlight {duty_cycle_percent=}% or {f_dc=}")
        self._backlight.duty_cycle = f_dc

    def set_text(self, text):
        """Set the text to display. '0-9' (and 'M', if that's useful) only! You must refresh the display when ready."""
        self._text_area.text = text

    def set_text_color(self, rgb_color):
        """Set the text to the indicated RGB color. You must refresh the display when ready."""
        self._text_area.color = rgb_color

    def set_status_text(self, text):
        """The little text area at the bottom. You must refresh the display."""
        self._text_area_status.text = text

    def refresh(self):
        """Only repaint the display when done making changes, to make it look nicer."""
        self._display.refresh()


def test():

    print(f"Running {__name__}.test() ...")

    tft = tft_22(0x_00_00_00)
    # tft.set_text_color(0x_00_00_D0)

    is_temperaure = True
    while True:
        if is_temperaure:
            t = random.randrange(25, 88)
            tft.set_text_color(0x_00FF00)
            tft.set_text(str(t))
            tft.refresh()
        else:
            t = random.randrange(0, 25)
            tft.set_text_color(0x_0000FF)
            tft.set_text(str(t))
            tft.refresh()

        is_temperaure = not is_temperaure
        time.sleep(5)

    print("Done! hit ctrl-C")
    while True:
        pass
