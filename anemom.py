# Class for anemometer
#
# Pulse-counting code as per 
#  https://learn.adafruit.com/cooperative-multitasking-in-circuitpython-with-asyncio?view=all#communicating-between-tasks
#
import asyncio
import board
import digitalio
import keypad
import neopixel
import time


# Correction factor for count to MPH.
# MPH =  COUNT_TO_MPH * counts_per_sample_time / sample_time
# Gotta figure this out!
COUNT_TO_MPH = 2.0

LED_BLIP_COLOR = 0xFF0000


class anemom:
    """Run the anemometer. Get 1-second sample count. Flash LED while collecting."""

    def __init__(self, input_pin, debug=False, neopixel=None):
        """Debug flag will emit a bit of verbiage. Neopixel will blip on every count."""

        self._input_pin = input_pin
        self._debug = debug
        self._neopixel = neopixel

        print(f"Creating anemom class. {COUNT_TO_MPH=}") if self._debug else True

        # we don't need to - and can't - do this, because keypad.Keys does it for us.
        #
        # input = digitalio.DigitalInOut(input_pin)
        # input.direction = digitalio.Direction.INPUT

    def collect_count(self, sample_time):
        """Collect pin transitions for the indicated period (seconds)"""

        async def catch_pin_transitions(pin, seconds):
            """Watch the given pin for the indicated number of seconds"""

            end_ticks = time.monotonic_ns() + seconds * 1000000000
            print(f" collect_count: {sample_time=}") if self._debug else True
            print(f" start: {time.monotonic_ns()=}, end: {end_ticks=}") if self._debug else True

            with keypad.Keys((pin,), value_when_pressed=False) as keys:
                while True:
                    event = keys.events.get()
                    if event:
                        if event.pressed:
                            self.count_ += 1
                            # print(f" pin went low: {self.count_=}")
                            
                            if self._neopixel is not None:
                                self._neopixel.fill(LED_BLIP_COLOR)

                        elif event.released:
                            # print(" pin went high")
                             if self._neopixel is not None:
                                 self._neopixel.fill(0)

                    if time.monotonic_ns() > end_ticks:
                        # print(" catch_pin_transitions done!")
                        print(f" catch_pin_transitions: {self.count_=}") if self._debug else True
                        return
                    await asyncio.sleep(0)

        async def gather_events(sample_time):
            interrupt_task = asyncio.create_task(catch_pin_transitions(self._input_pin, sample_time))
            await asyncio.gather(interrupt_task)

        self.count_ = 0
        asyncio.run(gather_events(sample_time))
        return self.count_

    def get_mph(self, sample_time):
        """This is the useful thing."""
        count = self.collect_count(sample_time)
        return count * COUNT_TO_MPH / sample_time


def demo():
    """Being an example of using this class."""

    anemometer = anemom(board.D12, debug=False)

    collect_time = 1 # seconds
    busy_time = 3 # seconds

    while True:
        print(f"Collecting for {collect_time} seconds...")

        print(f" {anemometer.get_mph(collect_time)}")

        # to simulate the user code doing something else for a while....
        print(f"Pausing {busy_time} seconds...")
        time.sleep(busy_time)

