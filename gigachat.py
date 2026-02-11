from __future__ import annotations

import base64
import hashlib
import psycopg2 as ps
import re
import requests
import time
import urllib3
import uuid

import environment
from ai_interface import AiInterface

# Disable SSL warnings for GigaChat API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GigaChatAi(AiInterface):

    def __init__(self):
        self.id = 'GigaChat'
        env = environment.Environment('business-ai-service')
        self.auth_key = env.get('python.gigachat-auth-key')
        self.base_url = "https://gigachat.devices.sberbank.ru/api/v1"
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.access_token = None
        self.token_expires_at = None
        
        # Image cache: url_hash -> file_id
        self._image_cache = {}
        
        # Model tiers (high -> low performance)
        self.text_tiers = [
            "GigaChat-2-Pro",
            "GigaChat",
            "GigaChat-Max"
        ]
        
        # Vision models for image description
        self.vision_tiers = [
            "GigaChat-2-Pro",
            "GigaChat",
            "GigaChat-Max"
        ]

    # Helper to pick symbolModel by kind and tier offset (0=pro, 1=standard, 2=max)
    def _pick_model(self, kind: str, lower_tier: int) -> str:
        tiers = self.text_tiers if kind == "text" else self.vision_tiers
        index = max(0, min(lower_tier, 2))
        return tiers[index]

    def _get_auth_token(self) -> bool:
        """Get or refresh authentication token"""
        if self.access_token and self.token_expires_at:
            # Check if token is still valid (with 5-minute buffer)
            if time.time() < (self.token_expires_at / 1000 - 300):
                return True
        
        if not self.auth_key:
            print("GigaChat authentication key not configured")
            return False
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {self.auth_key}"
        }
        
        try:
            response = requests.post(
                self.auth_url,
                headers=headers,
                data={"scope": "GIGACHAT_API_PERS"},
                verify=False
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.token_expires_at = token_data.get("expires_at")
            
            return self.access_token is not None
        except Exception as e:
            print(f"GigaChat authentication failed: {e}")
            return False

    def _get_cached_image_id(self, image_url: str) -> str | None:
        """Get cached file ID for image URL"""
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        file_id = self._image_cache.get(url_hash)
        if file_id:
            print(f"Using cached image file ID: {file_id}")
        return file_id
    
    def _cache_image_id(self, image_url: str, file_id: str):
        """Cache file ID for image URL"""
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        self._image_cache[url_hash] = file_id
        print(f"Cached image file ID: {file_id} for URL hash: {url_hash[:8]}...")

    def _upload_image(self, image_data: bytes) -> str | None:
        """Upload image to GigaChat file storage and return file ID"""
        if not self._get_auth_token():
            return None
            
        headers = {
            "Authorization": f"Bearer {self.access_token}"
            # Don't set Content-Type - let requests handle multipart/form-data
        }
        
        files = {
            "file": ("image.jpg", image_data, "image/jpeg")
        }
        
        data = {
            "purpose": "general"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/files",
                headers=headers,
                files=files,
                data=data,
                verify=False
            )
            response.raise_for_status()
            
            result = response.json()
            file_id = result.get("id")
            print(f"NEW GIGACHAT FILE ID FOR TESTING: {file_id}")
            print(f"Image uploaded successfully, file ID: {file_id}")
            return file_id
            
        except Exception as e:
            print(f"Image upload failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return None
    def _chat_completion(self, messages: list, symbolModel: str, max_tokens: int = None) -> str | None:
        """Generic chat completion method"""
        print(f"provider GigaChat endpoint chat/completions called (model: {symbolModel})")
        
        if not self._get_auth_token():
            print("provider GigaChat endpoint chat/completions response failed (auth)")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": symbolModel,
            "messages": messages,
            "temperature": 0.7
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                verify=False
            )
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                print("provider GigaChat endpoint chat/completions response success")
                return result["choices"][0]["message"]["content"]
            print("provider GigaChat endpoint chat/completions response failed (no choices)")
            return None
            
        except Exception as e:
            print(f"provider GigaChat endpoint chat/completions response failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response body: {e.response.text}")
            print(f"Request data: {data}")
            return None

    def getId(self) -> str:
        return self.id

    def request_rate(self, request: str, prompt: str) -> float:
        print("provider GigaChat endpoint request_rate called")
        symbolModel = self._pick_model("text", 0)
        
        messages = [
            {"role": "system", "content": prompt},
            {
                "role": "system",
                "content": "Верните только числовое значение от 1 до 10 без дополнительных объяснений."
            },
            {"role": "user", "content": request}
        ]
        
        result = self._chat_completion(messages, symbolModel, 10)
        
        if result:
            try:
                # Extract numeric value
                match = re.search(r'\d+(?:\.\d+)?', result)
                if match:
                    rating = float(match.group())
                    print("provider GigaChat endpoint request_rate response success")
                    return max(1.0, min(10.0, rating))  # Clamp to valid range
            except:
                pass
        
        print("provider GigaChat endpoint request_rate response failed (using default)")
        return 5.0  # Default neutral rating

    def response_to_request(self, orgName: str, request: dict, prompt: str, char_limit: int, lower_tier: int = 0) -> str | None:
        print(f"provider GigaChat endpoint response_to_request called (tier: {lower_tier})")
        symbolModel = self._pick_model("text", lower_tier)
        
        messages = [
            {"role": "system", "content": prompt},
            {
                "role": "system",
                "content": f"Результирующее описание должно содержать не более {char_limit} символов"
            },
            {
                "role": "system",
                "content": f"Необходимо учесть, что компания именуется как {orgName}"
            },
            {
                "role": "user",
                "content": f"Пользователь услуг направил в компанию запрос следующего содержания: {request}"
            }
        ]
        
        result = self._chat_completion(messages, symbolModel, char_limit * 2)
        
        if result is None and lower_tier < 2:
            print(f"Retrying response_to_request with lower tier: {lower_tier + 1}")
            return self.response_to_request(orgName, request, prompt, char_limit, lower_tier + 1)
        
        if result:
            print("provider GigaChat endpoint response_to_request response success")
        else:
            print("provider GigaChat endpoint response_to_request response failed")
        
        return result

    def generate_publication(self, orgName: str, assortment: str, description: str,
                           imageDescription: str, prompt: str, char_limit: int, lower_tier: int = 0) -> str | None:
        print(f"provider GigaChat endpoint generate_publication called (tier: {lower_tier})")
        symbolModel = self._pick_model("text", lower_tier)
        
        # Format the prompt template with actual values
        formatted_prompt = prompt.format(orgName=orgName, assortment=assortment, char_limit=char_limit)
        
        # Consolidate system messages to avoid 422 errors
        system_content = f"{formatted_prompt}\n\nНеобходимо учесть, что компания именуется как {orgName}, а публикация формируется для продукта или услуги компании, называющегося {assortment}.\n\nРезультирующее описание должно содержать не более {char_limit} символов."
        
        messages = [
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": f"Компания предоставила следующее описание для продукта или услуги: {description}"
            }
        ]
        
        if imageDescription is not None:
            messages.append({
                "role": "user",
                "content": f"Публикация сопровождается изображением, описание которого сформулировано как {imageDescription}"
            })
        
        result = self._chat_completion(messages, symbolModel, char_limit * 2)
        
        if result is None and lower_tier < 2:
            print(f"Retrying generate_publication with lower tier: {lower_tier + 1}")
            return self.generate_publication(orgName, assortment, description, imageDescription, prompt, char_limit, lower_tier + 1)
        
        if result:
            print("provider GigaChat endpoint generate_publication response success")
        else:
            print("provider GigaChat endpoint generate_publication response failed")
        
        return result

    def describeImage(self, orgName: str, imageUrl: str, assortment: str,
                     prompt: str, token_limit: int, is_public_url: bool | None = None, lower_tier: int = 0,
                     file_metadata: dict = None) -> tuple[str | None, dict | None]:
        print(f"provider GigaChat endpoint describeImage called (tier: {lower_tier})")
        symbolModel = self._pick_model("vision", lower_tier)
        
        # Initialize metadata if not provided
        if file_metadata is None:
            file_metadata = {}
        
        try:
            # Check if we already have a GigaChat file ID
            existing_file_id = file_metadata.get('gigachat_file_id')
            
            if existing_file_id:
                print(f"Using existing GigaChat file ID: {existing_file_id}")
                file_id = existing_file_id
            else:
                # Download and upload image
                print(f"Downloading image from: {imageUrl}")
                response = requests.get(imageUrl, stream=True, verify=False)
                response.raise_for_status()
                image_data = response.content
                print(f"Downloaded {len(image_data)} bytes of image data")
                
                print("Uploading image to GigaChat...")
                file_id = self._upload_image(image_data)
                if not file_id:
                    print("provider GigaChat endpoint describeImage response failed (upload failed)")
                    return None, None
                
                print(f"NEW GIGACHAT FILE ID FOR TESTING: {file_id}")  # For hardcoding in tests
                
                # CRITICAL FIX: Update file_metadata immediately so retry attempts can reuse this file ID
                file_metadata['gigachat_file_id'] = file_id
            
            # Create messages with attachment - simpler format
            messages = [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"Опишите изображение для компании {orgName}, продукт {assortment}. Максимум {token_limit} символов.",
                    "attachments": [file_id]
                }
            ]
            
            print(f"Sending chat completion with file attachment: {file_id}")
            result = self._chat_completion(messages, symbolModel, token_limit * 2)
            
            if result is None and lower_tier < 2:
                print(f"Retrying describeImage with lower tier: {lower_tier + 1}")
                # Pass updated file_metadata with the file ID to retry attempts
                return self.describeImage(orgName, imageUrl, assortment, prompt, token_limit, is_public_url,
                                          lower_tier + 1, file_metadata)
            
            # Prepare metadata to return
            metadata_to_return = None
            if not existing_file_id and file_id:
                # Return new file ID for caching
                metadata_to_return = {"gigachat_file_id": file_id}
            
            if result:
                print("provider GigaChat endpoint describeImage response success")
            else:
                print("provider GigaChat endpoint describeImage response failed")
            
            return result, metadata_to_return
            
        except Exception as e:
            print(f"Error in describeImage: {e}")
            if lower_tier < 2:
                print(f"Retrying describeImage with lower tier: {lower_tier + 1}")
                # Pass updated file_metadata with the file ID to retry attempts
                return self.describeImage(orgName, imageUrl, assortment, prompt, token_limit, is_public_url,
                                          lower_tier + 1, file_metadata)
            print(f"provider GigaChat endpoint describeImage response failed: {e}")
            return None, None
