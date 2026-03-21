#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
IMAGE_NAME="rag-backend"
IMAGE_TAG="latest"

docker build -t gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG -f infra/docker/backend/Dockerfile .
