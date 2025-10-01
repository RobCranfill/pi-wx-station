"""
    Pi-WX-Station
    Using a pair of Adafruit Feather RP2040 RFM69
    w/ BME280 xducer and an anemomter.

    Sending side.

    (c)2025 rob cranfill
    see https://github.com/RobCranfill/pi-wx-station
"""

# region imports

# stdlibs
import board
import digitalio
import json
import os
import time

import microcontroller
import supervisor

from digitalio import DigitalInOut, Pull
import storage

# adafruit libs
import adafruit_rfm69
import neopixel

# my code
import anemom
import sensors

# endregion imports

# region defines
MAX_RFM_MSG_LEN = 60

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

# just test the sensors and data packing?
ACTUALLY_SEND = True

# Read 16-character encryption key.
# TODO: can this fail?
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# endregion defines
# region functions

def set_power_level(rfm, pixel):
    """Check if we are connected to a computer; if so, use low power, to prevent USB corruption."""
    
    connected_to_pc = supervisor.runtime.usb_connected
    # print(f"{connected_to_pc=}")
    color = (0, 255, 0) # green
    if we_are_connected_to_pc:
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
        power = -2 if connected_to_pc==True else 20
    else:
        power = -18 if connected_to_pc==True else 13
    print(f"  {rfm.high_power=} and {connected_to_pc=} -> will set power to {power}")


def show_rfm_info(rfm):
    """ Just for fun """
    print("-------------- RFM Radio info --------------")
    print(f"temperature: {rfm.temperature}C")
    print(f"{rfm.ack_delay=}")
    # print(f"{rfm.__dict__=}")
    print("--------------------------------------------")


def main():

    # Turn off neopixel
    neo = neopixel.NeoPixel(board.NEOPIXEL, 1)
    neo.fill(0)

    # Send delay in seconds 
    # TODO: how should this relate to rcv.LISTEN_TIMEOUT?
    SEND_PERIOD = 4
    print(f"Sending data every {SEND_PERIOD} seconds")

    # Initialize RFM69 radio
    radio = None # why is the board getting corrupted so often?
    if ACTUALLY_SEND:
        radio = adafruit_rfm69.RFM69(board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)
        set_power_level(radio, neo)
        show_rfm_info(radio)
    else:
        print("\n\n****************** NOT USING RADIO!!!!! \n\n")

    # Set up whichever sensor is attatched.
    sensor = sensors.Sensor()
    if sensor is None:
        print("**** No p/t/h sensor???")

    # Our anemometer interface class.
    anemometer = anemom.Anemom(board.D12, LED_DATA_SEND_COLOR, debug=False, neopixel=neo)

    packet_count = 0
    time_start = time.time() # seconds

    while True:

        data_dict = {}

        if sensor.is_ok():

            temp = sensor.temperature()
            t_F = (temp * 9 / 5) + 32
            data_dict['T'] = f"{t_F:2.0f}"

            if sensor.has_humidity():
                hum  = sensor.humidity()
                data_dict['H'] = f"{hum:2.0f}"
            else:
                data_dict['H'] = "?H"

            if sensor.has_pressure():
                pres = sensor.pressure()
                data_dict['P'] = f"{pres:2.0f}"
            else:
                data_dict['P'] = "?P"

        else:
            data_dict['T'] = "T?"
            data_dict['H'] = "H?"
            data_dict['P'] = "P?"

        # Before sending the packet, blink the LED.
        neo.fill(LED_PRE_SEND_COLOR)
        time.sleep(LED_POST_SEND_BLINK)
        neo.fill(LED_COLOR_OFF)

        # Now just get the raw count from the anemomoter;
        # calculate MPH on this side.
        #
        # wind = anemometer.get_mph(COLLECTION_TIME)
        anemom_count = anemometer.get_raw(COLLECTION_TIME)

        # Send the raw anemometer count, to be intrepreted by the rcv side.
        print(f"  {anemom_count=}")
        data_dict['C'] = f"{anemom_count:2.0f}"

        # if we don't do this we exceed 60 chars!
        msg_to_send = json.dumps(data_dict).replace(" ", "")



        # Augment with some status data?
        # TODO: also send CPU or radio temperature? (that is, device temp)

        uptime = time.time() - time_start
        data_dict['U'] = uptime
        msg_augmented = json.dumps(data_dict).replace(" ", "")

        if len(msg_augmented) <= MAX_RFM_MSG_LEN:
            msg_to_send = msg_augmented
        else:
            print(f"Full data packet too large! {len(msg_augmented)=}")
            print(f"  ie: {msg_augmented}")

        packet_count += 1
        print(f"({ACTUALLY_SEND=}) Sending packet #{packet_count}, {len(msg_to_send)} chars: {msg_to_send}")
        try:

            neo.fill(LED_POST_SEND_COLOR)
            if radio is not None:
                radio.send(msg_to_send)
            time.sleep(LED_POST_SEND_BLINK)

        except AssertionError:
            print(f"*** Sending packet failed: {AssertionError}")
        finally:
            neo.fill(LED_COLOR_OFF)

        print(f" Uptime: {uptime} seconds")
        if radio is not None:
            print(f" CPU: {microcontroller.cpu.temperature:1.0f}C; radio: {radio.temperature:1.0f}C")
        time.sleep(SEND_PERIOD)

        # we never exit the send loop.


# endregion functions
# region main

# do it!
main()

# endregion main