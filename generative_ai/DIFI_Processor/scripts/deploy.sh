#!/bin/bash
set -e

# Configuration
STACK_NAME="difi-processor"
REGION=${AWS_DEFAULT_REGION:-us-east-1}
REPOSITORY_NAME="difi-processor"
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
    PcapBucketName="$DIFI_RAW_BUCKET" \
    ResultsBucketName="$DIFI_RESULTS_BUCKET" \
  --capabilities CAPABILITY_IAM \
  --region $REGION

echo ""
echo "Deployment complete!"
echo "PCAP Bucket: $DIFI_RAW_BUCKET"
echo "Results Bucket: $DIFI_RESULTS_BUCKET"
echo ""
echo "To test, upload a .pcap file to: s3://$DIFI_RAW_BUCKET/"
echo "Results will appear in: s3://$DIFI_RESULTS_BUCKET/"

