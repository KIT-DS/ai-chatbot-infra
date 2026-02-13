#!/bin/bash

echo "📊 AI Chatbot Infrastructure Status"
echo "===================================="
echo ""

# Check namespace
echo "📦 Namespace:"
kubectl get namespace ai-chatbot 2>/dev/null || echo "❌ Namespace not found"
echo ""

# Check all resources
echo "🔧 All Resources:"
kubectl get all -n ai-chatbot 2>/dev/null || echo "❌ No resources found"
echo ""

# Check pods
echo "🐳 Pods Status:"
kubectl get pods -n ai-chatbot -o wide 2>/dev/null || echo "❌ No pods found"
echo ""

# Check PVCs
echo "💾 Persistent Volume Claims:"
kubectl get pvc -n ai-chatbot 2>/dev/null || echo "ℹ️  No PVCs found"
echo ""

# Check secrets
echo "🔐 Secrets:"
kubectl get secrets -n ai-chatbot 2>/dev/null || echo "❌ No secrets found"
echo ""

# Get service URLs
echo "🌐 Service URLs:"
MINIKUBE_IP=$(minikube ip 2>/dev/null)
if [ -n "$MINIKUBE_IP" ]; then
    echo "   n8n: http://$MINIKUBE_IP:30678"
    echo "   ArgoCD: http://$MINIKUBE_IP:30443 (if installed)"
else
    echo "   ❌ Minikube IP not available"
fi
echo ""

# Check n8n logs (last 10 lines)
echo "📝 n8n Recent Logs:"
kubectl logs deployment/n8n -n ai-chatbot --tail=10 2>/dev/null || echo "❌ n8n not running"
echo ""

# Resource usage
echo "📈 Resource Usage:"
kubectl top pods -n ai-chatbot 2>/dev/null || echo "ℹ️  Metrics not available (install metrics-server)"
echo ""

echo "===================================="
echo "💡 Useful commands:"
echo "   kubectl logs -f deployment/n8n -n ai-chatbot"
echo "   kubectl exec -it deployment/n8n -n ai-chatbot -- /bin/sh"
echo "   minikube service n8n -n ai-chatbot --url"
