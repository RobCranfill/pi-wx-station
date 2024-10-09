
import board
import digitalio
import time

import asyncio
import board
import countio

import asyncio
import board
import keypad


digital_input_pin_ = board.D25

def using_nothing():

    # if I wire this to the blue wire, I get something.
    switch = digitalio.DigitalInOut(digital_input_pin_)

    count = 0
    while True:

        # t = switch.value
        # print(f"{t=}")

        # wait for true
        print("waiting for true..")
        while switch.value is False:
            time.sleep(.01)
        print("got a true!")

        # wait for false
        while switch.value is True:
            time.sleep(.01)
        print("got a false!")

        count = count +1
        print(f"{count=}!")

        # time.sleep(1)


def using_countio():

    global kount
    kount = 0

    async def catch_interrupt(pin):
        global kount
        """Print a message when pin goes low."""
        with countio.Counter(pin) as interrupt:
            while True:
                if interrupt.count > 0:
                    interrupt.count = 0
                    kount = kount + 1
                    print(f"interrupted - {kount=}")

                # Let another task run.
                await asyncio.sleep(0)

    async def main():
        interrupt_task = asyncio.create_task(catch_interrupt(digital_input_pin_))
        await asyncio.gather(interrupt_task)

    asyncio.run(main())


def using_keypad():

    global count_

    """Print a message when pin goes low and when it goes high."""
    async def catch_pin_transitions(pin):

        global count_
        end_ticks = time.monotonic_ns() + 1000000000
        print(f"start: {time.monotonic_ns()=}, end: {end_ticks=}")

        with keypad.Keys((pin,), value_when_pressed=False) as keys:
            while True:
                event = keys.events.get()
                if event:
                    if event.pressed:
                        count_ = count_ + 1
                        print(f"pin went low: {count_=}")
                        print(f"start: {time.monotonic_ns()=}, end: {end_ticks=}")
                    # elif event.released:
                        # print("pin went high")
                if time.monotonic_ns() > end_ticks:
                    print("DONE!")
                    return
                await asyncio.sleep(0)

    async def main():
        interrupt_task = asyncio.create_task(catch_pin_transitions(digital_input_pin_))
        await asyncio.gather(interrupt_task)

    count_ = 0
    asyncio.run(main())



print("\n**** Hello, cran!")

# THESE DON'T WORK
# using_nothing()
# using_countio()

# THIS DOES
using_keypad()
