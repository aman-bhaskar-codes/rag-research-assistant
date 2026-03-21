#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="rag-backend"
IMAGE="gcr.io/$PROJECT_ID/rag-backend:latest"

gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
