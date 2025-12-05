# DIFI_Processor

A serverless AWS Lambda solution that processes Digital Intermediate Frequency Interoperability (DIFI) standard PCAP files from S3 and generates constellation plots for AI inference with Amazon Bedrock. This containerized Lambda function provides independent, scalable processing without impacting other compute resources.

## 🚧 Development Status

**ACTIVE DEVELOPMENT** - This project is currently under active development. Features and APIs may change.

## Overview

DIFI_Processor enables AI-driven analysis of DIFI data through:

- **Serverless Processing**: AWS Lambda automatically processes PCAP files uploaded to S3
- **Independent Compute**: Isolated processing that doesn't impact other system performance
- **AI-Ready Outputs**: Generates constellation plots optimized for Amazon Bedrock inference
- **Event-Driven**: Automatically triggered by S3 uploads for seamless workflow
- **Scalable**: Lambda scales automatically based on processing demand

## Architecture

```
S3 PCAP Upload → Lambda Trigger → Containerized Processing → Constellation Plots → Amazon Bedrock AI
```

**Key Benefits:**

- **Serverless Simplicity**: No infrastructure management required
- **Cost Effective**: Pay only for processing time used
- **Performance Isolation**: Independent processing preserves system resources
- **AI Integration**: Direct pipeline to Amazon Bedrock for intelligent analysis

## Features

- **Serverless Lambda**: Event-driven processing with automatic scaling
- **AI-Focused**: Optimized constellation plots for Amazon Bedrock inference
- **Performance Isolation**: Independent processing preserves main system resources
- **DIFI Compliance**: Full support for DIFI standard signal packets
- **Automated Pipeline**: S3 upload triggers immediate processing
- **Container-Based**: Consistent execution environment across deployments

## Quick Start

### Deploy to AWS

**Prerequisites:**

1. Set your AWS region: `export AWS_DEFAULT_REGION=us-east-1`
2. Create S3 buckets:
   ```bash
   aws s3 mb s3://your-project-raw
   aws s3 mb s3://your-project-results
   ```
3. Update bucket names in `scripts/deploy.sh`:
   ```bash
   PCAP_BUCKET_NAME="your-project-raw"
   RESULTS_BUCKET_NAME="your-project-results"
   ```
   
**Deploy:**

```bash
# Navigate to DIFI_Processor directory
cd DIFI_Processor

# Build and push container to ECR
./scripts/build-and-push.sh

# Deploy Lambda infrastructure
./scripts/deploy.sh
```

This will:

1. Build the Docker container and push to Amazon ECR
2. Deploy a Lambda function that automatically processes PCAP files uploaded to S3
3. Generate constellation plots and save them to the results bucket

**Add a Lambda trigger:**

Attach a trigger to invoke the Lambda function when a new pcap is added to the source (raw) S3 bucket: -
<img width="800" alt="Screenshot 2025-12-05 101538" src="https://github.com/user-attachments/assets/5faf8d04-d89c-441b-8657-1a5bbb9b0e2c" />

**Test:**

Upload a pcap file to your source bucket either programmatically or via the AWS console. 

Validate that the Lambda has been invoked by clicking on the Lambda function `Monitor` tab. You should see the invocations count increase each time a new pcap is uploaded.

Navigate to S3 in the console. You should see 1 or more IQ constellation png files in the `RESULTS_BUCKET_NAME` -> `results` folder

### Local Processing (Alternative)

For local development and testing, you can run the code natively.

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

## Amazon Bedrock AI Integration

This solution creates an automated pipeline for AI analysis of DIFI data:

- **Constellation Plots**: Generated specifically for visual AI inference
- **Automated Workflow**: S3 → Lambda → Bedrock pipeline
- **AI Insights**: Apply generative AI insights to signal analysis without training of machine learning models
- **Performance Benefits**: Independent Lambda processing preserves main system resources
- **Scalable Analysis**: Process multiple PCAP files simultaneously

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
    └── Dockerfile.lambda  # Container definition
```

### Contributing

This project focuses on serverless AI-driven DIFI analysis. Current development areas:

- Enhanced Amazon Bedrock integration patterns
- Optimized constellation plot generation for AI inference
- Advanced Lambda performance tuning
- Additional AI-ready visualization formats

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
