#!/usr/bin/env python3
"""
GigaChat API Testing Script

This script tests your GigaChat credentials by:
1. Getting an authentication token
2. Fetching available models
3. Sending a test chat message

Usage:
    python test_gigachat.py

Set your credentials as environment variables:
    export GIGACHAT_CLIENT_ID="your_client_id"
    export GIGACHAT_CLIENT_SECRET="your_client_secret"

Or modify the CLIENT_ID and CLIENT_SECRET variables in this script.
"""

import base64
import os
import sys
import uuid
from typing import Optional, Dict, Any

import requests
# Disable SSL warnings for GigaChat API
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GigaChatTester:
    def __init__(self, client_id: str, client_secret: str, auth_key: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_key = auth_key  # Pre-encoded authorization key
        self.base_url = "https://gigachat.devices.sberbank.ru/api/v1"
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.access_token: Optional[str] = None
        
    def get_auth_token(self, scope: str = "GIGACHAT_API_PERS") -> bool:
        """Get authentication token from GigaChat API."""
        print("🔐 Getting authentication token...")
        
        # Use pre-encoded auth key if available, otherwise encode credentials
        if self.auth_key:
            credentials = self.auth_key
            print("📝 Using pre-encoded authorization key")
        else:
            credentials = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            print("📝 Encoding credentials for authorization")
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {credentials}"
        }
        
        data = {"scope": scope}
        
        try:
            response = requests.post(self.auth_url, headers=headers, data=data, verify=False)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            
            if self.access_token:
                print(f"✅ Authentication successful! Token: {self.access_token[:20]}...")
                return True
            else:
                print("❌ No access token in response")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Authentication failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return False
    
    def get_models(self) -> Optional[Dict[str, Any]]:
        """Get list of available models."""
        print("\n📋 Getting available models...")
        
        if not self.access_token:
            print("❌ No access token. Please authenticate first.")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{self.base_url}/models", headers=headers, verify=False)
            response.raise_for_status()
            
            models_data = response.json()
            print("✅ Models retrieved successfully!")
            
            if "data" in models_data:
                print("Available models:")
                for model in models_data["data"][:5]:  # Show first 5 symbolModels
                    print(f"  - {symbolModel.get('id', 'Unknown')}")
                    
            return models_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get symbolModels: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def send_chat_message(self, message: str, symbolModel: str = "GigaChat") -> Optional[Dict[str, Any]]:
        """Send a chat message to the symbolModel."""
        print(f"\n💬 Sending chat message to {symbolModel}...")
        
        if not self.access_token:
            print("❌ No access token. Please authenticate first.")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "symbolModel": symbolModel,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions", 
                headers=headers, 
                json=data,
                verify=False
            )
            response.raise_for_status()
            
            chat_data = response.json()
            print("✅ Chat message sent successfully!")
            
            if "choices" in chat_data and len(chat_data["choices"]) > 0:
                message_content = chat_data["choices"][0]["message"]["content"]
                print(f"🤖 Model response: {message_content}")
                
                if "usage" in chat_data:
                    usage = chat_data["usage"]
                    print(f"📊 Tokens used: {usage.get('total_tokens', 'Unknown')}")
            
            return chat_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send chat message: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def run_full_test(self) -> bool:
        """Run the complete test suite."""
        print("🚀 Starting GigaChat API test suite...\n")
        
        # Step 1: Authentication
        if not self.get_auth_token():
            return False
        
        # Step 2: Get symbolModels
        models_data = self.get_models()
        if not models_data:
            return False
        
        # Step 3: Send chat message
        # Try to use the first available symbolModel, fallback to "GigaChat"
        model_to_use = "GigaChat"
        if "data" in models_data and len(models_data["data"]) > 0:
            model_to_use = models_data["data"][0].get("id", "GigaChat")
        
        chat_result = self.send_chat_message("Привет! Как дела?", model_to_use)
        if not chat_result:
            return False
        
        print("\n🎉 All tests completed successfully!")
        print("✅ Your GigaChat credentials are working correctly.")
        return True


def load_credentials_from_file(file_path: str = "GigaChatApi.txt") -> tuple[Optional[str], Optional[str]]:
    """Load credentials from GigaChatApi.txt file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        client_id = None
        auth_key = None
        
        for line in content.strip().split('\n'):
            if line.startswith('Client ID:'):
                client_id = line.split(':', 1)[1].strip()
            elif line.startswith('Authorization Key:'):
                auth_key = line.split(':', 1)[1].strip()
                
        return client_id, auth_key
        
    except FileNotFoundError:
        print(f"❌ Credentials file '{file_path}' not found")
        return None, None
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return None, None


def main():
    """Main function to run the GigaChat tests."""
    # Try to load credentials from file first
    client_id, auth_key = load_credentials_from_file()
    
    if client_id and auth_key:
        print(f"📄 Loaded credentials from GigaChatApi.txt")
        print(f"   Client ID: {client_id}")
        print(f"   Auth Key: {auth_key[:20]}...")
        
        # Decode the authorization key to get client_secret
        try:
            decoded = base64.b64decode(auth_key).decode()
            if ':' in decoded:
                _, client_secret = decoded.split(':', 1)
            else:
                print("❌ Invalid authorization key format")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error decoding authorization key: {e}")
            sys.exit(1)
    else:
        # Fallback to environment variables
        client_id = os.getenv("GIGACHAT_CLIENT_ID")
        client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
        
        # If not found in environment, use hardcoded values (replace these!)
        if not client_id or not client_secret:
            client_id = "YOUR_CLIENT_ID_HERE"
            client_secret = "YOUR_CLIENT_SECRET_HERE"
            
            if client_id == "YOUR_CLIENT_ID_HERE" or client_secret == "YOUR_CLIENT_SECRET_HERE":
                print("❌ Error: Please set your credentials!")
                print("\nOption 1 - Create GigaChatApi.txt file with:")
                print("Client ID: your_client_id")
                print("Scope: GIGACHAT_API_PERS")
                print("Authorization Key: your_base64_encoded_key")
                print("\nOption 2 - Environment variables:")
                print("export GIGACHAT_CLIENT_ID='your_client_id'")
                print("export GIGACHAT_CLIENT_SECRET='your_client_secret'")
                print("\nOption 3 - Edit this script:")
                print("Replace YOUR_CLIENT_ID_HERE and YOUR_CLIENT_SECRET_HERE with your actual credentials")
                sys.exit(1)
    
    # Create tester instance and run tests
    if 'auth_key' in locals():
        # Use the pre-encoded authorization key from file
        tester = GigaChatTester(client_id, client_secret, auth_key)
    else:
        # Use client_id and client_secret directly
        tester = GigaChatTester(client_id, client_secret)
    
    success = tester.run_full_test()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()