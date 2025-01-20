# Class for anemometer
#
# pulse-counting code as per 
#  https://learn.adafruit.com/cooperative-multitasking-in-circuitpython-with-asyncio?view=all#communicating-between-tasks
#
import asyncio
import board
import digitalio
import keypad
import time


# DIGITAL_INPUT_PIN = board.D13

class anemom:

    def __init__(self, input_pin, debug=False):
        self._input_pin = input_pin
        self._debug = debug

    def collect_count(self, sample_time):
        """Collect pin transitions for the indicated period (seconds)"""

        async def catch_pin_transitions(pin, seconds):

            # global count_
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
                        # elif event.released:
                            # print(" pin went high")
                    if time.monotonic_ns() > end_ticks:
                        # print(" catch_pin_transitions done!")
                        return
                    await asyncio.sleep(0)

        async def gather_events(sample_time):
            interrupt_task = asyncio.create_task(catch_pin_transitions(self._input_pin, sample_time))
            await asyncio.gather(interrupt_task)

        self.count_ = 0
        asyncio.run(gather_events(sample_time))
        return self.count_


anemometer = anemom(board.D13, debug=False)

collect_time = 5 # seconds
busy_time = 3 # seconds

while True:
    print(f"Collecting for {collect_time} seconds...")
    count = anemometer.collect_count(collect_time)
    print(f"  {count=}\n")

    print(f"Pausing {busy_time} seconds.....")
    time.sleep(busy_time)

