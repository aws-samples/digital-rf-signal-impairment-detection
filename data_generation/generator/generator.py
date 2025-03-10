from gnuradio import gr
from file_atsc_tx import file_atsc_tx
import random
import time
import os

print("Starting data generation, ignore the following two warnings")

# Configure the number of files in the dataset
NUMBER_OF_FILES = 25
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
    "COMPRESSION_MIN": 0,
    "COMPRESSION_MAX": 0,
    "IQ_IMB_MAG_MIN": 0, 
    "IQ_IMB_MAG_MAX": 0,
    "IQ_IMB_PHA_MIN": 0, 
    "IQ_IMB_PHA_MAX": 0,        
    "OUTPUT_FILE_PATH": "./data/%s/%s/phase_noise-%s.npy"
}},
{"class_name": "normal",
 "CONFIG": {
    "PHASE_NOISE_MIN": 0,
    "PHASE_NOISE_MAX": 0,
    "PHASE_NOISE_ALPHA_MIN": 0,
    "PHASE_NOISE__ALPHA_MAX": 0,
    "NOISE_SOURCE_MIN": 0.01,
    "NOISE_SOURCE_MAX": 0.02,
    "COMPRESSION_MIN": 0,
    "COMPRESSION_MAX": 0,
    "IQ_IMB_MAG_MIN": 0, 
    "IQ_IMB_MAG_MAX": 0,
    "IQ_IMB_PHA_MIN": 0, 
    "IQ_IMB_PHA_MAX": 0,    
    "OUTPUT_FILE_PATH": "./data/%s/%s/normal-%s.npy"
}},
{"class_name": "interference",
 "CONFIG":  {
    "PHASE_NOISE_MIN": 0,
    "PHASE_NOISE_MAX": 0,
    "PHASE_NOISE_ALPHA_MIN": 0,
    "PHASE_NOISE__ALPHA_MAX": 0,
    "NOISE_SOURCE_MIN": 0.03,
    "NOISE_SOURCE_MAX": 0.04,
    "COMPRESSION_MIN": 0,
    "COMPRESSION_MAX": 0,
    "IQ_IMB_MAG_MIN": 0, 
    "IQ_IMB_MAG_MAX": 0,
    "IQ_IMB_PHA_MIN": 0, 
    "IQ_IMB_PHA_MAX": 0,    
    "OUTPUT_FILE_PATH": "./data/%s/%s/interference-%s.npy"
}},
{"class_name": "compression",
 "CONFIG":  {
    "PHASE_NOISE_MIN": 0,
    "PHASE_NOISE_MAX": 0,
    "PHASE_NOISE_ALPHA_MIN": 0,
    "PHASE_NOISE__ALPHA_MAX": 0,
    "NOISE_SOURCE_MIN": 0.001,
    "NOISE_SOURCE_MAX": 0.01,
    "COMPRESSION_MIN": 0.023,
    "COMPRESSION_MAX": 0.038,
    "IQ_IMB_MAG_MIN": 0, 
    "IQ_IMB_MAG_MAX": 0,
    "IQ_IMB_PHA_MIN": 0, 
    "IQ_IMB_PHA_MAX": 0,    
    "OUTPUT_FILE_PATH": "./data/%s/%s/compression-%s.npy"
}},
{"class_name": "iq_imbalance",
 "CONFIG":  {
    "PHASE_NOISE_MIN": 0,
    "PHASE_NOISE_MAX": 0,
    "PHASE_NOISE_ALPHA_MIN": 0,
    "PHASE_NOISE__ALPHA_MAX": 0,
    "NOISE_SOURCE_MIN": 0.01,
    "NOISE_SOURCE_MAX": 0.02,
    "COMPRESSION_MIN": 0,
    "COMPRESSION_MAX": 0,    
    "IQ_IMB_MAG_MIN": 1, 
    "IQ_IMB_MAG_MAX": 1,
    "IQ_IMB_PHA_MIN": 10, 
    "IQ_IMB_PHA_MAX": 20,
    "OUTPUT_FILE_PATH": "./data/%s/%s/iq_imbalance-%s.npy"
}}]


# Run the flowgraph on repeat
for mod in modcod:
    for i in classes:
        for j in range(0, NUMBER_OF_FILES):
            flowgraph = file_atsc_tx(mod)
            flowgraph.set_phase_noise(random.uniform(i['CONFIG']['PHASE_NOISE_MIN'], i['CONFIG']['PHASE_NOISE_MAX']))
            flowgraph.set_phase_noise_alpha(random.uniform(i['CONFIG']['PHASE_NOISE_ALPHA_MIN'], i['CONFIG']['PHASE_NOISE__ALPHA_MAX']))
            flowgraph.set_noise_source(random.uniform(i['CONFIG']['NOISE_SOURCE_MIN'], i['CONFIG']['NOISE_SOURCE_MAX']))
            flowgraph.set_compression(random.uniform(i['CONFIG']['COMPRESSION_MIN'], i['CONFIG']['COMPRESSION_MAX']))
            flowgraph.set_iq_imb_mag(random.uniform(i['CONFIG']['IQ_IMB_MAG_MIN'], i['CONFIG']['IQ_IMB_MAG_MAX']))
            flowgraph.set_iq_imb_phase(random.uniform(i['CONFIG']['IQ_IMB_PHA_MIN'], i['CONFIG']['IQ_IMB_PHA_MAX']))
            flowgraph.set_outputFile(i['CONFIG']['OUTPUT_FILE_PATH'] % (mod, i["class_name"], j)) # set output file path as ex. data/8psk/normal
            flowgraph.start()
            flowgraph.wait()

# GNU Radio makes initial empty output file, removing it
file_path = 'data/output-.txt'
if os.path.exists(file_path):
    os.remove(file_path)

print("Complete, exiting data generation")