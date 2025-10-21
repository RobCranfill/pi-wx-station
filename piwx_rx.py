"""
    Pi-WX-Station
    Using a pair of Adafruit Feather RP2040 RFM69
    This is the receiver side
    using an Adafruit 16x8 LED "backpack". 
    (c)2025 rob cranfill
    See https://github.com/RobCranfill/pi-wx-station

    Version 2: TFT test
        - Note: remember that the display font only has 0-9, " " and "M" in it!!

"""

# stdlibs
import board
import digitalio
import json
import os
import random
import time
import traceback

# adafruit libs
import adafruit_rfm69
from adafruit_ht16k33 import matrix
import adafruit_vcnl4020
import neopixel

# mine
# import LEDMatrix
import tft_22

import piwx_constants
import moving_average



########################################################

# Pause between showing the various measurements, in seconds.
DISPLAY_WAIT = 3

# TODO: this may be important.
# We send every X seconds, we should probably wait for 2X seconds??
LISTEN_TIMEOUT  = 8

# we will re-use old data for this many missed packets
MAX_MISSED_PACKETS = 8

# we will display data elements from this is we get more than MAX_MISSED_PACKETS
NO_DATA_PACKET = {}
NO_DATA_PACKET['T'] = 'T?'
NO_DATA_PACKET['C'] = 'W?'

# We will average the wind over this many readings (which take 2-3 seconds each).
WIND_MOVING_AVG_SAMPLES = 5


def show_radio_status(radio):
    """For fun. But also could use to show local temp - if it worked!"""

    print("RFM69 status:")
    print(f"  {radio.bitrate=}")
    print(f"  {radio.encryption_key=}")
    print(f"  {radio.frequency_deviation=}")
    print(f"  {radio.rssi=}")
    print(f"  {radio.temperature=}C, {c_to_f(radio.temperature)}F")
    print()


def get_message(rfm):
    '''Return the dictionary of values received by the radio, or None'''

    # Look for a new packet - wait up to given timeout
    print("\nListening...")
    packet = rfm.receive(timeout=LISTEN_TIMEOUT)
    # print(" Got a packet or timed out....")

    # If no packet was received after the timeout then None is returned.
    result = None
    if packet is None:
        print("No packet?")
    else:
        print(f" Got a packet; {rfm.last_rssi=}")
        pstr = packet.decode('utf8')
        # print(f"Rcvd: '{pstr}'")

        # TODO: catch exception?
        result = json.loads(pstr)

    # also get local temp?

    return result


def init_hardware():
    """Init the radio, display, and light sensor and return them."""

    CS = digitalio.DigitalInOut(board.RFM_CS)
    RESET = digitalio.DigitalInOut(board.RFM_RST)

    # Initialize RFM69 radio
    rfm = adafruit_rfm69.RFM69(board.SPI(), CS, RESET,
                               piwx_constants.RADIO_FREQ_MHZ, encryption_key=piwx_constants.ENCRYPTION_KEY)
    # show_radio_status(rfm)

    # leds = LEDMatrix.LEDMatrix()
    tft = tft_22.tft_22(0x_00_00_00)

    tft.set_status_text("Starting up...")
    # tft.set_text_color(0x_00FF00)
    tft.refresh()

    # Does this help? no, not obviously, and adds >10 seconds to startup.
    #
    # print("pre-loading glyphs....")
    # t_start = time.monotonic()
    # for i in range(10):
    #     tft.set_text(str(i))
    # print(f"done in {time.monotonic() - t_start} seconds")

    # Initialize VCNL4020 light sensor.
    vcln = None
    try:
        vcln = adafruit_vcnl4020.Adafruit_VCNL4020(board.I2C())
        vcln.lux_enabled = True
        vcln.proximity_enabled = False
    except:
        print("No light sensor? Continuing....")

    return rfm, tft, vcln


def get_brightness_value(light_sensor):
    """Calculate a value 0-15 for display brighness acccording to ambient light."""

    # TODO: Not sure what max possible lux is.
    #
    if light_sensor is None:
        lux = 1000 # full brightness, sorta
    else:
        lux = light_sensor.lux

    # 1000 lux, "indoors near the windows on a clear day", gets full LED value.
    # This seems OK, but not very scientific
    # 1000 seems low. 4000?
    scaled = lux / 4000
    if scaled > 1:
        scaled = 1

    # Then scale to 0-15, the display's range.
    scaled_int = int(15 * scaled)
    # print(f" Brightness: {lux=} -> {scaled_int=}")
    return scaled_int

# def count_to_mph(count):
#     """Return integer MPH as a string"""

#     mph = int(count / 15)
#     print(f" count_to_mph: {count=} -> {mph=}")
#     return str(mph)

def c_to_f(c):
    """Return farenheit from celsius"""
    return (c*9/5) + 32


def initial_dict():
    """Dictionary of values we display, with defaults."""
    d = {}
    d['T'] = piwx_constants.DICT_VALUE_NO_THERMOMETER
    d['W'] = piwx_constants.DICT_VALUE_NO_ANEMOMETER
    return d


def update_dict_from_radio(rfm, dict, missed_packet_count):
    """Return (new dictionary, missed packet count)."""

    # Get a radio packet.
    #
    data = get_message(rfm)
    print(f" Received: {data=}")

    # For testing, miss 80% of packets
    if data is None: # or random.randint(0, 10) > 2:
        missed_packet_count += 1
        print(f"** missing packet #{missed_packet_count}")

        if missed_packet_count >= MAX_MISSED_PACKETS:
            print("*** MISSED PACKETS > {MAX_MISSED_PACKETS}!")
            dict = initial_dict()

    else:
        print("Got data packet - resetting missed packet count.")
        missed_packet_count = 0
        # led_matrix.set_aux_indicator(0)

        for k in ['T', 'W']:

            #TODO: shouldn't these just be integers?

            data_val = str(data[k])
            # if len(data_val) < 2:
            #     data_val = ' ' + data_val
            dict[k] = data_val
            print(f" * update_dict_from_radio assigning {k} = '{dict[k]}'")
        print(f" update_dict_from_radio: {dict=}")

    return dict, missed_packet_count


def update_display(tft, text, is_temperature, missed_packets):
    """Update all the things."""

    print(f" DISPLAY: '{text}' {is_temperature}")

    tft.set_text(text)
    if is_temperature:
        tft.set_text_color(0x00FF00)
    else:
        tft.set_text_color(0x0000FF)
    
    tft.refresh()

    # led.set_mode_indicator(is_temperature)
    # led.set_aux_indicator_h(missed_packets)


def test_tft_display(display):

    display.set_text("00")

    is_temperaure = True
    while True:
        if is_temperaure:
            t = random.randrange(25, 88)
            display.set_text_color(0x_00FF00)
            print(f" * Displaying '{t}'...")
            display.set_text(str(t))
            # tft.set_temp_wind_icon(1)
        else:
            t = random.randrange(0, 25)
            display.set_text_color(0x_0000FF)
            print(f" * Displaying '{t}'...")
            display.set_text(str(t))
            # tft.set_temp_wind_icon(0)

        is_temperaure = not is_temperaure
        time.sleep(5)


def show_status_info(radio, display, missed):

    # If we do this *before* update_display, we can let that method do the update()
    display.set_status_text(f"{missed} missed packets; RSSI {radio.rssi}")


def run():

    missed_packets = 0

    radio, tft_display, sensor = init_hardware()

    data_dict = initial_dict()
    print(f" initial {data_dict=}")

    averager = moving_average.moving_average(WIND_MOVING_AVG_SAMPLES)
    print(f"* Averaging wind readings over {WIND_MOVING_AVG_SAMPLES} samples.")

    # Run this loop forever.
    while True:

        data_dict, missed_packets = update_dict_from_radio(radio, data_dict, missed_packets)

        # we can't treat T and W the same any more :-/

        # Temp is always good to display.
        print()
        print(" ** Display temp:")
        temp_str = data_dict[piwx_constants.DICT_KEY_TEMPERATURE]

        show_status_info(radio, tft_display, missed_packets)
        update_display(tft_display, temp_str, True, missed_packets)

        time.sleep(DISPLAY_WAIT)

        # Wind needs massaging (only latest data point was sent; we want the average)
        #
        print(" ** Display wind:")
        w_data = data_dict[piwx_constants.DICT_KEY_WIND]
        if w_data == piwx_constants.DICT_VALUE_NO_ANEMOMETER:
            wind_str = w_data
        else:
            wind_val = float(w_data)

            # # to display most recent wind value:
            # wind_str = str(int(wind_val))

            # to display average:
            avg = averager.update_moving_average(wind_val)
            print(f" >> wind speed {wind_val}; {WIND_MOVING_AVG_SAMPLES} second average now {avg}")
            wind_str = f"{avg:2.0f}"

        show_status_info(radio, tft_display, missed_packets)
        update_display(tft_display, wind_str, False, missed_packets)

        time.sleep(DISPLAY_WAIT)

    # end run()


run()

# If we just import this module, this code runs.
# Is this the best way to do this???
#
while True:
    try:
        run()
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Got exception {e}; going around again!")
        traceback.print_exception(e)


print("DONE!")
while True:
    pass


# def test():
#     LEDMatrix.test()
