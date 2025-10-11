# pi-wx-station
A RP2040-based weather station

# Goal
I want to make my own weather station, in large part becuase
I keep one running at the beach, and they keep dying due to 
the inclement weather; I'd like to be able to repair it rather
than buy a new one every few years!

The Adafruit RFM parts use the so-called ISM "no-license" band at 915MHz. See https://en.wikipedia.org/wiki/ISM_radio_band


# Method
## Hardware:
  * Two Adafruit Feather RP2040 RFM69 microcontrollers (Adafruit part #5712)
  * I2C-based temperature (optionally also pressure/humidity) sensor
  * Anemometer: Part number RS-FSJT-NPN, from Amazon (or see below)
  * Low priority:
    * Wind vane (for wind direction)
    * Solar sensor
  * Display is problematic - see below
  * A light sensor to dim the display as appropriate
  * Antenna as needed; so far a quarter-wave wire antenna suffices (altho it may be marginal)

## Software
  * CircuitPython, of course! Up to version 10.0.0 used in development.
  * Various Adafruit libraries; see 'requirements.txt' for output from 'circup'

## HW Notes
| Anemometer | Signal | Feather |
| ------ | ------ | ------ |
| Brown  | VCC    | USB
| Black  | Ground | GND
| Blue   | signal | GPIO 13
| Yellow | N/C    | N/C


## Thoughts

The radio seems OK for my situation: a distance of about 100 feet, thru several walls of the house,
but nothing too metallic or RF-generating in the way. I do get some missing packets; more research
is needed. (An initial attempt to fix this involves upping the xmit power; we shall see if that works.)

Could be made slightly more cheaply with RP Pico and Adafruit RFM69HCW Transceiver Radio Breakout.

A nicer display would be, uh, nice.

## Version 2
In order to support a more varied set of data points, take a somewhat more sophisticated approach:
 - Xmit various items as they are measured - wind speed every, say, 5 seconds, but temperature every 1 minute.
 - Send each item as an individual radio packet.
 - On the receive side, collect these values locally, and dispay them as desired.
 - This means noticing when a given value goes "stale". This could be complicated. Or not.



## Reference

### Same part?
* https://www.renkeer.com/product/polycarbon-wind-speed-sensor/

When using the pulse-type wind speed sensor, connect the black wire to the power supply and signal ground, the brown wire to the 5-30VDC power supply, the green wire to the pulse signal PNPOUT, and the blue wire to NPN (NPNR) OUT. That’s it! Wide voltage power input is 5~30V.

### Helpful article
 * https://how2electronics.com/interfacing-anemometer-npn-pulse-output-with-arduino/
