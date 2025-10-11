"""
    Pi-WX-Station
    Using a pair of Adafruit Feather RP2040 RFM69
    and appropriate transducers and displays.

    Sending side. Version 2: KISS.

    (c)2025 rob cranfill
    see https://github.com/RobCranfill/pi-wx-station
"""

# region imports

# stdlibs
import board
import digitalio
import json
import microcontroller
import os
import random
import supervisor
import time

# Adafruit libs
import adafruit_rfm69
import neopixel

# my code
import anemom
import sensors
import piwx_constants


# endregion imports

# region defines

# Send delay in seconds. This is in addition to data collection time.
# TODO: How should this relate to rcv.LISTEN_TIMEOUT?
SEND_DELAY = 2

# Define some stuff
COLLECTION_TIME = 1 # collect anemometer data for this many seconds at a time
LED_PRE_SEND_COLOR  = 0x00_FF_00
LED_PRE_SEND_BLINK  = 0.5
LED_POST_SEND_COLOR = 0x00_00_FF
LED_DATA_SEND_COLOR = 0xFF_00_00
LED_POST_SEND_BLINK = 0.5
LED_COLOR_OFF = 0x00_00_00

# Don't change this!
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM_CS)
RESET = digitalio.DigitalInOut(board.RFM_RST)

# This is a hardware limit
MAX_RFM_MSG_LEN = 60

# just test the sensors and data packing, or actually send data?
ACTUALLY_SEND = True

# Read 16-character encryption key.
# TODO: can this fail?
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# endregion defines

# region functions

def set_power_level(rfm, pixel):
    """Check if we are connected to a computer; if so, use low power, to prevent USB corruption."""

    connected_to_pc = supervisor.runtime.usb_connected
    print(f"{connected_to_pc=}")
    color = (0, 255, 0) # green
    if connected_to_pc:
        color = (255, 0, 0) # red

    for i in range(3):
        pixel.fill(color)
        time.sleep(.5)
        pixel.fill(0)
        time.sleep(.5)

# The transmit power in dBm.
# Can be set to a value from -2 to 20 for high power devices (RFM69HCW, high_power=True)
#  or -18 to 13 for low power devices.
#
    if rfm.high_power:
        power =  -2 if connected_to_pc else 20
    else:
        power = -18 if connected_to_pc else 13
    print(f"  {rfm.high_power=} and {connected_to_pc=} -> will set power to {power}")


def init_radio(neo_pix):
    """Return the RFM object."""

    radio = adafruit_rfm69.RFM69(board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)
    if radio is None:
        print("What? no radio???")
        return None

    set_power_level(radio, neo_pix)

    # Also set some of these????
    # 'xmit_timeout': 2.0, 'ack_wait': 0.5, 'ack_delay': None

    # Just for fun
    print("-------------- RFM Radio info --------------")
    print(f"temperature: {radio.temperature}C")
    print(f"{radio.ack_delay=}")
    # print(f"{radio.__dict__=}")
    print("--------------------------------------------")

    return radio

COUNT_TO_MPH_CONST = 1

def count_to_mph(count, period):
    """Return the MPH implied by the given count over the indicated period in seconds."""
    return int(count / period * COUNT_TO_MPH_CONST)


def create_initial_data_dict():
    return {}

def update_data_dict(data_dict, sensor, anemom):
    """Populate with the *display values* for the receiving station to show."""

    # Get the temperature.
    if sensor.is_ok():
        temp = sensor.temperature()
        temp_f = (temp * 9 / 5) + 32
        data_dict[piwx_constants.DICT_KEY_TEMPERATURE] = f"{temp_f:2.0f}" # TODO: negative? >100?
    else:
        data_dict[piwx_constants.DICT_KEY_TEMPERATURE] = piwx_constants.DICT_VALUE_NO_THERMOMETER

    USE_RANDOM_WIND = True
    if not USE_RANDOM_WIND:

        # Caclulate wind speed.
        anemom_count = anemom.get_raw(COLLECTION_TIME)
    else:
        # FIXME: for testing
        anemom_count = random.randint(0, 30)

    mph = count_to_mph(anemom_count, COLLECTION_TIME)
    print(f" {anemom_count=} -> {mph} MPH")
    data_dict[piwx_constants.DICT_KEY_WIND] = f"{mph:2.0f}"

    return data_dict


def main():
    """This has our forever processing loop."""

    # Turn off neopixel
    neo = neopixel.NeoPixel(board.NEOPIXEL, 1)
    neo.fill(0)


    ## Set up whichever temperature sensor is attatched.
    sensor = sensors.Sensor()
    if sensor is None:
        print("**** No p/t/h sensor???")


    ## Our anemometer interface.
    anemometer = anemom.Anemom(board.D12, LED_DATA_SEND_COLOR, debug=False, neopixel=neo)


    ## Initialize RFM69 radio
    radio = None
    if ACTUALLY_SEND:
        radio = init_radio(neo)
    else:
        print("\n\n****************** NOT USING RADIO!!!!! \n\n")

    packet_count = 0
    time_start = time.time() # seconds

    data_dict = create_initial_data_dict()

    print(f"\nSending data every {SEND_DELAY} seconds at most.\n")

    while True:

        data_dict = update_data_dict(data_dict, sensor, anemometer)
        # if we don't do this we exceed 60 chars!
        msg_to_send = json.dumps(data_dict).replace(" ", "")


        # Augment with some status data?
        uptime = time.time() - time_start
        # print(f" Uptime: {uptime} seconds")
        data_dict['U'] = uptime
        msg_augmented = json.dumps(data_dict).replace(" ", "")

        # TODO: also send CPU or radio temperature? (that is, device temp)
        # if radio is not None:
        #     print(f" CPU: {microcontroller.cpu.temperature:1.0f}C; radio: {radio.temperature:1.0f}C")

        if len(msg_augmented) <= MAX_RFM_MSG_LEN:
            msg_to_send = msg_augmented
        else:
            print(f"Full data packet too large! {len(msg_augmented)=}")
            print(f"  ie: {msg_augmented}")

        packet_count += 1
        print(f"({ACTUALLY_SEND=}) Sending packet #{packet_count}, {len(msg_to_send)} chars: {msg_to_send}\n")
        try:
            neo.fill(LED_POST_SEND_COLOR)
            if radio is not None:

                # Before sending the packet, blink the LED.
                neo.fill(LED_PRE_SEND_COLOR)
                time.sleep(LED_POST_SEND_BLINK)
                neo.fill(LED_COLOR_OFF)

                radio.send(msg_to_send)
            time.sleep(LED_POST_SEND_BLINK)

        except AssertionError:
            print(f"*** Sending packet failed: {AssertionError}")
        finally:
            neo.fill(LED_COLOR_OFF)

        time.sleep(SEND_DELAY)

        # we never exit the send loop.


# endregion functions
# region main

# do it!
main()

# endregion main