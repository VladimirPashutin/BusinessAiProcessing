# POST /chat/completions - Получить ответ модели на сообщения

**Источник:** [Официальная документация](https://developers.sber.ru/docs/ru/gigachat/api/reference/rest/post-chat)  
**Обновлено:** 2 сентября 2025  
**Спецификация:** [api.yml](./api.yml)

## Описание

Возвращает ответ модели, сгенерированный на основе переданных сообщений. Это основной endpoint для взаимодействия с моделями GigaChat в формате диалога, генерации текста, работы с файлами и функциями.

### Ключевые особенности:
- **Аутентификация:** Bearer Token (JWT)
- **Метод:** POST
- **Поддержка диалогов:** Многосообщенческие разговоры с сохранением контекста
- **Работа с файлами:** Поддержка текстовых документов, изображений и аудиофайлов
- **Функции:** Встроенные и пользовательские функции
- **Потоковая генерация:** Server-Sent Events (SSE)
- **Preview-модели:** Поддержка моделей в раннем доступе

## Endpoint

```http
POST https://gigachat.devices.sberbank.ru/api/v1/chat/completions
```

## Заголовки запроса

### Обязательные заголовки

| Заголовок | Тип | Описание | Пример |
|-----------|-----|----------|--------|
| `Content-Type` | string | Тип содержимого запроса | `application/json` |
| `Accept` | string | Ожидаемый формат ответа | `application/json` или `text/event-stream` |
| `Authorization` | string | Bearer токен для авторизации | `Bearer <access_token>` |

## Параметры запроса

### Обязательные параметры

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `model` | string | Название модели для генерации | `"GigaChat"`, `"GigaChat-Pro"`, `"GigaChat-Max"` |
| `messages` | array | Массив сообщений диалога | `[{"role": "user", "content": "Привет!"}]` |

### Опциональные параметры

| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|-------------|
| `temperature` | float | Температура выборки (0.0-2.0+) | Зависит от модели |
| `top_p` | float | Параметр nucleus sampling (0.0-1.0) | Зависит от модели |
| `max_tokens` | integer | Максимальное количество токенов в ответе | null |
| `repetition_penalty` | float | Штраф за повторения (рекомендуется 1.0) | Зависит от модели |
| `stream` | boolean | Потоковая генерация ответа | `false` |
| `update_interval` | number | Интервал между токенами в потоковом режиме (сек) | `0` |
| `function_call` | string/object | Режим работы с функциями | null |
| `functions` | array | Описания пользовательских функций | null |

## Структура сообщений

### Типы ролей

#### `system` - Системный промпт
- **Назначение:** Задает роль и поведение модели
- **Ограничения:** Только одно сообщение, должно быть первым в массиве
- **Пример:**
```json
{
  "role": "system",
  "content": "Ты профессиональный переводчик на английский язык."
}
```

#### `user` - Сообщение пользователя
- **Назначение:** Запросы и сообщения от пользователя
- **Пример:**
```json
{
  "role": "user",
  "content": "Переведи это предложение на английский."
}
```

#### `assistant` - Ответ модели
- **Назначение:** Ответы модели в диалоге
- **Пример:**
```json
{
  "role": "assistant",
  "content": "Конечно! Пожалуйста, укажите предложение для перевода."
}
```

#### `function` - Результат функции
- **Назначение:** Передача результатов работы пользовательских функций
- **Формат:** JSON-объект, обернутый в строку
- **Пример:**
```json
{
  "role": "function",
  "content": "{\"temperature\": \"27\", \"humidity\": \"65\"}"
}
```

## Примеры запросов

### Простой диалог

#### cURL
```bash
curl -X POST 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <ваш_access_token>' \
  -d '{
    "model": "GigaChat",
    "messages": [
      {
        "role": "user",
        "content": "Привет! Расскажи про себя"
      }
    ]
  }'
```

#### Python (requests)
```python
import requests

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {access_token}"
}

payload = {
    "model": "GigaChat",
    "messages": [
        {
            "role": "user",
            "content": "Привет! Как дела?"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    print("Ответ модели:", result['choices'][0]['message']['content'])
else:
    print(f"Ошибка: {response.status_code} - {response.text}")
```

#### Python (gigachat библиотека)
```python
from gigachat import GigaChat

giga = GigaChat(
    credentials="<ключ_авторизации>",
)

response = giga.chat("Расскажи про себя")
print(response)

# Или с более детальным контролем:
response = giga.chat(
    messages=[
        {"role": "user", "content": "Привет! Как дела?"}
    ],
    model="GigaChat-Pro",
    temperature=0.7
)
print(response.choices[0].message.content)
```

### Диалог с системным промптом

```python
payload = {
    "model": "GigaChat-Pro",
    "messages": [
        {
            "role": "system",
            "content": "Ты профессиональный программист Python. Отвечай кратко и технически точно."
        },
        {
            "role": "user",
            "content": "Как создать виртуальное окружение в Python?"
        }
    ],
    "temperature": 0.3
}
```

### Потоковая генерация (SSE)

```python
import requests
import json

def stream_chat(message, access_token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Authorization": f"Bearer {access_token}"
    }
    
    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "user", "content": message}
        ],
        "stream": True,
        "update_interval": 0.1
    }
    
    response = requests.post(url, headers=headers, json=payload, stream=True)
    
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    data_part = decoded_line[6:]  # Убираем 'data: '
                    if data_part == '[DONE]':
                        print("\n[Генерация завершена]")
                        break
                    try:
                        chunk = json.loads(data_part)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            print(content, end='', flush=True)
                    except json.JSONDecodeError:
                        continue
    else:
        print(f"Ошибка: {response.status_code}")

# Использование
stream_chat("Расскажи интересную историю", "your_access_token")
```

## Работа с файлами

### Текстовые документы

```python
# Предварительно загрузите файл в хранилище
file_response = giga.upload_file(open("document.pdf", "rb"))
file_id = file_response.id

# Используйте файл в запросе
payload = {
    "model": "GigaChat",
    "messages": [
        {
            "role": "user",
            "content": "Проанализируй содержимое документа",
            "attachments": [file_id]
        }
    ]
}
```

### Изображения

```python
# Загрузите изображение
image_response = giga.upload_file(open("image.jpg", "rb"))
image_id = image_response.id

# Используйте изображение в запросе
payload = {
    "model": "GigaChat",
    "messages": [
        {
            "role": "user",
            "content": "Опиши что изображено на картинке",
            "attachments": [image_id]
        }
    ]
}
```

### Ограничения при работе с файлами

- **Текстовые документы:** Только один файл на запрос
- **Изображения:** До 10 изображений на сессию, одно изображение на сообщение
- **Общий размер:** Менее 80 МБ для изображений и аудио
- **Контекст:** Содержимое файлов не должно превышать размер контекста модели

## Ответы

### 200 OK - Успешное выполнение

**Схема ответа (обычный режим):**

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "string"
      },
      "index": 0,
      "finish_reason": "stop"
    }
  ],
  "created": 1678878333,
  "model": "GigaChat:1.0.26.20",
  "object": "chat.completion",
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

**Описание полей ответа:**

| Поле | Тип | Описание |
|------|-----|----------|
| `choices` | array | Массив вариантов ответа модели |
| `choices[].message` | object | Сгенерированное сообщение |
| `choices[].message.role` | string | Роль автора (всегда "assistant") |
| `choices[].message.content` | string | Содержимое ответа модели |
| `choices[].finish_reason` | string | Причина завершения генерации |
| `created` | integer | Unix timestamp создания ответа |
| `model` | string | Идентификатор использованной модели |
| `usage` | object | Статистика использования токенов |

### Причины завершения (finish_reason)

| Значение | Описание |
|----------|----------|
| `stop` | Модель естественно завершила генерацию |
| `length` | Достигнут лимит токенов |
| `function_call` | Вызвана функция |
| `blacklist` | Запрос попадает под тематические ограничения |
| `error` | Ошибка в аргументах функции |

**Пример успешного ответа:**

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Привет! Я GigaChat — российская языковая модель, созданная командой Sber AI. Я умею общаться на русском языке, отвечать на вопросы, помогать с различными задачами, писать тексты и даже генерировать изображения. Чем могу помочь?"
      },
      "index": 0,
      "finish_reason": "stop"
    }
  ],
  "created": 1678878333,
  "model": "GigaChat:1.0.26.20",
  "object": "chat.completion",
  "usage": {
    "prompt_tokens": 8,
    "completion_tokens": 47,
    "total_tokens": 55
  }
}
```

### Коды ошибок

#### 400 Bad Request
- **Причина:** Некорректный формат запроса
- **Примеры:** Неверная структура JSON, отсутствуют обязательные поля

#### 401 Unauthorized
- **Причина:** Ошибка авторизации
- **Примеры:** Недействительный токен, истекший токен

#### 404 Not Found
- **Причина:** Указан неверный идентификатор модели
- **Решение:** Проверьте список доступных моделей через GET /models

#### 422 Validation Error
- **Причина:** Ошибка валидации параметров
- **Примеры:** 
  - Превышен размер контекста модели
  - Несколько системных промптов
  - Системный промпт не первый в массиве
  - Неверные значения параметров

**Пример ошибки 422:**
```json
{
  "status": 422,
  "message": "Invalid params: system message must be the first message"
}
```

#### 429 Too Many Requests
- **Причина:** Превышен лимит запросов
- **Решение:** Реализуйте exponential backoff

#### 500 Internal Server Error
- **Причина:** Внутренняя ошибка сервера
- **Решение:** Повторите запрос позже

## Работа с функциями

### Встроенные функции

```python
payload = {
    "model": "GigaChat",
    "messages": [
        {
            "role": "user",
            "content": "Создай изображение кота в космосе"
        }
    ],
    "function_call": "auto",
    "functions": [
        {
            "name": "text2image"
        }
    ]
}
```

### Пользовательские функции

```python
payload = {
    "model": "GigaChat",
    "messages": [
        {
            "role": "user",
            "content": "Какая погода в Москве?"
        }
    ],
    "function_call": "auto",
    "functions": [
        {
            "name": "get_weather",
            "description": "Получает текущую погоду для указанного города",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Название города"
                    }
                },
                "required": ["city"]
            }
        }
    ]
}
```

### Режимы работы с функциями

| Режим | Описание |
|-------|----------|
| `"auto"` | Модель автоматически решает, вызывать ли функцию |
| `"none"` | Функции не вызываются |
| `{"name": "function_name"}` | Принудительный вызов конкретной функции |

## Настройка параметров генерации

### Temperature (температура)

```python
# Детерминированная генерация
payload = {
    "model": "GigaChat",
    "messages": [{"role": "user", "content": "2+2="}],
    "temperature": 0.001
}

# Творческая генерация
payload = {
    "model": "GigaChat",
    "messages": [{"role": "user", "content": "Напиши стихотворение"}],
    "temperature": 1.0
}
```

### Ограничение длины ответа

```python
payload = {
    "model": "GigaChat",
    "messages": [{"role": "user", "content": "Кратко объясни квантовую физику"}],
    "max_tokens": 100,  # Максимум 100 токенов в ответе
    "temperature": 0.7
}
```

### Управление повторениями

```python
payload = {
    "model": "GigaChat",
    "messages": [{"role": "user", "content": "Перечисли преимущества Python"}],
    "repetition_penalty": 1.1,  # Снижаем повторения
    "temperature": 0.8
}
```

### Использование preview-моделей

```python
payload = {
    "symbolModel": "GigaChat-Pro-preview",  # Обратите внимание на суффикс -preview
    "messages": [{"role": "user", "content": "Тестируем новые возможности"}]
}
```

## Полезные ссылки

- [Официальная документация моделей GigaChat](https://developers.sber.ru/ru/gigachat/symbolModels)
- [Модели в раннем доступе](https://developers.sber.ru/ru/gigachat/symbolModels/preview-symbolModels)
- [GET /symbolModels - Получить список моделей](./get-symbolModels.md)
- [POST /oauth - Получить токен доступа](./post-token.md)
- [Работа с файлами](https://developers.sber.ru/ru/gigachat/guides/working-with-files)
- [Работа с функциями](https://developers.sber.ru/ru/gigachat/guides/functions/overview)
- [Потоковая генерация токенов](https://developers.sber.ru/ru/gigachat/guides/response-token-streaming)
- [Сохранение контекста диалога](https://developers.sber.ru/ru/gigachat/guides/keeping-context)
- [Тарифы и ограничения](https://developers.sber.ru/ru/gigachat/api/tariffs)
- [Официальная спецификация OpenAPI](https://developers.sber.ru/docs/files/openapi/gigachat/api.yml)

---
*Документация создана на основе официальной спецификации GigaChat API*