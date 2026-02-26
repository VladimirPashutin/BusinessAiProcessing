# Interface for LLM model requests.
from __future__ import annotations

import enum


class AiInterface:
    def getId(self) -> str:
        pass
    def request_rate(self, request: str, prompt: str) -> float:
        pass
    def response_to_request(self, orgName: str, request: str, prompt: str, char_limit: int, lower_tier: int = 0) -> str:
        pass
    def generate_publication(self, orgName: str, assortment: str, description: str, imageDescription: str, prompt: str,char_limit: int, lower_tier: int = 0) -> str:
        pass
    def describeImage(self, orgName: str, imageUrl: str, assortment: str, prompt: str, token_limit: int, is_public_url: bool | None = None, lower_tier: int = 0, file_metadata: dict = None) -> tuple[str | None, dict | None]:
        pass

@enum.unique
class AiTarget(enum.Enum):
    publication = 0
    response = 1
