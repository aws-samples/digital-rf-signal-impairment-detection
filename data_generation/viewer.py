import numpy as np
import matplotlib.pyplot as plt
import os
import sys

switch = {
    "0": 'no_noise',
    "1": 'interference',
    "2": 'generator'
}
if len(sys.argv) > 1:
    arg = sys.argv[1]
else:
    print('pass a number to view, 0 = no_noise, 1 = interference, 2 = phase_noise')
    # exit()

# noise_class = switch.get(arg, 'no_noise')
noise_class = 'generator'

# print constellation to get idea of test data quality
for filename in os.listdir('./%s/data' % noise_class):
    print(filename)
    # samples = np.loadtxt("./%s/data/%s" % (noise_class, filename))
    # samples = np.load("./%s/data/%s" % (noise_class, filename), allow_pickle=True)
    samples = np.fromfile(open("./%s/data/%s" % (noise_class, filename)), dtype=np.complex64)

    real = np.real(samples)
    imag = np.imag(samples)
    X = np.concatenate([real.reshape(-1, 1), imag.reshape(-1, 1)], axis=1)
    # cluster

    # CEE

    # Classifier
    # plt.scatter(samples[:, 0], samples[:, 1], c='blue', label='Interpolated Points')
    plt.scatter(real, imag)
    plt.xlabel('Real')
    plt.ylabel('Imag')

    plt.show()