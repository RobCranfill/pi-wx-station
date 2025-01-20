# pi-wx-station
RP2040-based weather station

# Goal
I want to make my own weather station, in large part becuase
I keep one running at the beach, and they keep dying due to 
the inclement weather; I'd like to be able to repair it rather
than buy a new one every few years!

The Adafruit RFM parts use the so-called ISM "no-license" band at 915MHz. See https://en.wikipedia.org/wiki/ISM_radio_band


# Method
## Hardware:
  * Two Adafruit Feather RP2040 RFM69 microcontrollers (Adafruit part #5712)
  * I2C-based temperature/pressure/humidity sensor
  * Anemometer: Part number RS-FSJT-NPN, from Amazon
  * Low priority:
    * Wind vane (for wind direction)
    * Solar sensor
  * Display is problematic - see below
  * Antenna as needed; so far a quarter-wave wire antenna suffices!


## Software
  * CircuitPython, of course! 9.2.2 used so far.
  * Various Adafruit libraries; see 'requirements.txt' for output from 'circup'

## HW Notes

| Anemometer      | Signal | Feather |
| ----------- | ----------- | ----------- |
| Brown/Green      | VCC       | USB
| Black   | Ground        | GND
| Blue   | signal        | GPIO 13
| Yellow   | NC        | NC


## Thoughts

Could be made slightly more cheaply with RP Pico and Adafruit RFM69HCW Transceiver Radio Breakout.

