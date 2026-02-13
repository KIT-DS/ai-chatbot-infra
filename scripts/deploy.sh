#!/bin/bash
set -e

echo "🚀 Deploying AI Chatbot Infrastructure to Minikube..."
echo ""

# Check if minikube is running
if ! minikube status | grep -q "Running"; then
    echo "❌ Minikube is not running. Please start it with: minikube start"
    exit 1
fi

echo "✅ Minikube is running"
echo ""

# Apply manifests in order
echo "📦 Creating namespace..."
kubectl apply -f k8s/base/00-namespace.yaml

echo "🔐 Creating secrets..."
kubectl apply -f k8s/base/01-secrets.yaml

echo "🐘 Deploying PostgreSQL..."
kubectl apply -f k8s/base/02-postgres.yaml

echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres-n8n -n ai-chatbot --timeout=300s

echo "🤖 Deploying n8n..."
kubectl apply -f k8s/base/03-n8n.yaml

echo "⏳ Waiting for n8n to be ready..."
kubectl wait --for=condition=available deployment/n8n -n ai-chatbot --timeout=300s

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Current status:"
kubectl get pods -n ai-chatbot
echo ""

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

echo "🌐 Access n8n at:"
echo "   http://$MINIKUBE_IP:30678"
echo "   or use: minikube service n8n -n ai-chatbot --url"
echo ""
echo "💡 Useful commands:"
echo "   kubectl get all -n ai-chatbot"
echo "   kubectl logs -f deployment/n8n -n ai-chatbot"
echo "   kubectl exec -it deployment/n8n -n ai-chatbot -- /bin/sh"
echo ""
