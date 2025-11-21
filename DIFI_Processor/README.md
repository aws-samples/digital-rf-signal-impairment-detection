# DIFI_Processor

A containerized solution for processing Digital Intermediate Frequency Interoperability (DIFI) standard PCAP files stored in Amazon S3. This processor extracts signal packet payloads, converts them to I/Q CSV format, and generates constellation plots for analysis with Amazon Bedrock.

## 🚧 Development Status

**ACTIVE DEVELOPMENT** - This project is currently under active development. Features and APIs may change.

## Overview

DIFI_Processor is designed to:

- Download DIFI PCAP files from Amazon S3
- Parse DIFI packets (context and data packets)
- Extract complex I/Q samples from signal payloads
- Convert samples to CSV format (I, Q columns)
- Generate constellation diagrams and plots
- Upload results back to S3 for Amazon Bedrock integration

## Architecture

```
S3 PCAP Files → DIFI_Processor Container → CSV Files + Plots → Amazon Bedrock
```

## Features

- **DIFI Standard Compliance**: Supports DIFI standard flow signal packets
- **S3 Integration**: Direct download/upload from Amazon S3
- **Flexible Processing**: Configurable packet limits and sampling rates
- **Multiple Output Formats**: CSV files and PNG constellation plots
- **Containerized**: Docker-based deployment for scalability
- **Bedrock Ready**: Outputs formatted for Amazon Bedrock analysis

## Quick Start

### Using Docker

```bash
# Build the container
docker build -f docker/Dockerfile.extract -t difi-extract .

# Extract payload from S3 PCAP (set your region)
docker run \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -v $(pwd)/output:/app/output \
  difi-extract python s3_extract_payload.py <bucket-name> <pcap-file> --max-packets 1000

# Generate constellation plots
docker run \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -v $(pwd)/output:/app/output \
  difi-extract python s3_plot_csv.py <bucket-name> results/constellation.png --directory /app/output
```

### Local Development

```bash
# Install dependencies
pip install numpy matplotlib scapy pyyaml boto3 dpkt

# Extract payload from local PCAP
python extract_payload.py sample.pcap --prefix packet --max-packets 100

# Generate constellation plots
python plot_random_csv.py --output constellation.png --num-plots 20
```

## Core Components

### Signal Processing

- `extract_payload.py` - Core DIFI packet parsing and I/Q extraction
- `s3_extract_payload.py` - S3-enabled payload extraction
- `difi_utils/` - DIFI packet classes and utilities

### Visualization

- `plot_random_csv.py` - Constellation diagram generation
- `s3_plot_csv.py` - S3-enabled plot generation and upload

### Container

- `docker/Dockerfile.extract` - Production container definition

## Usage Examples

### Extract I/Q Data from S3 PCAP

```bash
python s3_extract_payload.py <bucket-name> <pcap-file> --prefix signal_001 --max-packets 500
```

Output: `output/signal_001_000.csv`, `output/signal_001_001.csv`, etc.

### Generate Constellation Plots

```bash
python s3_plot_csv.py <bucket-name> plots/constellation.png --directory ./output --num-plots 25
```

### CSV Format

TBD

## Configuration

### Environment Variables

- `AWS_REGION` - AWS region for S3 operations
- `AWS_PROFILE` - AWS profile for authentication

### Processing Parameters

- `--max-packets` - Limit number of packets processed
- `--every-nth` - Sample every nth data point for plots
- `--num-plots` - Number of constellation plots to generate
- `--aggregate` - Files to aggregate per plot

## Amazon Bedrock Integration

Generated plots are formatted for direct ingestion into Amazon Bedrock workflows:

- PNG constellation plots for Gen AI Inference
- S3-based data pipeline integration

## Development

### Project Structure

```
DIFI_Processor/
├── README.md
├── extract_payload.py      # Core extraction logic
├── s3_extract_payload.py   # S3-enabled extraction
├── plot_random_csv.py      # Plot generation
├── s3_plot_csv.py         # S3-enabled plotting
├── drx.py                 # Signal processing utilities
├── difi_utils/            # DIFI packet parsing
│   ├── difi_data_packet_class.py
│   ├── difi_context_packet_class.py
│   └── ...
└── docker/
    └── Dockerfile.extract  # Container definition
```

### Contributing

This project is in active development. Current focus areas:

- Enhanced DIFI standard compliance
- Performance optimization for large PCAP files
- Additional visualization options
- Bedrock integration improvements

## Requirements

- Python 3.9+
- NumPy 1.26+
- Matplotlib 3.7.1+
- Scapy, PyYAML, Boto3, dpkt
- AWS credentials for S3 access

## License

[License information to be added]

## Support

For issues and questions during active development, please check the project's issue tracker.
