# POST /oauth - Получить токен доступа

**Источник:** [Официальная документация](https://developers.sber.ru/docs/ru/gigachat/api/reference/rest/post-token)  
**Обновлено:** 2 сентября 2025  
**Спецификация:** [api.yml](./api.yml)

## Описание

Возвращает токен доступа для авторизации запросов к GigaChat API. Этот endpoint является основным способом получения JWT токена, необходимого для работы с API.

### Ключевые особенности:
- **Срок действия токена:** 30 минут
- **Лимит запросов:** до 10 раз в секунду
- **Аутентификация:** Basic Auth с использованием ключа авторизации
- **Формат токена:** JWT (JSON Web Token)

## Endpoint

```http
POST https://ngw.devices.sberbank.ru:9443/api/v2/oauth
```

## Заголовки запроса

### Обязательные заголовки

| Заголовок | Тип | Описание | Пример |
|-----------|-----|----------|--------|
| `Content-Type` | string | Тип содержимого | `application/x-www-form-urlencoded` |
| `Accept` | string | Ожидаемый формат ответа | `application/json` |
| `Authorization` | string | Ключ авторизации в формате Basic Auth | `Basic <base64_encoded_key>` |
| `RqUID` | string | Уникальный идентификатор запроса (UUID4) | `6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e` |

### Подробности о заголовках

#### RqUID (Request ID)
- **Формат:** UUID4
- **Назначение:** Параметр для журналирования входящих вызовов и разбора инцидентов
- **Генерация:** Используйте стандартные библиотеки для генерации UUID
- **Паттерн:** `([0-9a-fA-F-]){36}`

#### Authorization
- **Тип:** Basic Authentication
- **Формат:** `Basic <base64_encoded_credentials>`
- **Содержимое:** Base64 кодировка строки `client_id:client_secret`
- **Получение:** Из личного кабинета при создании проекта GigaChat API

## Тело запроса

### Формат
```
Content-Type: application/x-www-form-urlencoded
```

### Параметры

| Параметр | Тип | Обязательный | Описание | Возможные значения |
|----------|-----|--------------|----------|-----------------|
| `scope` | string | ✅ | Версия API и тип доступа | `GIGACHAT_API_PERS`, `GIGACHAT_API_B2B`, `GIGACHAT_API_CORP` |

### Типы доступа (scope)

#### `GIGACHAT_API_PERS`
- **Тип пользователя:** Физические лица
- **Описание:** Доступ для индивидуальных пользователей
- **Тарификация:** Бесплатные лимиты + платные опции

#### `GIGACHAT_API_B2B`
- **Тип пользователя:** ИП и юридические лица
- **Описание:** Доступ по платным пакетам
- **Тарификация:** Предоплаченные пакеты токенов

#### `GIGACHAT_API_CORP`
- **Тип пользователя:** ИП и юридические лица
- **Описание:** Доступ по схеме pay-as-you-go
- **Тарификация:** Оплата по факту использования

## Примеры запросов

### cURL

```bash
curl -L -X POST 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Accept: application/json' \
  -H 'RqUID: 6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e' \
  -H 'Authorization: Basic <ваш_ключ_авторизации>' \
  --data-urlencode 'scope=GIGACHAT_API_PERS'
```

### Python (requests)

```python
import requests
import uuid
import base64

# Подготовка данных
client_id = "your_client_id"
client_secret = "your_client_secret"
auth_string = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
request_id = str(uuid.uuid4())

# Заголовки
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "RqUID": request_id,
    "Authorization": f"Basic {auth_string}"
}

# Тело запроса
data = {
    "scope": "GIGACHAT_API_PERS"
}

# Отправка запроса
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
response = requests.post(url, headers=headers, data=data)

# Обработка ответа
if response.status_code == 200:
    token_info = response.json()
    access_token = token_info["access_token"]
    expires_at = token_info["expires_at"]
    print(f"Токен получен: {access_token[:50]}...")
    print(f"Истекает: {expires_at}")
else:
    print(f"Ошибка: {response.status_code} - {response.text}")
```

### Python (gigachat библиотека)

```python
"""
Установите библиотеку gigachat с помощью менеджера пакетов pip:

pip install gigachat
"""
from gigachat import GigaChat

giga = GigaChat(
    credentials="<ключ_авторизации>",
)

response = giga.get_token()
print(response)
```

### JavaScript (fetch)

```javascript
const crypto = require('crypto');

// Генерация UUID4
function generateUUID4() {
    return crypto.randomUUID();
}

// Кодирование в Base64
function encodeBase64(str) {
    return Buffer.from(str).toString('base64');
}

async function getToken() {
    const clientId = "your_client_id";
    const clientSecret = "your_client_secret";
    const authString = encodeBase64(`${clientId}:${clientSecret}`);
    const requestId = generateUUID4();

    const url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth";
    
    const headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": requestId,
        "Authorization": `Basic ${authString}`
    };

    const body = new URLSearchParams({
        scope: "GIGACHAT_API_PERS"
    });

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: headers,
            body: body
        });

        if (response.ok) {
            const tokenInfo = await response.json();
            console.log("Токен получен:", tokenInfo.access_token.substring(0, 50) + "...");
            console.log("Истекает:", new Date(tokenInfo.expires_at));
            return tokenInfo;
        } else {
            const error = await response.text();
            console.error(`Ошибка ${response.status}:`, error);
        }
    } catch (error) {
        console.error("Ошибка запроса:", error);
    }
}

getToken();
```

## Ответы

### 200 OK - Успешный ответ

**Схема ответа:**

```json
{
  "access_token": "string",
  "expires_at": "integer"
}
```

**Описание полей:**

| Поле | Тип | Описание | Пример |
|------|-----|----------|--------|
| `access_token` | string | JWT токен для авторизации запросов | `eyJhbGci3iJkaXIiLCJlbmMiOiJBMTI4R0NNIi...` |
| `expires_at` | integer | Дата и время истечения токена в миллисекундах (Unix timestamp) | `1739784663483` |

**Пример успешного ответа:**

```json
{
  "access_token": "eyJhbGci3iJkaXIiLCJlbmMiOiJBMTI4R0NNIiwidHlwIjoiSldUIn0..Dx7iF7cCxL8SSTKx.Uu9bPK3tPe_crdhOJqU3fmgJo_Ffvt4UsbTG6Nn0CHghuZgA4mD9qiUiSVC--okoGFkjO77W.vjYrk3T7vGM6SoxytPkDJw",
  "expires_at": 1739784663483
}
```

### 400 Bad Request - Некорректный формат запроса

**Причины возникновения:**
- Неправильный формат тела запроса
- Отсутствуют обязательные параметры
- Неверный Content-Type
- Некорректное значение scope

**Пример ошибки:**
```json
{
  "error": "invalid_request",
  "error_description": "Missing required parameter: scope"
}
```

### 401 Unauthorized - Ошибка авторизации

**Схема ответа:**

```json
{
  "code": "integer",
  "message": "string"
}
```

**Причины возникновения:**
- Неверный ключ авторизации
- Неправильное кодирование Base64
- Недействительные Client ID или Client Secret
- Неправильный формат заголовка Authorization

**Пример ошибки:**
```json
{
  "code": 6,
  "message": "credentials doesn't match db data"
}
```

## Использование полученного токена

После получения токена используйте его во всех запросах к GigaChat API:

```bash
curl -X GET 'https://gigachat.devices.sberbank.ru/api/v1/models' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer <полученный_access_token>'
```

```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

## Управление токенами

### Проверка времени жизни токена

```python
import time

def is_token_valid(expires_at):
    """Проверяет, действителен ли токен"""
    current_time = int(time.time() * 1000)  # Текущее время в миллисекундах
    return current_time < expires_at

def time_until_expiry(expires_at):
    """Возвращает время до истечения токена в секундах"""
    current_time = int(time.time() * 1000)
    return max(0, (expires_at - current_time) / 1000)

# Использование
if is_token_valid(expires_at):
    remaining_time = time_until_expiry(expires_at)
    print(f"Токен действителен еще {remaining_time:.0f} секунд")
else:
    print("Токен истек, необходимо получить новый")
```

### Автоматическое обновление токена

```python
class GigaChatTokenManager:
    def __init__(self, client_id, client_secret, scope="GIGACHAT_API_PERS"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.access_token = None
        self.expires_at = None
        
    def get_valid_token(self):
        """Возвращает действительный токен, обновляя его при необходимости"""
        if not self.is_token_valid():
            self.refresh_token()
        return self.access_token
    
    def is_token_valid(self):
        """Проверяет действительность текущего токена"""
        if not self.access_token or not self.expires_at:
            return False
        current_time = int(time.time() * 1000)
        # Обновляем токен за 5 минут до истечения
        return current_time < (self.expires_at - 300000)
    
    def refresh_token(self):
        """Получает новый токен"""
        # Реализация запроса на получение токена
        # (код из примера выше)
        pass
```

## Ключ авторизации

### Что такое ключ авторизации

Ключ авторизации (Authorization key) — это строка, полученная в результате кодирования в Base64 клиентского идентификатора (Client ID) и ключа (Client Secret) API.

### Получение ключа авторизации

1. **Из личного кабинета** (рекомендуется):
   - Войдите в личный кабинет разработчика
   - Создайте проект GigaChat API
   - Скопируйте готовый ключ авторизации

2. **Самостоятельное кодирование**:
   ```python
   import base64
   
   client_id = "your_client_id"
   client_secret = "your_client_secret"
   
   # Создание строки credentials
   credentials = f"{client_id}:{client_secret}"
   
   # Кодирование в Base64
   auth_key = base64.b64encode(credentials.encode()).decode()
   print(f"Authorization: Basic {auth_key}")
   ```

### Безопасность

⚠️ **Важные рекомендации по безопасности:**

1. **Не храните ключи в коде** - используйте переменные окружения
2. **Ограничьте доступ** - храните ключи в безопасном месте
3. **Ротация ключей** - периодически обновляйте ключи авторизации
4. **Мониторинг** - отслеживайте использование API

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Безопасное получение ключей из переменных окружения
client_id = os.getenv('GIGACHAT_CLIENT_ID')
client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
```

## Лимиты и ограничения

| Параметр | Значение | Описание |
|----------|----------|----------|
| Время жизни токена | 30 минут | После истечения необходимо получить новый токен |
| Лимит запросов | 10 запросов/сек | Максимальная частота запросов на получение токена |
| Формат токена | JWT | JSON Web Token стандарт |
| Кодировка ключа | Base64 | Стандартное кодирование для Basic Auth |

## Устранение неполадок

### Частые ошибки

1. **"credentials doesn't match db data"**
   - Проверьте правильность Client ID и Client Secret
   - Убедитесь в корректности Base64 кодирования
   - Проверьте формат заголовка Authorization

2. **"Missing required parameter: scope"**
   - Убедитесь, что параметр scope передается в теле запроса
   - Проверьте Content-Type: application/x-www-form-urlencoded

3. **"Invalid UUID format"**
   - Проверьте формат RqUID (должен быть UUID4)
   - Используйте стандартные библиотеки для генерации UUID

4. **429 Too Many Requests**
   - Уменьшите частоту запросов (максимум 10/сек)
   - Реализуйте экспоненциальную задержку при повторных попытках

### Отладка

```python
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_token_request():
    logger.debug(f"Client ID: {client_id[:10]}...")
    logger.debug(f"Request ID: {request_id}")
    logger.debug(f"Scope: {scope}")
    logger.debug(f"Auth header: Basic {auth_string[:20]}...")
```

## Полезные ссылки

- [Быстрый старт для физических лиц](https://developers.sber.ru/ru/gigachat/individuals-quickstart)
- [Быстрый старт для ИП и юридических лиц](https://developers.sber.ru/ru/gigachat/legal-quickstart)
- [Получение авторизационных данных (физ. лица)](https://developers.sber.ru/ru/gigachat/quickstart/ind-using-api#poluchenie-avtorizatsionnyh-dannyh)
- [Получение авторизационных данных (ИП/юр. лица)](https://developers.sber.ru/ru/gigachat/quickstart/legal-using-api#poluchenie-avtorizatsionnyh-dannyh)
- [Тарифы и оплата](https://developers.sber.ru/ru/gigachat/api/tariffs)
- [Официальная спецификация OpenAPI](https://developers.sber.ru/docs/files/openapi/gigachat/api.yml)

---
*Документация создана на основе официальной спецификации GigaChat API*