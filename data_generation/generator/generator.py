from gnuradio import gr
from file_atsc_tx import file_atsc_tx
import random
import time
import os

# Configure the number of files in the dataset
NUMBER_OF_FILES = 100
modcod = ["qpsk", "8psk", "16apsk", "32apsk"]

# Configure the amount of phase noise to introduce, see the gnuradio GUI for more info
classes = [
{"class_name": "phase_noise",
 "CONFIG": {
    "PHASE_NOISE_MIN": 0.05,
    "PHASE_NOISE_MAX": 0.15,
    "PHASE_NOISE_ALPHA_MIN": 0.1,
    "PHASE_NOISE__ALPHA_MAX": 0.5,
    "NOISE_SOURCE_MIN": 0.0001,
    "NOISE_SOURCE_MAX": 0.01,
    "OUTPUT_FILE_PATH": "./data/%s/%s/phase_noise-%s.txt"
}},
{"class_name": "normal",
 "CONFIG": {
    "PHASE_NOISE_MIN": 0,
    "PHASE_NOISE_MAX": 0,
    "PHASE_NOISE_ALPHA_MIN": 0,
    "PHASE_NOISE__ALPHA_MAX": 0,
    "NOISE_SOURCE_MIN": 0.01,
    "NOISE_SOURCE_MAX": 0.02,
    "OUTPUT_FILE_PATH": "./data/%s/%s/normal-%s.txt"
}},
{"class_name": "interference",
 "CONFIG":  {
    "PHASE_NOISE_MIN": 0,
    "PHASE_NOISE_MAX": 0,
    "PHASE_NOISE_ALPHA_MIN": 0,
    "PHASE_NOISE__ALPHA_MAX": 0,
    "NOISE_SOURCE_MIN": 0.03,
    "NOISE_SOURCE_MAX": 0.04,
    "OUTPUT_FILE_PATH": "./data/%s/%s/interference-%s.txt"
}}]
# TODO use gnuradio to generate compression
# COMPRESSION = {
#     "PHASE_NOISE_MIN": 0,
#     "PHASE_NOISE_MAX": 0,
#     "PHASE_NOISE_ALPHA_MIN": 0,
#     "PHASE_NOISE__ALPHA_MAX": 0,
#     "NOISE_SOURCE_MIN": 0.0001,
#     "NOISE_SOURCE_MAX": 0.01,
#     "OUTPUT_FILE_PATH": "./data/normal-%s.txt"
# }

# Run the flowgraph on repeat
for mod in modcod:
    for i in classes:
        for j in range(0, NUMBER_OF_FILES):
            flowgraph = file_atsc_tx(mod)
            flowgraph.set_phase_noise(random.uniform(i['CONFIG']['PHASE_NOISE_MIN'], i['CONFIG']['PHASE_NOISE_MAX']))
            flowgraph.set_phase_noise_alpha(random.uniform(i['CONFIG']['PHASE_NOISE_ALPHA_MIN'], i['CONFIG']['PHASE_NOISE__ALPHA_MAX']))
            flowgraph.set_noise_source(random.uniform(i['CONFIG']['NOISE_SOURCE_MIN'], i['CONFIG']['NOISE_SOURCE_MAX']))
            flowgraph.set_outputFile(i['CONFIG']['OUTPUT_FILE_PATH'] % (mod, i["class_name"], j)) # set output file path as ex. data/8psk/normal
            flowgraph.start()
            flowgraph.wait()

# GNU Radio makes initial empty output file, removing it
file_path = 'data/output-.txt'
if os.path.exists(file_path):
    os.remove(file_path)