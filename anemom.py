# module for anemometer
#
import asyncio
import board
import countio
import digitalio
import keypad
import time


digital_input_pin_ = board.D13


def collect_count(sample_time):
    """Collect pin transitions for the indicated period (seconds)"""

    global count_

    async def catch_pin_transitions(pin, seconds):

        global count_
        end_ticks = time.monotonic_ns() + seconds * 1000000000

        print(f"collect_count: {sample_time=}")
        print(f"start: {time.monotonic_ns()=}, end: {end_ticks=}")

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

    async def main(sample_time):
        interrupt_task = asyncio.create_task(catch_pin_transitions(digital_input_pin_, sample_time))
        await asyncio.gather(interrupt_task)

    count_ = 0
    asyncio.run(main(sample_time))
    return count_


print("\n**** Hello, cran!")

while True:
    print("Collecting...")
    count = collect_count(5)
    print(f" {count}\n")
    
    print("Pausing.....")
    time.sleep(5)

