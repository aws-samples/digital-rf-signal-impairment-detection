# Digital RF Signal Impairment Detection

This repository demonstrates two approaches for detecting signal impairments in digital RF signals by analyzing IQ constellation diagrams. Both solution paths identify impairments such as phase noise, interference, compression, and IQ imbalance across modulation schemes including QPSK, 8PSK, 16APSK, and 32APSK.

For background on digital RF signal impairments, see this [video](https://www.youtube.com/watch?v=aQd_zBytid8).

## Solution Paths

### 📊 [Solution Path 1: Supervised Learning](./supervised_learning/)

Uses statistical feature engineering and machine learning to classify impairments. IQ constellation data is processed through K-Means clustering and covariance error ellipse analysis to extract features, which train a multi-class classifier using [AutoGluon](https://auto.gluon.ai/) on [Amazon SageMaker AI](https://aws.amazon.com/sagemaker-ai/).

```
IQ Data → K-Means Clustering → Ellipse Feature Extraction → AutoGluon Training → Classifier → S3 Alerts
```

### 🧠 [Solution Path 2: Generative AI](./generative_ai/)

Uses Amazon Bedrock's multimodal AI capabilities to analyze constellation plot images directly, without model training. A serverless pipeline processes DIFI standard PCAP files into constellation diagrams, which are analyzed by a Bedrock Agent using Claude Sonnet 4.5 with few-shot prompting and RAG.

```
PCAP Files → DIFI_Processor (Lambda) → Constellation Diagrams → Bedrock Agent (Claude) → AI Analysis
```

## Comparison of Approaches

| Aspect | Supervised Learning | Generative AI |
| --- | --- | --- |
| **Setup Time** | Hours/Days (requires training) | Minutes (no training) |
| **Data Requirements** | Large labeled datasets | Few examples (few-shot) |
| **Expertise Needed** | ML/Data science expertise | Basic AWS knowledge |
| **Output Type** | Statistical classification labels | Natural language insights & recommendations |
| **Scalability** | Requires retraining for new classes | Immediate via prompt modifications |
| **Explainability** | Feature importance metrics | Contextual natural language explanations |
| **Infrastructure** | SageMaker notebooks | AWS Lambda + Amazon Bedrock |
| **Data Source** | Generated IQ data (GNU Radio) | DIFI standard PCAP files |
| **Impairment Classes** | Phase noise, interference, compression, IQ imbalance, normal | Phase noise, interference, compression, normal |
| **Modulation Support** | QPSK, 8PSK, 16APSK, 32APSK | QPSK, 8PSK, 16APSK, 32APSK |

## When to Use Each Approach

### Choose Supervised Learning when:
- You need deterministic, repeatable classification results
- You have access to large labeled training datasets
- Low-latency edge deployment is a priority
- You need fine-grained control over classification thresholds

### Choose Generative AI when:
- You need rapid deployment without training infrastructure
- Natural language explanations of impairments are valuable
- You want to analyze new impairment types without retraining
- You're processing DIFI standard PCAP files from satellite or RF systems

## IQ Constellation Impairment Classes

Both solution paths detect impairments visible in IQ constellation diagrams:

|   ![](supervised_learning/repository_images/normal_plot.png)    |    ![](supervised_learning/repository_images/noise_plot.png)    |
| :-----------------------------------------: | :-----------------------------------------: |
|                Ideal - 16QAM                |               Noise (low SNR)               |
| ![](supervised_learning/repository_images/phase_noise_plot.png) | ![](supervised_learning/repository_images/compression_plot.png) |
|                 Phase Noise                 |     Compression (amplitude gain noise)      |

## Repository Structure

```
digital-rf-signal-impairment-detection/
├── README.md                    # This file
├── supervised_learning/         # Solution Path 1: ML-based classification
│   ├── README.md
│   ├── notebooks/               # SageMaker notebooks (preprocess, train, infer)
│   ├── data_generation/         # GNU Radio synthetic data generation
│   └── repository_images/       # Documentation images
├── generative_ai/               # Solution Path 2: Bedrock-based analysis
│   ├── README.md
│   ├── DIFI_Processor/          # Serverless PCAP → constellation pipeline
│   └── Bedrock_Insights/        # Bedrock Agent + Lambda + Streamlit UI
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
└── LICENSE
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.
