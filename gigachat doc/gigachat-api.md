# GigaChat API Documentation

*Справочная документация по REST API нейросетевой модели GigaChat*

**Обновлено:** 2 сентября 2025  
**Источник:** [Документация для разработчиков](https://developers.sber.ru/docs/ru/gigachat/api/reference/rest/gigachat-api)

## Содержание

- [Обзор](#обзор)
- [Получение токена доступа и авторизация](#получение-токена-доступа-и-авторизация)
- [Схемы аутентификации](#схемы-аутентификации)
- [Обращение к моделям в раннем доступе](#обращение-к-моделям-в-раннем-доступе)
- [Основные endpoints](#основные-endpoints)
- [Примеры использования](#примеры-использования)

## Обзор

GigaChat API предоставляет доступ к нейросетевой модели GigaChat через REST API. Запросы передаются по адресу `https://gigachat.devices.sberbank.ru/` и авторизуются с помощью токена доступа по протоколу OAuth 2.0.

### Ключевые особенности:
- Авторизация через OAuth 2.0
- Токен доступа действует 30 минут
- Поддержка различных типов пользователей (физ. лица, ИП, юр. лица)
- Возможность работы с моделями в раннем доступе
- Поддержка функций и хранилища файлов

### Тарифы и стоимость
Информация о стоимости и условиях использования доступна в разделе "Тарифы и оплата" на сайте разработчиков.

## Получение токена доступа и авторизация

### Базовый URL
```
https://gigachat.devices.sberbank.ru/
```

### Получение токена

Для получения токена отправьте POST запрос:

```bash
curl -L -X POST 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Accept: application/json' \
  -H 'RqUID: <идентификатор_запроса>' \
  -H 'Authorization: Basic <ключ_авторизации>' \
  --data-urlencode 'scope=GIGACHAT_API_PERS'
```

### Параметры запроса

#### Заголовки
- **RqUID** (обязательный) — уникальный идентификатор запроса в формате UUID4
- **Authorization** (обязательный) — ключ авторизации в формате Basic Auth
- **Content-Type** — `application/x-www-form-urlencoded`
- **Accept** — `application/json`

#### Тело запроса
- **scope** (обязательный) — тип доступа:
  - `GIGACHAT_API_PERS` — доступ для физических лиц
  - `GIGACHAT_API_B2B` — доступ для ИП и юридических лиц по платным пакетам
  - `GIGACHAT_API_CORP` — доступ для ИП и юридических лиц по схеме pay-as-you-go

### Ответ при успешной авторизации

```json
{
  "access_token": "eyJhbGci3iJkaXIiLCJlbmMiOiJBMTI4R0NNIiwidHlwIjoiSldUIn0..Dx7iF7cCxL8SSTKx.Uu9bPK3tPe_crdhOJqU3fmgJo_Ffvt4UsbTG6Nn0CHghuZgA4mD9qiUiSVC--okoGFkjO77W.vjYrk3T7vGM6SoxytPkDJw",
  "expires_at": 1679471442
}
```

### Использование токена

Полученный токен передается в заголовке Authorization всех последующих запросов:

```bash
curl -L -X GET 'https://gigachat.devices.sberbank.ru/api/v1/models' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <токен_доступа>'
```

### Ограничения
- Токен действует **30 минут**
- Запросы на получение токена: до **10 раз в секунду**

## Схемы аутентификации

### 1. Basic Authentication
**Используется:** для получения токена доступа

| Параметр | Значение |
|----------|----------|
| Security Scheme Type | http |
| HTTP Authorization Scheme | basic |

Ключ авторизации — строка, полученная в результате кодирования в base64 идентификатора (Client ID) и клиентского ключа (Client Secret) API.

### 2. Bearer Authentication
**Используется:** во всех запросах к GigaChat API (кроме получения токена)

| Параметр | Значение |
|----------|----------|
| Security Scheme Type | http |
| HTTP Authorization Scheme | bearer |
| Bearer format | JWT |

## Обращение к моделям в раннем доступе

Модели GigaChat регулярно обновляются и получают новые возможности (например, вызов функций). Новые версии моделей некоторое время доступны в раннем доступе.

**Особенности моделей в раннем доступе:**
- Могут отличаться от промышленных версий
- Предоставляют доступ к новейшим функциям
- Используют тот же API endpoint

## Основные endpoints

### Базовый URL API
```
https://gigachat.devices.sberbank.ru/api/v1
```

### Категории методов

#### 1. Models (Модели)
- **GET /models** — получение списка доступных моделей

#### 2. Chat Completions (Генерация ответов)
- **POST /chat/completions** — отправка запроса на генерацию

#### 3. Functions (Функции)
Методы для работы с собственными функциями:
- Описание и вызов функций
- Интеграция с AI-агентами и ассистентами

#### 4. Files Storage (Хранилище файлов)
- **POST /files** — загрузка файлов
- **GET /files** — получение списка файлов
- **GET /files/{file_id}** — получение информации о файле
- **GET /files/{file_id}/content** — скачивание файла
- **DELETE /files/{file_id}** — удаление файла

### Поддерживаемые форматы файлов

#### Текстовые документы
| Формат | MIME-тип |
|--------|-----------|
| txt | text/plain |
| doc | application/msword |
| docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document |
| pdf | application/pdf |
| epub | application/epub |
| ppt | application/ppt |
| pptx | application/pptx |

#### Изображения
| Формат | MIME-тип |
|--------|-----------|
| jpeg | image/jpeg |
| png | image/png |
| tiff | image/tiff |
| bmp | image/bmp |

#### Аудиофайлы
| Формат | MIME-тип |
|--------|-----------|
| mp4 | audio/mp4 |
| mp3 | audio/mp3 |
| m4a | audio/x-m4a |
| wav | audio/x-wav, audio/wave, audio/wav, audio/x-pn-wav |
| weba | audio/webm |
| ogg | audio/x-ogg |
| opus | audio/opus |

## Примеры использования

### 1. Получение токена доступа

```python
import requests
import uuid
import base64

# Подготовка данных
client_id = "your_client_id"
client_secret = "your_client_secret"
auth_string = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
request_id = str(uuid.uuid4())

# Запрос токена
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "RqUID": request_id,
    "Authorization": f"Basic {auth_string}"
}
data = {"scope": "GIGACHAT_API_PERS"}

response = requests.post(url, headers=headers, data=data)
token_info = response.json()
access_token = token_info["access_token"]
```

### 2. Получение списка моделей

```python
url = "https://gigachat.devices.sberbank.ru/api/v1/models"
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(url, headers=headers)
models = response.json()
print(models)
```

### 3. Отправка запроса на генерацию

```python
url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
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

response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(result)
```

### 4. Загрузка файла

```python
url = "https://gigachat.devices.sberbank.ru/api/v1/files"
headers = {
    "Authorization": f"Bearer {access_token}"
}

with open("document.pdf", "rb") as file:
    files = {"file": file}
    response = requests.post(url, headers=headers, files=files)
    
file_info = response.json()
print(f"File uploaded: {file_info}")
```

## Полезные ссылки

- [Официальная документация](https://developers.sber.ru/docs/ru/gigachat/api/reference/rest/gigachat-api)
- [Быстрый старт для физических лиц](https://developers.sber.ru/ru/gigachat/individuals-quickstart)
- [Быстрый старт для ИП и юридических лиц](https://developers.sber.ru/ru/gigachat/legal-quickstart)
- [Тарифы и оплата](https://developers.sber.ru/ru/gigachat/api/tariffs)
- [Модели GigaChat](https://developers.sber.ru/ru/gigachat/models)
- [Работа с функциями](https://developers.sber.ru/ru/gigachat/guides/functions/overview)

## Контакты

- **Email:** gigachat@sberbank.ru
- **URL:** https://developers.sber.ru/portal/products/gigachat-api

---
*Документация обновлена на основе официальных источников Sber Developers Portal*