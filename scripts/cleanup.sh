#!/bin/bash
set -e

echo "🧹 Cleaning up AI Chatbot Infrastructure..."

# Delete all resources
kubectl delete -f k8s/base/03-n8n.yaml --ignore-not-found=true
kubectl delete -f k8s/base/02-postgres.yaml --ignore-not-found=true
kubectl delete -f k8s/base/01-secrets.yaml --ignore-not-found=true

# Delete PVCs
kubectl delete pvc -n ai-chatbot --all --ignore-not-found=true

# Delete namespace (this will delete everything)
kubectl delete namespace ai-chatbot --ignore-not-found=true

echo "✅ Cleanup completed!"
