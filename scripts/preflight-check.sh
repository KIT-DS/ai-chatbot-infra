#!/bin/bash

echo "🔍 Pre-flight checks for AI Chatbot Infrastructure"
echo ""

FAILED=0

# Check if minikube is installed
if command -v minikube &> /dev/null; then
    echo "✅ Minikube is installed"
else
    echo "❌ Minikube is NOT installed"
    FAILED=1
fi

# Check if kubectl is installed
if command -v kubectl &> /dev/null; then
    echo "✅ kubectl is installed"
else
    echo "❌ kubectl is NOT installed"
    FAILED=1
fi

# Check if minikube is running
if minikube status | grep -q "Running"; then
    echo "✅ Minikube is running"
    
    # Get minikube resources
    MEMORY=$(minikube config get memory 2>/dev/null || echo "unknown")
    CPUS=$(minikube config get cpus 2>/dev/null || echo "unknown")
    
    echo "   Memory: $MEMORY MB"
    echo "   CPUs: $CPUS"
    
    # Check if enough resources
    if [ "$MEMORY" != "unknown" ] && [ "$MEMORY" -lt 4096 ]; then
        echo "⚠️  Warning: Recommended minimum memory is 4096 MB"
    fi
else
    echo "❌ Minikube is NOT running"
    echo "   Run: minikube start --memory=4096 --cpus=2"
    FAILED=1
fi

# Check if kustomize is installed (optional)
if command -v kustomize &> /dev/null; then
    echo "✅ kustomize is installed (optional)"
else
    echo "ℹ️  kustomize is not installed (optional, kubectl has built-in kustomize)"
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo "✅ All pre-flight checks passed!"
    echo "   You can proceed with: ./scripts/deploy.sh"
else
    echo "❌ Some checks failed. Please fix the issues above."
    exit 1
fi
