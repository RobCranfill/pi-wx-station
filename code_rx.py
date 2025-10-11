print()
print("This is the RECEIVER side!")

# turn this off - kind of a pain
import supervisor
supervisor.runtime.autoreload = False
print(f"NOTICE: {supervisor.runtime.autoreload=}")
print()

################ the real deal
import rcv


################ Testinng zone

# import LEDMatrix
# lm = LEDMatrix
# lm.test()


# import TwoCharLED

# import displayText

# import matrix_display_16x8
# matrix_display_16x8.test_2()

# import feather_oled
