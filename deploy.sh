#!/bin/bash

set -e  # Exit on any error

# Configuration variables
PROD_HOST="root@home.lan"
PROD_PATH="/opt/parla_italiano_bot"
IMAGE_NAME="parla_italiano_bot:latest"
TAR_FILE="parla_italiano_bot.tar"

# Pre-deployment checks
if [ ! -f ".env" ]; then
    echo "Error: .env file not found in the current directory. Please ensure it exists with your bot token."
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    echo "Error: docker-compose.yml file not found in the current directory."
    exit 1
fi

if [ ! -f "Dockerfile" ]; then
    echo "Error: Dockerfile not found in the current directory."
    exit 1
fi

echo "Starting deployment process..."

echo "-- Step 1: Building Docker image..."
docker build -f Dockerfile -t $IMAGE_NAME .

echo "-- Step 2: Saving Docker image..."
docker save -o $TAR_FILE $IMAGE_NAME

echo "-- Step 3: Verifying image size..."
docker images $IMAGE_NAME

echo "-- Step 4: Transferring files to production server..."
scp $TAR_FILE $PROD_HOST:$PROD_PATH/
scp docker-compose.yml $PROD_HOST:$PROD_PATH/
scp .env $PROD_HOST:$PROD_PATH/

echo "-- Step 5: Deploying on production server..."
# Stop the current container
ssh $PROD_HOST "cd $PROD_PATH && docker compose down"
# Load the new image
ssh $PROD_HOST "cd $PROD_PATH && docker load -i $TAR_FILE"
# Start the new service
ssh $PROD_HOST "cd $PROD_PATH && docker compose up -d"

echo "-- Step 6: Cleaning up remote tar file..."
ssh $PROD_HOST "cd $PROD_PATH && rm $TAR_FILE"

echo "-- Step 7: Cleaning up local tar file..."
rm $TAR_FILE

echo "Deployment complete successfully!"