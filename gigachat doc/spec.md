# GigaChat Provider Implementation Specification

## Overview

Implement GigaChat as a new AI model provider following the existing Mistral pattern. Keep it simple and reuse existing database schema.

## Architecture

### Current System
- [`AiInterface`](file:///Users/airm1/work/businessaiprocessing/ai_interface.py) - Base interface with 5 methods
- [`MistralAi`](file:///Users/airm1/work/businessaiprocessing/mistral.py) - Reference implementation
- [`getProvider(providerType)`](file:///Users/airm1/work/businessaiprocessing/businessAiProcessing.py#L37-L40) - Factory pattern
- Provider type `0` = Mistral, `1` = GigaChat (integer values)

### Implementation Rules

#### 1. File Structure
- **Create:** `gigachat.py` - Main provider class (following mistral.py pattern)
- **Update:** `businessAiProcessing.py` - Add provider type `1`
- **Update:** `application_dev.yaml` - Add credentials only

#### 2. GigaChat Provider Class
```
class GigaChatAi(AiInterface):
```

**Required Methods:**
- `getId()` → return "GigaChat"
- `request_rate()` → numeric rating 1-10
- `response_to_request()` → customer service response
- `generate_publication()` → marketing content
- `describeImage()` → image description

**Authentication:**
- Use environment variables only (no file reading)
- Token caching with 30-minute expiration
- Simple retry on auth failure

**Model Selection:**
- Text: `["GigaChat-Pro", "GigaChat", "GigaChat-Max"]`
- Vision: Same models (GigaChat supports images)
- Tier fallback: try next model on failure

#### 3. Configuration

**Environment Variables:**
```
GIGACHAT_AUTH_KEY=your_authorization_key
```

**Application YAML:**
```yaml
python:
  # Only credentials, no provider selection
  mistral-key: "your_mistral_key"
  gigachat-auth-key: "your_authorization_key"
```

**Provider Selection Logic:**
- Provider determined by `prompts.ai_provider` column in database
- `ai_plans` table links organization to specific prompts
- `getPrompt()` returns the provider type from database
- No default provider in application config

#### 4. Provider Factory Updates

**businessAiProcessing.py:**
- `getProvider(1)` → return `GigaChatAi()`
- `getProviderName(1)` → return "GigaChat"
- Provider selection comes from database via `getPrompt()` function
- Fallback to provider `0` (Mistral) when no prompt found

#### 5. Database Schema

**Keep current schema unchanged:**
- `prompts.ai_provider` uses integer values (0=mistral, 1=gigachat)
- `ai_plans` table links organizations to specific prompts
- `cust_requests.ai_provider` logs which provider was actually used
- Provider selection happens dynamically from database, not config
- Default fallback to provider `0` when no prompt found

**Database Updates Required:**

1. **Update prompts table constraint** to allow GigaChat provider:
```sql
-- Allow both Mistral (0) and GigaChat (1) providers
ALTER TABLE business_ai.prompts 
DROP CONSTRAINT IF EXISTS prompts_ai_provider_check;

ALTER TABLE business_ai.prompts 
ADD CONSTRAINT prompts_ai_provider_check 
CHECK (ai_provider BETWEEN 0 AND 1);
```

2. **Set 'Технологии третьего тысячелетия' to use GigaChat by default:**
```sql
-- Create GigaChat prompts for all prompt types (0=image, 1=publication, 2=review, 3=rate)
INSERT INTO business_ai.prompts(id, ai_provider, kind, fcontent) VALUES
(gen_random_uuid(), 1, 0, 'Ваша задача - проанализировать изображение и создать подробное описание...'),
(gen_random_uuid(), 1, 1, 'Вы — автор текстов. Напишите привлекательную публикацию...'),
(gen_random_uuid(), 1, 2, 'Вы представитель компании. Отвечайте на отзывы клиентов...'),
(gen_random_uuid(), 1, 3, 'Ваша задача - оценить по 10-бальной шкале эмоциональную окраску...');

-- Create AI plans that use GigaChat prompts
INSERT INTO business_ai.ai_plans(fname, prompt_id) 
SELECT 'gigachat-plan-' || kind, id 
FROM business_ai.prompts 
WHERE ai_provider = 1;

-- Link 'Технологии третьего тысячелетия' organization to GigaChat plans
INSERT INTO business_ai.org_ai_plans(org_id, plan_name)
SELECT o.id, ap.fname
FROM business_ai.organization o, business_ai.ai_plans ap
WHERE o.strictname = 'Технологии третьего тысячелетия'
AND ap.fname LIKE 'gigachat-plan-%';
```

#### 6. API Integration

**Endpoints:**
- Auth: `https://ngw.devices.sberbank.ru:9443/api/v2/oauth`
- API: `https://gigachat.devices.sberbank.ru/api/v1`

**Request Format:**
- Same message structure as Mistral
- Standard OpenAI-compatible chat completions
- Image support via base64 encoding

**SSL Handling:**
- Use `verify=False` for now
- Add `urllib3.disable_warnings()` to suppress warnings

#### 7. Implementation Pattern

**Follow Mistral structure exactly:**
- Same tier system with `lower_tier` parameter
- Same error handling pattern (print and return None)
- Same message building approach
- Same capacity exceeded logic

**Key Differences:**
- Authentication: OAuth2 with Bearer token vs API key
- Models: GigaChat model names vs Mistral symbolModel names
- Rate limits: 10 req/sec vs Mistral limits

## Implementation Steps

### Phase 1: Core Setup
1. Create `gigachat.py` with basic structure
2. Implement authentication method
3. Add to provider factory
4. Test basic connectivity

### Phase 2: Interface Methods
1. Implement `generate_publication()` first (main use case)
2. Add `response_to_request()`
3. Add `describeImage()` with image handling
4. Add `request_rate()` with numeric parsing

### Phase 3: Integration
1. Update configuration files
2. Test with existing prompts
3. Validate tier fallback works
4. Deploy and monitor

## Success Criteria

1. **Drop-in replacement** - Works with existing prompts and database
2. **Configuration driven** - Easy to switch providers via YAML
3. **Same behavior** - Identical output quality and format
4. **Reliable** - Basic retry and fallback mechanisms

## Notes

- **No new dependencies** - Use existing `requests`
- **No schema changes** - Reuse current database structure
- **No complex error handling** - Keep it simple for v1
- **No monitoring** - Use existing logging patterns
- **Environment first** - No file-based configuration