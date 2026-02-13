import os
from openai import OpenAI

# Вставь сюда свой ключ (или убедись, что он в переменных окружения)
client = OpenAI(api_key="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")

try:
    # Запрос списка доступных моделей
    models = client.models.list()
    
    print("✅ Соединение успешно! Доступные модели:")
    # Выводим первые 10 моделей для проверки
    for model in list(models.data)[:]:
        print(f"- {model.id}")

    # Попробуем сделать тестовый запрос самой дешевой моделью
    print("--- Тестовый чат ---")
    completion = client.chat.completions.create(
        model="gpt-4o-mini", # или "gpt-4o"
        messages=[{"role": "user", "content": "Say 'API is working'"}],
        max_tokens=10
    )
    print(f"Ответ модели: {completion.choices[0].message.content}")

except Exception as e:
    print(f"❌ Ошибка: {e}")