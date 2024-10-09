# module for anemometer
#
import asyncio
import board
import countio
import digitalio
import keypad
import time


digital_input_pin_ = board.D25


def collect_count():
    """Collect pin transitions for the indicated period (always 1 second?)"""

    global count_

    async def catch_pin_transitions(pin):

        global count_
        end_ticks = time.monotonic_ns() + 1000000000
        # print(f"start: {time.monotonic_ns()=}, end: {end_ticks=}")

        with keypad.Keys((pin,), value_when_pressed=False) as keys:
            while True:
                event = keys.events.get()
                if event:
                    if event.pressed:
                        count_ += 1
                        # print(f"pin went low: {count_=}")
                    # elif event.released:
                        # print("pin went high")
                if time.monotonic_ns() > end_ticks:
                    # print("catch_pin_transitions done!")
                    return
                await asyncio.sleep(0)

    async def main():
        interrupt_task = asyncio.create_task(catch_pin_transitions(digital_input_pin_))
        await asyncio.gather(interrupt_task)

    count_ = 0
    asyncio.run(main())
    return count_


print("\n**** Hello, cran!")

while True:
    print("Collecting...")
    count = collect_count()
    print(f" {count}\n")
    time.sleep(5)

