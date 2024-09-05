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
  * Two Adafruit Feather RP2040 RFM69 microcontrollers
  * I2C-based temperature/pressure/humidity sensor
  * Some kind of anemometer
  * Low priority:
    * Wind vane (for wind direction)
    * Solar sensor
  * Display is problematic - see below
  * Antenna as needed; so far a quarter-wave wire antenna suffices!


## Software
  * CircuitPython, of course! 9.1.3 used.
  * Various Adafruit libraries; see 'requirements.txt' for output from 'circup'


## Thoughts

Could be made more cheaply with QTPy and Adafruit RFM69HCW Transceiver Radio Breakout?


