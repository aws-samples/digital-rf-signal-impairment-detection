## Detecting digital RF signal impairments in IQ Constellation plots

This repository demonstrates applying a statistical machine learning approach to detecting signal impairments in digital RF signals by examining the IQ Constellation Plot. For background on see the following [video](https://www.youtube.com/watch?v=aQd_zBytid8).

### IQ Constellation Impairment Classes

The following impairment classes are considered in this solution. Its expected that the feature engineering process of this solution can be extended to scale for additional impairment classes.

#### Noise

![Noise](repository_images/noise_plot.png)

#### Phase Noise

![Phase Noise](repository_images/phase_noise_plot.png)

#### Compression

![Compression](repository_images/compression_plot.png)

### Generating Data

A Docker image is used to run a GNU Radio flowgraph in a headless environment. The flowgraph uses a DVB-S2X modulator to create constellation plots. Signal error is introduced in the flowgraph which can be randomly varied to simulate each of the impairment classes. We use this section to generate a large number of samples for each of the impairment classes. Those samples will train a Classification Machine Learning model to determine whether an impairment is present in future IQ Constellation plots.

##### GNU Radio Flowgraph

The following flowgraph is used to generate data. Normal, Phase Noise, and Interference impairment classes are generated using GNU Radio. Compression was not achieved using the flowgraph and is suggested as future work. Compression was generated using a mathematical approach for QPSK only, see generator/compression-generator.py.

![Flowgraph](repository_images/flowgraph.png)

##### Docker Image

Perform the following command in data_generation/docker_build

```
docker build . -t gnuradio-image
```

##### Running Scripts

First create the directory structure by running the following from the root of this directory

```
cd data_generation/generator
./create_folders.sh
cd ../..
```

```
docker run -it --rm -v data_generation:/temp/data 49fff3e13027 /bin/bash -c "cd /temp/data/generator; python generator.py"
```

Next create data for the compression class by running

```
for i in {1..100}; do python compression-generator.py; done
```

### Preprocessing

The approach for solving impairment classification first relies on feature engineering using a statistical approach. If we consider the following constellation plot, we note 32 blobs which represent 32APSK modulation and coding. We first cluster the samples to find each of the blobs. At each blob, we apply the covariance error ellipse which tells us the eccentricity. Further, the density, rotation, and ratio of major/minor axis of the ellipse can be extracted as features to give insight to whether an impairment class is present in the IQ Constellation plot.
![IQ Plot](repository_images/raw_iq_data.png)
We can see the result of applying the covariance error ellipse and solving for metrics like density, rotation, and ratio of major to minor axis.
![Metric Extraction](repository_images/feature_extraction.png)

### Training

We use the [Autogluon](https://auto.gluon.ai/) library to train a tabular classifier on the features which have been extracted during the preprocessing step. Autogluon will train multiple models based on the training data.

### Inference

We can load the Autogluon model and run inference on sample IQ Constellation plots in the inference/ folder.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
