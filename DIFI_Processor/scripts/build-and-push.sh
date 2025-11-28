#!/bin/bash
set -e

# Configuration
REPOSITORY_NAME="difi-processor"
REGION=${AWS_DEFAULT_REGION:-us-east-1}

echo "Building and pushing DIFI processor container..."

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create ECR repository if it doesn't exist
echo "Checking ECR repository..."
aws ecr describe-repositories --repository-names $REPOSITORY_NAME --region $REGION 2>/dev/null || \
aws ecr create-repository --repository-name $REPOSITORY_NAME --region $REGION

# Get ECR login token
echo "Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build container
echo "Building container..."
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME"
docker build --platform linux/amd64 -f docker/Dockerfile.lambda -t $ECR_URI:latest .

# Push container
echo "Pushing container..."
docker push $ECR_URI:latest

echo "Container pushed to: $ECR_URI:latest"
echo "Use this URI in your CloudFormation template"