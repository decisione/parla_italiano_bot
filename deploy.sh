#!/bin/bash

set -e  # Exit on any error

# Configuration variables
PROD_HOST="root@home.lan"
PROD_PATH="/opt/parla_italiano_bot"
TIMESTAMP=$(date +%Y%m%d_%H%M)
IMAGE_NAME="parla_italiano_bot:$TIMESTAMP"
TAR_FILE="parla_italiano_bot_$TIMESTAMP.tar"

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

# Step 1: Build the production image
echo "Building Docker image..."
docker build -f Dockerfile -t $IMAGE_NAME .

# Step 2: Save the image for deployment
echo "Saving Docker image..."
docker save -o $TAR_FILE $IMAGE_NAME

# Step 3: Verify image size
echo "Verifying image size..."
docker images $IMAGE_NAME

# Step 4: Transfer files to production server
echo "Transferring files to production server..."
scp $TAR_FILE $PROD_HOST:$PROD_PATH/
scp docker-compose.yml $PROD_HOST:$PROD_PATH/
scp .env $PROD_HOST:$PROD_PATH/

# Step 5: Deploy on production server
echo "Deploying on production server..."
# Stop the current container
ssh $PROD_HOST "cd $PROD_PATH && docker compose down"
# Load the new image
ssh $PROD_HOST "cd $PROD_PATH && docker load -i $TAR_FILE"
# Tag the image as latest
ssh $PROD_HOST "cd $PROD_PATH && docker tag $IMAGE_NAME parla_italiano_bot:latest"
# Start the new service
ssh $PROD_HOST "cd $PROD_PATH && docker compose up -d"

# Step 6: Clean up local tar file
echo "Cleaning up local tar file..."
rm $TAR_FILE

echo "Deployment complete successfully!"