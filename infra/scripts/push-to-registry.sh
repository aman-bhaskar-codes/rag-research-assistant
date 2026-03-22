#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# RAG Research Assistant — Push Backend Image to Google Artifact Registry
# ──────────────────────────────────────────────────────────────────────────────
# Usage:
#   1. Run: gcloud auth login
#   2. Run: ./infra/scripts/push-to-registry.sh
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

REGION="asia-south1"
REPO_NAME="rag-backend-repo"
IMAGE_NAME="rag-backend"
TAG="latest"

echo "──────────────────────────────────────────────"
echo "🚀 RAG Backend → Artifact Registry Push Script"
echo "──────────────────────────────────────────────"

# 1. Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
    echo "❌ No GCP project set. Run:"
    echo "   gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi
echo "✅ Project: $PROJECT_ID"

# 2. Enable required services
echo "📦 Enabling required GCP services..."
gcloud services enable artifactregistry.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
echo "✅ Services enabled"

# 3. Create Artifact Registry repo (if not exists)
echo "📦 Creating Artifact Registry repo..."
gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="RAG backend Docker images" \
    --quiet 2>/dev/null || echo "   (repo already exists — skipping)"
echo "✅ Repo ready: $REPO_NAME"

# 4. Configure Docker auth
echo "🔑 Configuring Docker authentication..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
echo "✅ Docker auth configured"

# 5. Build full registry path
REGISTRY_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${TAG}"
echo "🏷️  Target: $REGISTRY_PATH"

# 6. Tag the image
echo "🏷️  Tagging image..."
docker tag "$IMAGE_NAME" "$REGISTRY_PATH"
echo "✅ Image tagged"

# 7. Push
echo "📤 Pushing image to Artifact Registry..."
docker push "$REGISTRY_PATH"
echo ""
echo "══════════════════════════════════════════════"
echo "✅ SUCCESS — Image pushed to Artifact Registry"
echo "══════════════════════════════════════════════"
echo ""
echo "📍 Image: $REGISTRY_PATH"
echo "🔗 Console: https://console.cloud.google.com/artifacts/docker/${PROJECT_ID}/${REGION}/${REPO_NAME}"
echo ""
echo "Next step: Deploy to Cloud Run with:"
echo "   gcloud run deploy rag-backend \\"
echo "     --image $REGISTRY_PATH \\"
echo "     --region $REGION \\"
echo "     --allow-unauthenticated"
