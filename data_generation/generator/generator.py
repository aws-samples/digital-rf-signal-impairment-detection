from gnuradio import gr
from file_atsc_tx import file_atsc_tx
import random
import time
import os

# Configure the number of files in the dataset
NUMBER_OF_FILES = 2

# Configure the amount of phase noise to introduce
# create dictionary of configs settings
PHASE_NOISE = {
    "PHASE_NOISE_MIN": 0.05,
    "PHASE_NOISE_MAX": 0.15,
    "PHASE_NOISE_ALPHA_MIN": 0.1,
    "PHASE_NOISE__ALPHA_MAX": 0.5,
    "NOISE_SOURCE_MIN": 0.0001,
    "NOISE_SOURCE_MAX": 0.01,
    "OUTPUT_FILE_PATH": "./data/%s/phase_noise-%s.txt"
}

NORMAL = {
    "PHASE_NOISE_MIN": 0,
    "PHASE_NOISE_MAX": 0,
    "PHASE_NOISE_ALPHA_MIN": 0,
    "PHASE_NOISE__ALPHA_MAX": 0,
    "NOISE_SOURCE_MIN": 0.01,
    "NOISE_SOURCE_MAX": 0.02,
    "OUTPUT_FILE_PATH": "./data/%s/normal-%s.txt"
}

# COMPRESSION = {
#     "PHASE_NOISE_MIN": 0,
#     "PHASE_NOISE_MAX": 0,
#     "PHASE_NOISE_ALPHA_MIN": 0,
#     "PHASE_NOISE__ALPHA_MAX": 0,
#     "NOISE_SOURCE_MIN": 0.0001,
#     "NOISE_SOURCE_MAX": 0.01,
#     "OUTPUT_FILE_PATH": "./data/normal-%s.txt"
# }

INTERFERENCE = {
    "PHASE_NOISE_MIN": 0,
    "PHASE_NOISE_MAX": 0,
    "PHASE_NOISE_ALPHA_MIN": 0,
    "PHASE_NOISE__ALPHA_MAX": 0,
    "NOISE_SOURCE_MIN": 0.03,
    "NOISE_SOURCE_MAX": 0.04,
    "OUTPUT_FILE_PATH": "./data/%s/interference-%s.txt"
}

CONFIG = NORMAL
blobs = ["qpsk", "8psk", "16apsk", "32apsk"]
# CONFIG = INTERFERENCE
# CONFIG = PHASE_NOISE

# Run the flowgraph on repeat
for mod in blobs:
    for i in range(0, NUMBER_OF_FILES):
        print("Working on file %f", i)
        theTime = time.time()
        print(theTime)
        flowgraph = file_atsc_tx(mod)
        flowgraph.set_phase_noise(random.uniform(CONFIG['PHASE_NOISE_MIN'], CONFIG['PHASE_NOISE_MAX']))
        flowgraph.set_phase_noise_alpha(random.uniform(CONFIG['PHASE_NOISE_ALPHA_MIN'], CONFIG['PHASE_NOISE__ALPHA_MAX']))
        flowgraph.set_noise_source(random.uniform(CONFIG['NOISE_SOURCE_MIN'], CONFIG['NOISE_SOURCE_MAX']))
        flowgraph.set_outputFile(CONFIG['OUTPUT_FILE_PATH'] % (mod, i))
        flowgraph.start()
        flowgraph.wait()

# GNU Radio makes initial empty output file, removing it
file_path = 'data/output-.txt'
if os.path.exists(file_path):
    os.remove(file_path)