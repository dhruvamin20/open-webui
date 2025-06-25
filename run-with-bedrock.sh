#!/bin/bash

# Run Open WebUI with AWS Bedrock Integration
# This script starts both Bedrock Access Gateway and Open WebUI

echo "Starting Open WebUI with AWS Bedrock Integration"
echo ""

# Check if .env.bedrock exists
if [ ! -f .env.bedrock ]; then
    echo "Error: .env.bedrock file not found!"
    echo ""
    echo "Please create a .env.bedrock file with your AWS credentials:"
    echo ""
    echo "AWS_ACCESS_KEY_ID=your_aws_access_key_here"
    echo "AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here"
    echo "AWS_REGION=us-east-1"
    echo "WEBUI_SECRET_KEY=your_random_secret_key_here"
    echo ""
    exit 1
fi

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

# Check if bedrock-gateway image exists
if ! docker images | grep -q "bedrock-gateway"; then
    echo "Error: bedrock-gateway image not found!"
    echo ""
    echo "Please build it first:"
    echo "1. Clone: git clone https://github.com/aws-samples/bedrock-access-gateway.git"
    echo "2. Build: cd bedrock-access-gateway/src && docker build . -f Dockerfile_ecs -t bedrock-gateway"
    echo ""
    exit 1
fi

# Check if open-webui image exists
if ! docker images | grep -q "open-webui"; then
    echo "Error: open-webui image not found!"
    echo ""
    echo "Please build it first:"
    echo "docker build -t open-webui ."
    echo ""
    exit 1
fi

# Stop any existing containers
echo "Stopping any existing containers..."
docker-compose -f docker-compose.bedrock.yaml down 2>/dev/null || true

# Start the services
echo "Starting services..."
docker-compose --env-file .env.bedrock -f docker-compose.bedrock.yaml up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to start..."
sleep 5

# Check if services are running
if docker ps | grep -q "bedrock-gateway" && docker ps | grep -q "open-webui"; then
    echo ""
    echo "Services started successfully!"
    echo ""
    echo "Open WebUI: http://localhost:3000"
    echo "Bedrock Gateway API: http://localhost:8000/docs"
    echo ""
    echo "First time setup:"
    echo "1. Create an account at http://localhost:3000"
    echo "2. AWS Bedrock models should appear automatically"
    echo ""
    echo "To stop: docker-compose -f docker-compose.bedrock.yaml down"
    echo "View logs: docker-compose -f docker-compose.bedrock.yaml logs -f"
else
    echo ""
    echo "Error: Services failed to start!"
    echo "Check logs with: docker-compose -f docker-compose.bedrock.yaml logs"
    exit 1
fi 