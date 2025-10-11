print()
print("This is the TRANSMITTER side!")

# turn this off - kind of a pain
import supervisor
supervisor.runtime.autoreload = False
print(f"NOTICE: {supervisor.runtime.autoreload=}\n")

import send

# import gc_test_2
# print("done!")
# while True:
#     pass

# import input_test

# import anemom
# a = anemom
# a.demo()


