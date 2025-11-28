#!/bin/bash
set -e

# Configuration
STACK_NAME="difi-processor"
REGION=${AWS_DEFAULT_REGION:-us-east-1}
REPOSITORY_NAME="difi-processor"
PCAP_BUCKET_NAME="difi-raw"
RESULTS_BUCKET_NAME="difi-constellations"

echo "Deploying DIFI processor infrastructure..."

# Get AWS account ID and construct ECR URI
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:latest"

# Deploy CloudFormation stack
echo "Deploying CloudFormation stack: $STACK_NAME"
aws cloudformation deploy \
  --template-file infrastructure/difi-lambda-infrastructure.yaml \
  --stack-name $STACK_NAME \
  --parameter-overrides \
    ContainerImageURI="$ECR_URI" \
    PcapBucketName="$PCAP_BUCKET_NAME" \
    ResultsBucketName="$RESULTS_BUCKET_NAME" \
  --capabilities CAPABILITY_IAM \
  --region $REGION

echo ""
echo "Deployment complete!"
echo "PCAP Bucket: $PCAP_BUCKET_NAME"
echo "Results Bucket: $RESULTS_BUCKET_NAME"
echo ""
echo "To test, upload a .pcap file to: s3://$PCAP_BUCKET_NAME/"
echo "Results will appear in: s3://$RESULTS_BUCKET_NAME/"

