#!/bin/bash

# GigaChat API Test Script
# This script tests your GigaChat credentials by:
# 1. Getting an authentication token
# 2. Fetching available models
# 3. Sending a test chat message

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_PATH="${CONFIG_PATH:-$ROOT_DIR/application_dev.yaml}"

if [ ! -f "$CONFIG_PATH" ]; then
    echo -e "${RED}Error: config file not found: $CONFIG_PATH${NC}"
    exit 1
fi

AUTH_KEY=$(grep -E "^[[:space:]]*gigachat-auth-key:" "$CONFIG_PATH" | head -1 | sed -E 's/^[^:]+:[[:space:]]*//; s/^"//; s/"$//')
if [ -z "$AUTH_KEY" ]; then
    echo -e "${RED}Error: gigachat-auth-key not found in $CONFIG_PATH${NC}"
    exit 1
fi

BASE_URL="https://gigachat.devices.sberbank.ru/api/v1"
AUTH_URL="https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== GigaChat API Test Script ===${NC}"
echo
echo "Authorization key (first 20 chars): ${AUTH_KEY:0:20}..."

# Step 1: Get authentication token
echo -e "${YELLOW}Step 1: Getting authentication token...${NC}"

# Generate UUID for RqUID
RQUID=$(uuidgen)

TOKEN_RESPONSE=$(curl -s -k -w "\n%{http_code}" \
  -X POST "$AUTH_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "RqUID: $RQUID" \
  -H "Authorization: Basic $AUTH_KEY" \
  -d "scope=GIGACHAT_API_PERS")

# Extract HTTP status code and response body
HTTP_CODE=$(echo "$TOKEN_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$TOKEN_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Authentication successful${NC}"
    ACCESS_TOKEN=$(echo "$RESPONSE_BODY" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "Access token received (first 20 chars): ${ACCESS_TOKEN:0:20}..."
    echo
else
    echo -e "${RED}✗ Authentication failed (HTTP $HTTP_CODE)${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi

# Step 2: Get available models
echo -e "${YELLOW}Step 2: Getting available models...${NC}"

MODELS_RESPONSE=$(curl -s -k -w "\n%{http_code}" \
  -X GET "$BASE_URL/models" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

# Extract HTTP status code and response body
HTTP_CODE=$(echo "$MODELS_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$MODELS_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Models retrieved successfully${NC}"
    echo "Available models:"
    echo "$RESPONSE_BODY" | python3 -m json.tool | grep '"id"' | head -5
    
    # Extract first model ID for chat test
    FIRST_MODEL=$(echo "$RESPONSE_BODY" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    echo "Using model for chat test: $FIRST_MODEL"
    echo
else
    echo -e "${RED}✗ Failed to get models (HTTP $HTTP_CODE)${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi

# Step 3: Send a test chat message
echo -e "${YELLOW}Step 3: Sending test chat message...${NC}"

CHAT_REQUEST='{
  "model": "'$FIRST_MODEL'",
  "messages": [
    {
      "role": "user",
      "content": "Привет! Как дела?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 100
}'

CHAT_RESPONSE=$(curl -s -k -w "\n%{http_code}" \
  -X POST "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$CHAT_REQUEST")

# Extract HTTP status code and response body
HTTP_CODE=$(echo "$CHAT_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$CHAT_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Chat message sent successfully${NC}"
    echo "Model response:"
    echo "$RESPONSE_BODY" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('  Message:', data['choices'][0]['message']['content'])
    print('  Tokens used:', data['usage']['total_tokens'])
except Exception as e:
    print('Error parsing response:', e)
    "
    echo
else
    echo -e "${RED}✗ Failed to send chat message (HTTP $HTTP_CODE)${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi

echo -e "${GREEN}=== All tests completed successfully! ===${NC}"
echo -e "${BLUE}Your GigaChat credentials are working correctly.${NC}"
