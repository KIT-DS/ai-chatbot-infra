# 📦 AI CHATBOT INFRASTRUCTURE - PROJECT INDEX

## 📖 Documentation Files (Read in this order)

1. **QUICKSTART.md** - Начните отсюда! Быстрый старт за 10 минут
2. **README.md** - Полная документация проекта
3. **DEPLOYMENT_SUMMARY.md** - Обзор развернутой инфраструктуры
4. **CHECKLIST.md** - Чек-лист для отслеживания прогресса

## 🚀 Scripts (Execute in this order)

1. **scripts/preflight-check.sh** - Проверка готовности системы
2. **scripts/deploy.sh** - Основной деплой (n8n + PostgreSQL)
3. **scripts/install-argocd.sh** - Установка ArgoCD (опционально)
4. **scripts/status.sh** - Проверка статуса всех компонентов
5. **scripts/cleanup.sh** - Очистка всех ресурсов

## 📁 Kubernetes Manifests

### Base Manifests (k8s/base/)
- **00-namespace.yaml** - Namespace definition
- **01-secrets.yaml** - API keys and credentials (⚠️ DO NOT COMMIT)
- **02-postgres.yaml** - PostgreSQL StatefulSet
- **03-n8n.yaml** - n8n Deployment + Service
- **04-gitlab-optional.yaml** - Optional GitLab (not recommended)
- **kustomization.yaml** - Kustomize base config

### Overlays (k8s/overlays/dev/)
- **kustomization.yaml** - Dev environment config
- **patches.yaml** - Dev-specific patches

## 🔧 GitOps Configuration

### ArgoCD (argocd/)
- **application.yaml** - ArgoCD Application manifest

## 🎯 Quick Commands

### Deploy Infrastructure
```bash
cd ai-chatbot-infra
./scripts/preflight-check.sh  # Check prerequisites
./scripts/deploy.sh            # Deploy everything
./scripts/status.sh            # Check status
```

### Access Services
```bash
# n8n
minikube service n8n -n ai-chatbot --url
# or
echo "http://$(minikube ip):30678"

# ArgoCD (if installed)
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
echo "http://$(minikube ip):30443"
```

### Monitoring
```bash
kubectl get all -n ai-chatbot
kubectl logs -f deployment/n8n -n ai-chatbot
kubectl top pods -n ai-chatbot
```

### Cleanup
```bash
./scripts/cleanup.sh
```

## 🏗️ Project Structure

```
ai-chatbot-infra/
├── 📄 INDEX.md                    # This file
├── 📄 QUICKSTART.md               # Quick start guide
├── 📄 README.md                   # Full documentation
├── 📄 DEPLOYMENT_SUMMARY.md       # Deployment overview
├── 📄 CHECKLIST.md                # Progress checklist
├── 📄 .gitignore                  # Git ignore rules
│
├── 📂 k8s/                        # Kubernetes manifests
│   ├── 📂 base/                   # Base configurations
│   │   ├── 00-namespace.yaml
│   │   ├── 01-secrets.yaml
│   │   ├── 02-postgres.yaml
│   │   ├── 03-n8n.yaml
│   │   ├── 04-gitlab-optional.yaml
│   │   └── kustomization.yaml
│   └── 📂 overlays/               # Environment overlays
│       └── 📂 dev/
│           ├── kustomization.yaml
│           └── patches.yaml
│
├── 📂 argocd/                     # ArgoCD configs
│   └── application.yaml
│
└── 📂 scripts/                    # Automation scripts
    ├── preflight-check.sh
    ├── deploy.sh
    ├── install-argocd.sh
    ├── status.sh
    └── cleanup.sh
```

## 🔑 Important Information

### Credentials
- **PostgreSQL**: n8n / n8n_secure_password_2025
- **OpenAI API**: Stored in `openai-credentials` secret
- **Pinecone API**: Stored in `pinecone-credentials` secret
  - Index: avc-rag
  - Environment: us-east-1

### Service Endpoints
- **n8n**: http://$(minikube ip):30678
- **ArgoCD**: http://$(minikube ip):30443
- **PostgreSQL**: postgres-n8n.ai-chatbot.svc.cluster.local:5432

### Resources
- **PostgreSQL**: 256Mi-512Mi RAM, 2Gi storage
- **n8n**: 512Mi-1Gi RAM, 5Gi storage

## 🎯 Next Steps

1. ✅ Deploy infrastructure (./scripts/deploy.sh)
2. ⏭️ Access n8n UI
3. ⏭️ Create Telegram bot
4. ⏭️ Build RAG pipeline
5. ⏭️ Implement 3 agents (Finance, Legal, Project)
6. ⏭️ Test with ≥85% accuracy
7. ⏭️ Prepare presentation

## 🆘 Need Help?

- Check **QUICKSTART.md** for common issues
- Run `./scripts/status.sh` to diagnose problems
- Check logs: `kubectl logs -f deployment/n8n -n ai-chatbot`
- Port-forward if service unreachable: `kubectl port-forward svc/n8n 5678:5678 -n ai-chatbot`

---

**Version**: 1.0  
**Status**: ✅ Infrastructure Ready  
**Next**: Build AI Agents
