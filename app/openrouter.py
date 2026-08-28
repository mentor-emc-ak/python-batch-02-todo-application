import requests
import json
from .config import settings

DEFAULT_MODEL = "moonshotai/kimi-k3"

API_URL = "https://openrouter.ai/api/v1/chat/completions"


def _headers():
    return {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": "akhshy.dev",
        "X-OpenRouter-Title": "akhshy.dev",
    }


def get_openrouter_response(prompt, model=DEFAULT_MODEL, max_tokens=1024):
    return requests.post(
        url=API_URL,
        headers=_headers(),
        data=json.dumps({
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
            {
                "role": "user",
                "content": prompt
            }
            ]
        })
    )


def chat_completion(messages, tools=None, model=DEFAULT_MODEL, max_tokens=1024):
    """Multi-turn call that can hand the model tools to call."""
    payload = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if tools:
        payload["tools"] = tools

    return requests.post(url=API_URL, headers=_headers(), data=json.dumps(payload))
