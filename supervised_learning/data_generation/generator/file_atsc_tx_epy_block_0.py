"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr

class amplifier_with_noise(gr.sync_block):
    def __init__(self, gain=1.0, noise_level=0.1):
        gr.sync_block.__init__(self,
            name="Amplifier with Noise",
            in_sig=[np.complex64],
            out_sig=[np.complex64])
        self.gain = gain
        self.noise_level = noise_level

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        
        # Generate gain noise
        gain_noise = np.random.normal(0, self.noise_level, len(in0))
        
        # Apply noisy gain
        out[:] = in0 * (self.gain + gain_noise)
        return len(out)
