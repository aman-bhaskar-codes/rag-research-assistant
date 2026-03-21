#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
IMAGE_NAME="rag-backend"
IMAGE_TAG="latest"

docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG
