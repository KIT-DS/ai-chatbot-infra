# 🚀 QUICK START GUIDE

## Шаг 1: Проверка Minikube

```bash
minikube status
# Если не запущен:
minikube start --memory=4096 --cpus=2
```

## Шаг 2: Деплой инфраструктуры

```bash
cd ai-chatbot-infra
./scripts/deploy.sh
```

Это установит:
- ✅ Namespace `ai-chatbot`
- ✅ PostgreSQL для n8n
- ✅ n8n с агентами

## Шаг 3: Проверка статуса

```bash
# Проверить поды
kubectl get pods -n ai-chatbot

# Должно быть:
# postgres-n8n-0    1/1     Running
# n8n-xxx-xxx       1/1     Running
```

## Шаг 4: Доступ к n8n

```bash
# Получить URL
minikube service n8n -n ai-chatbot --url

# Или через NodePort
echo "http://$(minikube ip):30678"
```

## Шаг 5: Первый вход в n8n

1. Открыть URL из предыдущего шага
2. Создать аккаунт владельца
3. Войти в n8n

## Шаг 6: (Опционально) ArgoCD

```bash
./scripts/install-argocd.sh

# Получить пароль
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d

# URL: http://$(minikube ip):30443
```

## 🎯 Следующие шаги

После успешного деплоя:
1. ✅ Настроить агентов в n8n
2. ✅ Подключить Telegram bot
3. ✅ Загрузить документы в Pinecone
4. ✅ Тестировать RAG pipeline

## 🆘 Troubleshooting

### Проблема: Pod не стартует
```bash
kubectl describe pod <pod-name> -n ai-chatbot
kubectl logs <pod-name> -n ai-chatbot
```

### Проблема: Нет доступа к сервису
```bash
# Port-forward напрямую
kubectl port-forward svc/n8n 5678:5678 -n ai-chatbot
# Теперь доступен на http://localhost:5678
```

### Проблема: Недостаточно ресурсов
```bash
# Перезапустить с большими ресурсами
minikube delete
minikube start --memory=6144 --cpus=4
./scripts/deploy.sh
```

## 🧹 Cleanup

```bash
./scripts/cleanup.sh
```

---

**Время установки:** ~5-10 минут  
**Требования:** 4GB RAM, 20GB disk, 2 CPU cores
