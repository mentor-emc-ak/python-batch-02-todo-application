import requests
import json
from .config import settings


def get_openrouter_response(prompt):
    return requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "akhshy.dev",
            "X-OpenRouter-Title": "akhshy.dev",
        },
        data=json.dumps({
            "model": "~anthropic/claude-sonnet-latest",
            "messages": [
            {
                "role": "user",
                "content": prompt
            }
            ]
        })
    )
