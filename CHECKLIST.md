# ✅ DEPLOYMENT CHECKLIST

## Pre-Deployment

- [ ] Minikube установлен (`minikube version`)
- [ ] kubectl установлен (`kubectl version`)
- [ ] Minikube запущен (`minikube status`)
- [ ] Минимум 4GB RAM для Minikube
- [ ] Минимум 20GB свободного места

## Infrastructure Deployment

- [ ] Клонирован/скачан проект `ai-chatbot-infra`
- [ ] Выполнен `./scripts/preflight-check.sh` ✅
- [ ] Выполнен `./scripts/deploy.sh` 
- [ ] Namespace `ai-chatbot` создан
- [ ] PostgreSQL pod запущен (`postgres-n8n-0`)
- [ ] n8n pod запущен
- [ ] Все поды в статусе `Running`
- [ ] Проверен статус: `./scripts/status.sh`

## n8n Setup

- [ ] Открыт n8n UI: http://$(minikube ip):30678
- [ ] Создан owner account в n8n
- [ ] Выполнен первый вход
- [ ] n8n dashboard доступен

## Optional Components

- [ ] ArgoCD установлен (optional)
  - [ ] `./scripts/install-argocd.sh`
  - [ ] Получен admin password
  - [ ] Вход в ArgoCD UI выполнен
  
- [ ] GitLab установлен (not recommended)
  - [ ] Только если необходим внутренний GitLab

## Next Steps - Agent Development

- [ ] Создан Telegram bot через @BotFather
- [ ] Получен Telegram bot token
- [ ] Настроен webhook в n8n для Telegram
- [ ] Создан Document Loader workflow
- [ ] Протестирована загрузка документов в Pinecone
- [ ] Создан Finance Agent workflow
- [ ] Создан Legal Agent workflow
- [ ] Создан Project Agent workflow
- [ ] Настроена multi-language поддержка (KZ/RU/EN)
- [ ] Добавлено цитирование источников

## Testing

- [ ] Подготовлены test cases
- [ ] Загружены тестовые документы
- [ ] Выполнены тесты Finance Agent
- [ ] Выполнены тесты Legal Agent
- [ ] Выполнены тесты Project Agent
- [ ] Достигнуто ≥85% корректных ответов
- [ ] Среднее время ответа ≤ 3 секунды

## Documentation

- [ ] README.md прочитан
- [ ] QUICKSTART.md прочитан
- [ ] DEPLOYMENT_SUMMARY.md прочитан
- [ ] Архитектура понятна
- [ ] Все команды протестированы

## Production Readiness

- [ ] Пароли изменены (secrets)
- [ ] API ключи безопасно хранятся
- [ ] Backup стратегия определена
- [ ] Мониторинг настроен (optional)
- [ ] Логирование настроено
- [ ] Resource limits проверены

## GitHub Repository

- [ ] Создан private GitHub repository
- [ ] `.gitignore` настроен (secrets исключены!)
- [ ] Code committed
- [ ] README обновлен с актуальной информацией
- [ ] ArgoCD настроен на GitHub repo (optional)

## Final Presentation

- [ ] Видео-демо записано
- [ ] Презентация подготовлена (PowerPoint/Google Slides)
- [ ] PDF версия презентации создана
- [ ] Описание архитектуры готово
- [ ] Демонстрация работающего решения готова
- [ ] Q&A ответы подготовлены

---

**Progress**: ___ / 50 tasks completed

**Status**: 
- [ ] Infrastructure Ready
- [ ] Agents Implemented
- [ ] Testing Complete
- [ ] Production Ready
- [ ] Presentation Ready
