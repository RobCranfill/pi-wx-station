# pi-wx-station
RP2040-based weather station

# Goal
I want to make my own weather station, in large part becuase
I keep one running at the beach, and they keep dying due to 
the inclement weather; I'd like to be able to repair it rather
than buy a new one every few years!


# Implementation
## Hardware
  * Two Adafruit Feather RP2040 microcontrollers with RFM69 Packet Radio (Adafruit part #5712)
  * Adafruit BME280 I2C-based temperature/pressure/humidity sensor
  * VCNL4020 I2C light sensor, Adafruit Product ID 5810
  * Anemometer: Part number RS-FSJT-NPN, from Amazon (or see below)
  * Low priority, not yet implemented:
    * Rain guage
    * Wind vane (for wind direction)
    * Solar sensor
  * Display is problematic
    * For now, using an Adafruit 16x8 1.2" LED Matrix (part #2042)
  * Antenna as needed; so far a quarter-wave wire antenna suffices.

## Software
  * CircuitPython, of course! Latest version, 9.2.4, used for development.
  * Various Adafruit libraries; see 'requirements.txt' for output from 'circup'

## To Do
 * Better fade in/out on display

## HW Notes
| Anemometer | Signal | Feather |
| ------ | ------ | ------ |
| Brown  | VCC    | USB
| Black  | Ground | GND
| Blue   | signal | GPIO 13
| Yellow | N/C    | N/C


## Thoughts
### Alternative parts
 Could be made slightly more cheaply with RP Pico and Adafruit RFM69HCW Transceiver Radio Breakout.

### Display
What sort of display? I want something readable from across the room, but not too distracting.
For now I'm just using two 8x8 LED matrices, which are cheap-ish, readable from afar; not that cool looking tho!


## Reference
 * The Adafruit RFM parts use the so-called ISM "no-license" band at 915MHz. See https://en.wikipedia.org/wiki/ISM_radio_band

### Anemometer connections
* Is this ame anemomoter? Looks like it:
** https://www.renkeer.com/product/polycarbon-wind-speed-sensor/

When using the pulse-type wind speed sensor, connect the black wire to the power supply and signal ground, the brown wire to the 5-30VDC power supply, the green wire to the pulse signal PNPOUT, and the blue wire to NPN (NPNR) OUT. That’s it! Wide voltage power input is 5~30V.

### Helpful article
 * https://how2electronics.com/interfacing-anemometer-npn-pulse-output-with-arduino/
