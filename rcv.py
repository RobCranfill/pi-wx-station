"""
Pi-WX-Station
Using a pair of Adafruit Feather RP2040 RFM69
receiving side
(c)2024 rob cranfill
"""

# stdlibs
import board
import digitalio
import json
import os

# adafruit
import neopixel
import adafruit_rfm69

# my code
import displayText


# Define some stuff
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM_CS)
RESET = digitalio.DigitalInOut(board.RFM_RST)

# Read 16-character encryption key.
# TODO: can this fail?
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")


# Initialize RFM69 radio
rfm69 = adafruit_rfm69.RFM69(
    board.SPI(), CS, RESET, RADIO_FREQ_MHZ, encryption_key=ENCRYPTION_KEY)

print(f"{rfm69.bitrate=}")
print(f"{rfm69.encryption_key=}")
print(f"{rfm69.frequency_deviation=}")
print(f"{rfm69.rssi=}")
print(f"{rfm69.temperature=}")

# my display code
lmd = displayText.LEDMatrixDisplay()

    
print("Waiting for packets...")

while True:

    # Look for a new packet - wait up to given timeout
    packet = rfm69.receive(timeout=10)

    # If no packet was received after the timeout then None is returned.
    if packet is not None:

        pstr = packet.decode('utf8')
        print(f"Rcvd: '{pstr}'")

        dict = json.loads(pstr)
        display_str = dict["T"] + " "
        for c in display_str:
            lmd.display_single_char(c)

    else:
        print("No packet")

