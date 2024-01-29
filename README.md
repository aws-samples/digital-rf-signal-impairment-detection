## My Project

This repository demonstrates applying a statistical machine learning approach to detecting signal impairments in digital RF signals by examining the IQ Constellation Plot.

For background on see the following video:
https://www.youtube.com/watch?v=aQd_zBytid8

### IQ Constellation Plot

![Compression](repository_images/normal_plot.png)

### Noise Classes

The following classes are considered in this solution. Its expected that this approach can scale for additional classes but the feature engineering may need to be updated to extract additional features which are representative of each new class.

#### Compression

![Compression](repository_images/compression_plot.png)

#### Noise

![Compression](repository_images/noise_plot.png)

#### Phase Noise

![Compression](repository_images/phase_noise_plot.png)

### Generating Data

A Docker image is used to run a GNU Radio flowgraph in a headless environment. The flowgraph uses a DVB modulator to create constellation plots. Signal impairments are introduced in the flowgraph which can be randomly varied to simulate each of the previously introduced classes.

##### GNU Radio Flowgraph

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

### Training

### Inference

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
