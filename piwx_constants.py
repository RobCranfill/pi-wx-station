# piwx constants across the send and receive modules
# also has some executable code - OK?
import os



DICT_KEY_TEMPERATURE = 'T'
DICT_KEY_WIND        = 'W'

DICT_VALUE_NO_THERMOMETER = '?T'
DICT_VALUE_NO_ANEMOMETER  = "?W"

RADIO_FREQ_MHZ = 915.0

# Read 16-character encryption key.
# TODO: can this fail?
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
