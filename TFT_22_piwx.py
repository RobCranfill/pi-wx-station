"""
    Code for PiWX display using 2.2" TFT display via SPI.
    Since the RFM radio also uses SPI, we need a different chip select line.

    Fonts generated with
        otf2bdf {font_name}.ttf -p {point_size} -o {font_name}-{point_size}.bdf
      like
        otf2bdf LeagueGothic-Regular.ttf -p 220 -o LeagueGothic-Regular-220.bdf
    
    Also, only required glyphs (0-9, ' ', 'M") are kept in the font file, to keep it small.

"""
import board
import displayio
import time
import random

from fourwire import FourWire
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import adafruit_imageload


import adafruit_ili9341


DEFAULT_FONT_PATH = "fonts/LeagueSpartanBold-220-digits.bdf"

DISPLAY_HEIGHT = 240
DISPLAY_WIDTH  = 320


class TFT22PiWX():
    """"Driver for Adafruit 2.2" TFT display."""

    def __init__(self, rgb_background, font_path=DEFAULT_FONT_PATH):
                
        # Release any resources currently in use for the displays
        displayio.release_displays()

        spi = board.SPI()

        tft_dc = board.D6
        tft_reset = board.D9
        tft_tcs = board.D11 # LCD CS = display chip select
        # tft_sdcs = board.D10 # SD card chip select (unused)

        display_bus = FourWire(spi, command=tft_dc, chip_select=tft_tcs, reset=tft_reset)
        display = adafruit_ili9341.ILI9341(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

        # we need to do manual refresh or the display gets all wonky
        display.auto_refresh = False

        self._display = display

        # Make the display context
        splash = displayio.Group()
        display.root_group = splash

        color_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = rgb_background

        background_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        splash.append(background_sprite)


    # Not the way to go?
        # # Load the sprite sheet (bitmap)
        # sprite_sheet, palette = adafruit_imageload.load("/sprite_sheet_1.bmp",
        #                                         bitmap=displayio.Bitmap,
        #                                         palette=displayio.Palette)

        # # Create a sprite (tilegrid)
        # sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
        #                             width = 1, height = 1,
        #                             tile_width = 64, tile_height = 64)
        # self._sprite = sprite
        # # sprite[0] = 0

        # sprite_group = displayio.Group(scale=1)
        # sprite_group.append(sprite)
        # sprite_group.x = 250
        # sprite_group.y =  20
        # splash.append(sprite_group)


        # Create the text label
        # TODO: catch missing file?
        font_to_use = bitmap_font.load_font(font_path)

        # # for LeagueGothicMedium-220-digits
        # text_area = label.Label(font_to_use, color=0xFFFFFF, x=30, y=85)

        # for LeagueSpartanBold-220-digits
        text_area = label.Label(font_to_use, color=0xFFFFFF, x=-5, y=100)

        splash.append(text_area)
        self._text_area = text_area


    def set_text(self, text):
        """Set the text to display. '0-9' (and 'M', if that's useful) only! You must refresh it when ready."""
        self._text_area.text = text

    def set_text_color(self, rgb_color):
        """Set the text to the indicated RGB color. You must refresh it when ready."""
        self._text_area.color = rgb_color

    def refresh(self):
        """Only repaint the display when done making changes, to make it look nicer."""
        self._display.refresh()

    # def set_temp_wind_icon(self, icon_index):
    #     self._sprite[0] = icon_index


def test():

    print(f"Running {__name__}.test() ...")

    # not in the font, and no room on screen anyway
    # degree = '\u00b0'

    tft = TFT22PiWX(0x_00_00_00)
    # tft.set_text_color(0x_00_00_D0)

    is_temperaure = True
    while True:
        if is_temperaure:
            t = random.randrange(25, 88)
            tft.set_text_color(0x_00FF00)
            tft.set_text(str(t))
            # tft.set_temp_wind_icon(1)
        else:
            t = random.randrange(0, 25)
            tft.set_text_color(0x_0000FF)
            tft.set_text(str(t))
            # tft.set_temp_wind_icon(0)

        is_temperaure = not is_temperaure
        time.sleep(5)

    print("Done! hit ctrl-C")
    while True:
        pass
