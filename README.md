## Detecting digital RF signal impairments in IQ Constellation plots

This repository demonstrates applying a combination of statistical methods and machine learning to detect signal impairments in digital RF signals. The solution relies on processing data in an IQ Constellation diagram. For background on digital RF signal impairments, see the following [video](https://www.youtube.com/watch?v=aQd_zBytid8). The goal of this repository is to demonstrate using a software approach rather than more traditional hardware solutions. Another consideration of this solution is using methods which can scale the number of blobs in the modulation and coding scheme, for example QPSK to 32APSK. Lastly, the solution should be performant in terms of compute footprint to enable low cost analysis and edge deployment.

### IQ Constellation Impairment Classes

The following impairment classes are considered in this solution. Its expected that the feature engineering process of this solution can be extended to scale for additional impairment classes such as in-band spurs and imbalance.

<!-- Row 1 -->
<div align="center">
  <!-- Image 1 with Title -->
  <figure style="display:inline-block;">
    <img src="repository_images/normal_plot.png" width="200" alt="Image 1">
    <figcaption>Normal</figcaption>
  </figure>
  <!-- Image 2 with Title -->
  <figure style="display:inline-block; margin-left:20px;">
    <img src="repository_images/noise_plot.png" width="200" alt="Image 2">
    <figcaption>Wideband Noise</figcaption>
  </figure>
</div>
<!-- Row 2 -->
<div align="center" style="margin-top:20px;">
  <!-- Image 3 with Title -->
  <figure style="display:inline-block;">
    <img src="repository_images/phase_noise_plot.png" width="200" alt="Image 3">
    <figcaption>Phase Noise</figcaption>
  </figure>
  <!-- Image 4 with Title -->
  <figure style="display:inline-block; margin-left:20px;">
    <img src="repository_images/compression_plot.png" width="200" alt="Image 4">
    <figcaption>Compression</figcaption>
  </figure>
</div>

### Environment Setup

The following steps will utilize a [SageMaker Notebook](https://aws.amazon.com/sagemaker/notebooks/) as it provides a single interface for us to both run [Jupyter Notebook](https://jupyter.org/) files and build [Docker Containers](https://www.docker.com/resources/what-container/).

We create a Notebook Instance with the following settings.
![Notebook](repository_images/notebook_setup.png)

Once the infrastructure is provisioned, we can **Open Jupyter**.

### Generating Data

Given the solution relies on statistics and machine learning, we need to generate data to train on. For this task, we'll look to [GNURadio](https://www.gnuradio.org/)
A Docker image is used to run a GNU Radio flowgraph in a headless environment. The flowgraph uses a DVB-S2X modulator to create constellation plots and save to a file. Signal error is introduced in the flowgraph which can be randomly varied to simulate each of the impairment classes. We use this flowgraph to generate a large number of samples for each of the impairment classes. Those samples will train a Classification Machine Learning model to determine whether an impairment is present in future IQ Constellation plots.

The following flowgraph is used to generate data. Normal, Phase Noise, and Interference impairment classes are generated using GNU Radio.

![Flowgraph](repository_images/flowgraph.png)

Compression was not achieved using the flowgraph and is suggested as future work. Compression was generated using a mathematical approach for QPSK only, see generator/compression-generator.py.

##### Creating the GNURadio Docker Image

Within the Jupyter environment, first open a terminal with **New -> Terminal**.

Navigate to the SageMaker directory and clone this repository

```
cd SageMaker
git clone https://github.com/aws-samples/digital-rf-signal-impairment-detection.git
```

Navigate to the docker_build directory and build the container

```
cd digital-rf-signal-impairment-detection/data_generation/docker_build
docker build . -t gnuradio-image
```

##### Running Scripts

First create the directory structure to store the training data. Run the following commands from the root of this directory.

```
cd data_generation/generator
./create_folders.sh
cd ../..
```

Enter the docker container with the following

```
docker run -it --rm -v $PWD/data_generation:/temp/data gnuradio-image
```

Now, within the container, run the following

```
cd /temp/data/generator
python generator.py
for i in {1..100}; do python compression-generator.py; done
```

We can exit the container. We now have training data located at
_digital-rf-signal-impairment-detection/data_generation/generator/data_

```
exit
```

### Preprocessing

The approach for solving impairment classification first relies on feature engineering using a statistical approach. If we consider the following constellation plot, we note 32 blobs which represent 32APSK modulation and coding. We first apply [K-Means Clustering](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html) to find each of the blobs within the data sample. Its assumed we know the number of blobs ahead of time, although a future enhancement is to design without this assumption. Given each blob, we apply the Covariance Error Ellipse which tells us the [eccentricity](<https://en.wikipedia.org/wiki/Eccentricity_(mathematics)>). Further, the density, rotation, and ratio of major/minor axis of the ellipse can be extracted as features and recorded into a tabular data format.
![IQ Plot](repository_images/raw_iq_data.png)
We can see the result of applying K-Means Clustering, Covariance Error Ellipse, and solving for metrics like density, rotation, and ratio of major to minor axis. Note, color coding of the individual blobs, ellipse boundaries, and color coded major and minor ellipse axes.
![Metric Extraction](repository_images/feature_extraction.png)

### Training

We use the [Autogluon](https://auto.gluon.ai/) library to train a tabular classifier on the features which have been extracted during the preprocessing step. Autogluon will train multiple models based on the training data. As output, we're provided with metrics describing model performance. Autogluon will automatically use the model with the highest performance and lowest inference latency.
![Autogluon](repository_images/autogluon.png)

### Inference

We can load the Autogluon model and run inference on sample IQ Constellation plots in the _inference/_ folder.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
