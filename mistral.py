from __future__ import annotations

import base64

import httpx
import requests
from mistralai import Mistral

import environment
from ai_interface import AiInterface

CAPACITY_EXCEEDED_CODES = {"3505", "service_tier_capacity_exceeded"}

class MistralAi(AiInterface):

    def __init__(self):
        self.id = 'Mistral'
        env = environment.Environment('business-ai-service')
        self.api_key = env.get('python.mistral-key')
        # Predefined model tiers (high -> low), generic names only
        self.text_tiers = [
            "mistral-large-latest",
            "mistral-medium-latest",
            "mistral-small-latest",
        ]
        self.vision_tiers = [
            "mistral-medium-latest",
            "mistral-small-latest",
            "ministral-14b-2512",
        ]

    # Helper to pick model by kind and tier offset (0=large, 1=medium, 2=small)
    def _pick_model(self, kind: str, lower_tier: int) -> str:
        tiers = self.text_tiers if kind == "text" else self.vision_tiers
        index = max(0, min(lower_tier, 2))
        return tiers[index]

    def _is_capacity_exceeded(self, err: Exception) -> bool:
        # Heuristic: look for 429 and code in message
        msg = str(err)
        return ("Status 429" in msg) or any(code in msg for code in CAPACITY_EXCEEDED_CODES)

    def getId(self) -> str:
        return self.id

    def request_rate(self, request: str, prompt: str) -> float:
        print("provider Mistral endpoint request_rate called")
        print("provider Mistral endpoint request_rate response success (returning -1)")
        return -1

    def describeImage(self, orgName: str, imageUrl: str, assortment: str,
                      prompt: str, token_limit: int, lower_tier: int = 0, file_metadata: dict = None) -> tuple[str | None, dict | None]:
        print(f"provider Mistral endpoint describeImage called (tier: {lower_tier})")
        with Mistral(api_key=self.api_key, client=httpx.Client(verify=False, follow_redirects=True)) as mistral:
            try:
                response = requests.get(imageUrl, stream=True, verify=False)
                image_data = base64.b64encode(response.content).decode('utf-8')
                model_name = self._pick_model("vision", lower_tier)
                res = mistral.chat.complete(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": prompt},
                        {
                            "role": "system",
                            "content": f"Необходимо учесть, что компания именуется как {orgName}, "
                                       f"а описание изображения формируется для продукта или услуги компании, "
                                       f"называющегося {assortment}"
                        },
                        {
                            "content": "Результирующее описание должно содержать не более " + str(token_limit) + " символов",
                            "role": "system",
                        },
                        {
                            "content": [
                                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                            ],
                            "role": "user"
                        }
                    ],
                    max_tokens=token_limit)
                if res is not None and hasattr(res, 'choices') and len(res.choices) > 0:
                    print("provider Mistral endpoint describeImage response success")
                    return res.choices[0].message.content, None  # Mistral doesn't return metadata
                else:
                    print("provider Mistral endpoint describeImage response failed (no choices)")
                    return None, None
            except Exception as e:
                if self._is_capacity_exceeded(e) and lower_tier < 2:
                    # Retry with a lower tier inside provider
                    print(f"Retrying describeImage with lower tier: {lower_tier + 1}")
                    return self.describeImage(orgName, imageUrl, assortment, prompt, token_limit, lower_tier + 1, file_metadata)
                print(f"provider Mistral endpoint describeImage response failed: {e}")
                return None, None

    def response_to_request(self, orgName: str, request: dict, prompt: str, char_limit: int, lower_tier: int = 0) -> str | None:
        print(f"provider Mistral endpoint response_to_request called (tier: {lower_tier})")
        with Mistral(api_key=self.api_key, client=httpx.Client(verify=False)) as mistral:
            try:
                model_name = self._pick_model("text", lower_tier)
                res = mistral.chat.complete(
                    model=model_name,
                    messages=[
                        {"content": prompt, "role": "system"},
                        {"content": "Результирующее описание должно содержать не более " + str(char_limit) + " символов", "role": "system"},
                        {"role": "system", "content": f"Необходимо учесть, что компания именуется как {orgName}"},
                        {"content": f"Пользователь услуг направил в компанию запрос следующего содержания: {request}", "role": "user"}
                    ])
                if res is not None and hasattr(res, 'choices') and len(res.choices) > 0:
                    print("provider Mistral endpoint response_to_request response success")
                    return res.choices[0].message.content
                else:
                    print("provider Mistral endpoint response_to_request response failed (no choices)")
                    return None
            except Exception as e:
                if self._is_capacity_exceeded(e) and lower_tier < 2:
                    print(f"Retrying response_to_request with lower tier: {lower_tier + 1}")
                    return self.response_to_request(orgName, request, prompt, char_limit, lower_tier + 1)
                print(f"provider Mistral endpoint response_to_request response failed: {e}")
                return None

    def generate_publication(self, orgName: str, assortment: str, description: str,
                             imageDescription: str, prompt: str, char_limit: int, lower_tier: int = 0) -> str | None:
        print(f"provider Mistral endpoint generate_publication called (tier: {lower_tier})")
        with Mistral(api_key=self.api_key, client=httpx.Client(verify=False)) as mistral:
            try:
                operatedMessages = [
                    {"role": "system", "content": prompt},
                    {
                        "role": "system",
                        "content": f"Необходимо учесть, что компания именуется как {orgName}, "
                                   f"а публикация формируется для продукта или услуги компании, "
                                   f"называющегося {assortment}"
                    },
                    {"content": f"Результирующее описание должно содержать не более {char_limit} символов", "role": "system"},
                    {"role": "user", "content": f"Компания предоставила следующее описание для продукта или услуги: {description}"}
                ]
                if imageDescription is not None:
                    operatedMessages.append({
                        "role": "user",
                        "content": f"Публикация сопровождается изображением, описание которого сформулировано как {imageDescription}"
                    })
                model_name = self._pick_model("text", lower_tier)
                res = mistral.chat.complete(model=model_name, messages=operatedMessages)
                if res is not None and hasattr(res, 'choices') and len(res.choices) > 0:
                    print("provider Mistral endpoint generate_publication response success")
                    return res.choices[0].message.content
                else:
                    print("provider Mistral endpoint generate_publication response failed (no choices)")
                    return None
            except Exception as e:
                if self._is_capacity_exceeded(e) and lower_tier < 2:
                    print(f"Retrying generate_publication with lower tier: {lower_tier + 1}")
                    return self.generate_publication(orgName, assortment, description, imageDescription, prompt, char_limit, lower_tier + 1)
                print(f"provider Mistral endpoint generate_publication response failed: {e}")
                return None
