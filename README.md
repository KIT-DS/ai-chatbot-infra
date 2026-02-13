# AI Chatbot Infrastructure - Minikube Deployment

Упрощенная инфраструктура для AI чатбота с тремя агентами (Finance, Legal, Project) на базе n8n, PostgreSQL, и ArgoCD.

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────┐
│              Minikube Cluster                   │
│                                                 │
│  ┌──────────────┐         ┌─────────────────┐ │
│  │   ArgoCD     │         │   ai-chatbot    │ │
│  │  (GitOps)    │────────▶│   Namespace     │ │
│  └──────────────┘         │                 │ │
│                            │  ┌───────────┐  │ │
│                            │  │    n8n    │  │ │
│                            │  │  (agents) │  │ │
│                            │  └─────┬─────┘  │ │
│                            │        │        │ │
│                            │  ┌─────▼─────┐  │ │
│                            │  │ PostgreSQL│  │ │
│                            │  └───────────┘  │ │
│                            └─────────────────┘ │
└─────────────────────────────────────────────────┘
         │                            │
         ▼                            ▼
    External                    External APIs
    (port 30443)                (OpenAI, Pinecone)
    (port 30678)
```

## 📋 Prerequisites

- Minikube установлен и запущен
- kubectl настроен
- Минимум 4GB RAM для Minikube
- Минимум 20GB свободного места

## 🚀 Quick Start

### 1. Запустить Minikube (если еще не запущен)

```bash
minikube start --memory=4096 --cpus=2
```

### 2. Развернуть основную инфраструктуру

```bash
cd ai-chatbot-infra
chmod +x scripts/*.sh
./scripts/deploy.sh
```

Это установит:
- ✅ Namespace `ai-chatbot`
- ✅ Secrets с API ключами (OpenAI, Pinecone)
- ✅ PostgreSQL StatefulSet
- ✅ n8n Deployment

### 3. (Опционально) Установить ArgoCD

```bash
./scripts/install-argocd.sh
```

### 4. Проверить статус

```bash
kubectl get all -n ai-chatbot
```

## 🌐 Доступ к сервисам

### n8n
```bash
# Получить URL
minikube service n8n -n ai-chatbot --url

# Или через NodePort
MINIKUBE_IP=$(minikube ip)
echo "n8n: http://$MINIKUBE_IP:30678"
```

### ArgoCD (если установлен)
```bash
# Получить пароль
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# URL: http://$(minikube ip):30443
# Username: admin
```

## 📁 Структура проекта

```
ai-chatbot-infra/
├── k8s/
│   ├── base/
│   │   ├── 00-namespace.yaml      # Namespace
│   │   ├── 01-secrets.yaml        # API keys
│   │   ├── 02-postgres.yaml       # PostgreSQL
│   │   └── 03-n8n.yaml           # n8n deployment
│   └── overlays/
│       └── dev/                   # Dev environment
├── argocd/                        # ArgoCD configs
├── scripts/
│   ├── deploy.sh                 # Main deployment script
│   ├── install-argocd.sh         # ArgoCD installer
│   └── cleanup.sh                # Cleanup script
└── README.md
```

## 🔧 Configuration

### Secrets (k8s/base/01-secrets.yaml)

Текущие credentials:
- **OpenAI API**: Настроен
- **Pinecone API**: Настроен (index: avc-rag, region: us-east-1)
- **PostgreSQL**: n8n/n8n_secure_password_2025
- **n8n Encryption**: Настроен

⚠️ **ВАЖНО**: Измените пароли в production!

### Resource Limits

**PostgreSQL:**
- Request: 256Mi RAM, 100m CPU
- Limit: 512Mi RAM, 500m CPU

**n8n:**
- Request: 512Mi RAM, 200m CPU
- Limit: 1Gi RAM, 1000m CPU

## 🔍 Troubleshooting

### PostgreSQL не стартует
```bash
kubectl logs -f statefulset/postgres-n8n -n ai-chatbot
kubectl describe pod -l app=postgres-n8n -n ai-chatbot
```

### n8n не подключается к БД
```bash
kubectl logs -f deployment/n8n -n ai-chatbot
# Проверить init container
kubectl logs deployment/n8n -n ai-chatbot -c wait-for-postgres
```

### Недостаточно ресурсов
```bash
# Увеличить ресурсы Minikube
minikube delete
minikube start --memory=6144 --cpus=4
```

## 🧹 Cleanup

```bash
./scripts/cleanup.sh
```

## 📊 Next Steps

После успешного деплоя инфры:

1. ✅ Зайти в n8n UI
2. ✅ Создать первый workflow
3. ✅ Настроить агентов (Finance, Legal, Project)
4. ✅ Подключить Telegram bot
5. ✅ Загрузить документы в Pinecone

## 🎯 Agents to Build

1. **Financial Agent** - бюджеты, оплаты, лимиты
2. **Legal Agent** - НПА, контракты, процедуры
3. **Project Agent** - дедлайны, статусы, риски

Каждый агент будет:
- Поддерживать 3 языка (KZ/RU/EN)
- Использовать RAG с Pinecone
- Работать с OpenAI GPT-4o-mini
- Цитировать источники

## 📚 References

- [n8n Documentation](https://docs.n8n.io/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
