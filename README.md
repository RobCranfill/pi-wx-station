# pi-wx-station
A Feather RP2040-based weather station

# Goal
I want to make my own weather station, in large part becuase
I keep one running at the beach, and they keep dying due to 
the inclement weather; I'd like to be able to repair it rather
than buy a new one every few years!


# Method
## Hardware
  * Two Adafruit Feather RP2040 RFM69 microcontrollers (Adafruit part #5712)
  * I2C-based temperature (optionally also pressure/humidity) sensor
  * Anemometer: Part number RS-FSJT-NPN, from Amazon (or see below)
  * Adafruit 2.2" TFT LCD display - beautiful!
  * A light sensor so we can dim the display as appropriate
  * Antennas as needed; so far a quarter-wave wire antenna suffices (altho it may be marginal)
  * Low priority:
    * Pressure, humidity display
    * Wind vane (for wind direction)
    * Solar sensor

## Software
  * CircuitPython, of course! Up to version 10.x used in development.
  * Various Adafruit libraries; see 'requirements.txt' for output from 'circup'.

## HW Notes
| Anemometer | Signal | Feather |
| ------ | ------ | ------ |
| Brown  | VCC    | USB
| Black  | Ground | GND
| Blue   | signal | GPIO 13
| Yellow | N/C    | N/C

The TFT display uis now using a boatload of pins:
| Feather | Signal | TFT display |
| ------ | ------ | ------ |
| Gnd  | Gnd | GND
| 3v3  | 3v3 | VIN
| D5  | SPI data/command | D/C
| D9 | TFT reset | RESET
| (D10)  | SD card SPI chip select - unused so far | SD CS
| D11 | TFT SPI chip select | LCD CS
| MOSI  | SPI MCU Out | MOSI
| MISO  | SPI MCU In | MISO
| SCK  | SPI clock | SCK
| D12  | Backlight PWM | BACKLIGHT

Note that the RFM radio also uses the SPI bus so you have to avoid using its chip select line, D5 (SPI0 CS) :-/


## Thoughts

Initially the radio would miss occasional packets, when we used the default power settings. 
We now set the xmit power to the maximum *when we are NOT running in "USB connected" mode -
that is, not when the Feather is being presented as a USB disk, indicating we are connecfed to a PC
and in dev mode. When in USB mode, we set the xmit power to the minimum. This is becuase some online
info indicated that this can cause USB data corruption, which indeed we may have experienced.

Could be made slightly more cheaply with RP Pico and Adafruit RFM69HCW Transceiver Radio Breakout.

## Things to do - or not

### Bugz
 * Dropped packets - don't update average wind speed

### New features
 * Use the VCNL4020's (light sensor) proxmity sensing for control?
   - Will have to modify case?


### Fancier data collection? (Not really needed yet)
In order to support a more varied set of data points, take a somewhat more sophisticated approach:
 - Xmit various items as they are measured - wind speed every, say, 5 seconds, but temperature every 1 minute.
 - Send each item as an individual radio packet.
 - On the receive side, collect these values locally, and dispay them as desired.
 - This means noticing when a given value goes "stale". This could be complicated. Or not.
 This seems unnecessarily complicated, espcially when I'm only taking two data measurements. Not now.


## Reference

### Same part?
* https://www.renkeer.com/product/polycarbon-wind-speed-sensor/

When using the pulse-type wind speed sensor, connect the black wire to the power supply and signal ground, the brown wire to the 5-30VDC power supply, the green wire to the pulse signal PNPOUT, and the blue wire to NPN (NPNR) OUT. That’s it! Wide voltage power input is 5~30V.

### Helpful article
 * https://how2electronics.com/interfacing-anemometer-npn-pulse-output-with-arduino/

### Radio
The Adafruit RFM parts use the so-called ISM "no-license" band at 915MHz. See https://en.wikipedia.org/wiki/ISM_radio_band


### Notes on creating a font for TFT display

1) Create a bitmap of appropriate size:
	
	`otf2bdf LeagueGothic-Regular.ttf -p 220 -o LeagueGothic-Regular-220.bdf`

2) Using FontForge, remove all but digits, "M" (for kerning), " , "T", "W" and "?".
 
	- Open bdf file
	- Select 0-9, M, T, W, '?' and ' ' (space)
	- Edit / Invert selection
	- Encoding / Detach & Remove Glyphs... 
	- File / Generate Fonts...
    - Save as "fonts/LeagueSpartanBold-piwx.bdf"
