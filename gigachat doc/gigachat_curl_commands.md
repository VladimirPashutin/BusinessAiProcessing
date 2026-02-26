# GigaChat API Testing with cURL Commands

This document provides individual curl commands to test your GigaChat API credentials step by step.

## Prerequisites

Replace the following placeholders with your actual credentials:
- `YOUR_CLIENT_ID` - Your GigaChat client ID
- `YOUR_CLIENT_SECRET` - Your GigaChat client secret

## Step 1: Get Authentication Token

```bash
# Set your credentials
CLIENT_ID="YOUR_CLIENT_ID"
CLIENT_SECRET="YOUR_CLIENT_SECRET"

# Create base64 encoded credentials
CREDENTIALS=$(echo -n "$CLIENT_ID:$CLIENT_SECRET" | base64)

# Generate UUID for RqUID (optional but recommended)
RQUID=$(uuidgen)

# Get authentication token
curl -X POST "https://ngw.devices.sberbank.ru:9443/api/v2/oauth" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "RqUID: $RQUID" \
  -H "Authorization: Basic $CREDENTIALS" \
  -d "scope=GIGACHAT_API_PERS"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": 1640995200
}
```

## Step 2: Get Available Models

```bash
# Use the access token from Step 1
ACCESS_TOKEN="YOUR_ACCESS_TOKEN_FROM_STEP_1"

curl -X GET "https://gigachat.devices.sberbank.ru/api/v1/models" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "GigaChat",
      "object": "model",
      "owned_by": "salutedevices"
    },
    {
      "id": "GigaChat-Pro",
      "object": "model",
      "owned_by": "salutedevices"
    }
  ]
}
```

## Step 3: Send Chat Message

```bash
# Use the access token from Step 1 and a model ID from Step 2
ACCESS_TOKEN="YOUR_ACCESS_TOKEN_FROM_STEP_1"
MODEL_ID="GigaChat"  # or another symbolModel from the list

curl -X POST "https://gigachat.devices.sberbank.ru/api/v1/chat/completions" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbolModel": "'$MODEL_ID'",
    "messages": [
      {
        "role": "user",
        "content": "Привет! Как дела?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

**Expected Response:**
```json
{
  "choices": [
    {
      "message": {
        "content": "Привет! У меня всё отлично, спасибо за вопрос! Как у тебя дела?",
        "role": "assistant"
      },
      "index": 0,
      "finish_reason": "stop"
    }
  ],
  "created": 1640995200,
  "symbolModel": "GigaChat",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 15,
    "prompt_tokens": 8,
    "total_tokens": 23
  }
}
```

## One-liner Test Command

For quick testing, you can combine all steps in one command:

```bash
# Set your credentials first
export CLIENT_ID="YOUR_CLIENT_ID"
export CLIENT_SECRET="YOUR_CLIENT_SECRET"

# One-liner to test everything
CREDENTIALS=$(echo -n "$CLIENT_ID:$CLIENT_SECRET" | base64) && \
ACCESS_TOKEN=$(curl -s -X POST "https://ngw.devices.sberbank.ru:9443/api/v2/oauth" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "Authorization: Basic $CREDENTIALS" \
  -d "scope=GIGACHAT_API_PERS" | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4) && \
echo "Token: ${ACCESS_TOKEN:0:20}..." && \
curl -X POST "https://gigachat.devices.sberbank.ru/api/v1/chat/completions" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbolModel":"GigaChat","messages":[{"role":"user","content":"Тест API"}],"max_tokens":50}'
```

## Troubleshooting

### Common Error Codes:

- **401 Unauthorized**: Invalid credentials or expired token
- **403 Forbidden**: Insufficient permissions or wrong scope
- **422 Unprocessable Entity**: Invalid request parameters
- **429 Too Many Requests**: Rate limit exceeded (10 requests/second)
- **500 Internal Server Error**: Server-side issue

### Tips:

1. **Token expires in 30 minutes** - You'll need to get a new token if it expires
2. **Rate limiting**: Maximum 10 requests per second
3. **Scope**: Use `GIGACHAT_API_PERS` for personal use, `GIGACHAT_API_B2B` for business
4. **Base64 encoding**: Make sure there are no newlines in your base64 encoded credentials

### Debug Commands:

Check if your base64 encoding is correct:
```bash
echo -n "$CLIENT_ID:$CLIENT_SECRET" | base64 | base64 -d
```

Verbose curl for debugging:
```bash
curl -v -X POST "https://ngw.devices.sberbank.ru:9443/api/v2/oauth" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "Authorization: Basic $CREDENTIALS" \
  -d "scope=GIGACHAT_API_PERS"
```