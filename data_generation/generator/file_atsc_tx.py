#!/usr/bin/env python3
from gnuradio import analog
from gnuradio import blocks
import numpy
from gnuradio import channels
from gnuradio import dtv
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import math




class file_atsc_tx(gr.top_block):

    def __init__(self):
        # gr.top_block.__init__(self, "File Atsc Tx", catch_exceptions=True)
        gr.top_block.__init__(self, "File Atsc Tx")

        ##################################################
        # Variables
        ##################################################
        self.symbol_rate = symbol_rate = 1e6
        self.phase_noise_alpha = phase_noise_alpha = 0.1
        self.phase_noise = phase_noise = 0.1
        self.outputFile = outputFile = "data/output-.txt"
        self.noise_source = noise_source = 0.01

        self.center_freq = center_freq = 2e6

        ##################################################
        # Blocks
        ##################################################

        self.dtv_dvbs2_modulator_bc_0 = dtv.dvbs2_modulator_bc(
            dtv.FECFRAME_NORMAL,
            dtv.C3_4,
            dtv.MOD_32APSK,
            dtv.INTERPOLATION_OFF)
        self.channels_phase_noise_gen_0 = channels.phase_noise_gen(phase_noise, phase_noise_alpha)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, symbol_rate,True)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, outputFile, False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_random_source_x_0 = blocks.vector_source_b(list(map(int, numpy.random.randint(0, 200, 1024))), False)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, (noise_source * 2), 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_random_source_x_0, 0), (self.dtv_dvbs2_modulator_bc_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.channels_phase_noise_gen_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.dtv_dvbs2_modulator_bc_0, 0), (self.channels_phase_noise_gen_0, 0))

    def __init__(self, blobs):
        # gr.top_block.__init__(self, "File Atsc Tx", catch_exceptions=True)
        gr.top_block.__init__(self, "File Atsc Tx")

        ##################################################
        # Variables
        ##################################################
        self.symbol_rate = symbol_rate = 1e6
        self.phase_noise_alpha = phase_noise_alpha = 0.1
        self.phase_noise = phase_noise = 0.1
        self.outputFile = outputFile = "data/output-.txt"
        self.noise_source = noise_source = 0.01

        self.center_freq = center_freq = 2e6

        ##################################################
        # Blocks
        ##################################################
        if blobs == "qpsk":
            mod = dtv.MOD_QPSK
        elif blobs == "8psk":
            mod = dtv.MOD_8PSK
        elif blobs == "16apsk":
            mod = dtv.MOD_16APSK
        elif blobs == "32apsk":
            mod = dtv.MOD_32APSK
        else:
            exit()
        self.dtv_dvbs2_modulator_bc_0 = dtv.dvbs2_modulator_bc(
            dtv.FECFRAME_NORMAL,
            dtv.C3_4,
            mod,
            dtv.INTERPOLATION_OFF)
        self.channels_phase_noise_gen_0 = channels.phase_noise_gen(phase_noise, phase_noise_alpha)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, symbol_rate,True)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, outputFile, False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_random_source_x_0 = blocks.vector_source_b(list(map(int, numpy.random.randint(0, 200, 1024))), False)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, (noise_source * 2), 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_random_source_x_0, 0), (self.dtv_dvbs2_modulator_bc_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.channels_phase_noise_gen_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.dtv_dvbs2_modulator_bc_0, 0), (self.channels_phase_noise_gen_0, 0))


    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate
        self.blocks_throttle_0.set_sample_rate(self.symbol_rate)

    def get_phase_noise_alpha(self):
        return self.phase_noise_alpha

    def set_phase_noise_alpha(self, phase_noise_alpha):
        self.phase_noise_alpha = phase_noise_alpha
        self.channels_phase_noise_gen_0.set_alpha(self.phase_noise_alpha)

    def get_phase_noise(self):
        return self.phase_noise

    def set_phase_noise(self, phase_noise):
        self.phase_noise = phase_noise
        self.channels_phase_noise_gen_0.set_noise_mag(self.phase_noise)

    def get_outputFile(self):
        return self.outputFile

    def set_outputFile(self, outputFile):
        self.outputFile = outputFile
        self.blocks_file_sink_0.open(self.outputFile)

    def get_noise_source(self):
        return self.noise_source

    def set_noise_source(self, noise_source):
        self.noise_source = noise_source
        self.analog_noise_source_x_0.set_amplitude((self.noise_source * 2))

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq


def main(top_block_cls=file_atsc_tx, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
