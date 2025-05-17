import httpx
from app.core.config import settings

def get_llm_response(messages: list[dict], system_prompt: str = None):
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": messages
    }
    if system_prompt:
        payload["messages"].insert(0, {"role": "system", "content": system_prompt})
    
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60.0
    )
    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.text}")
    return response.json()["choices"][0]["message"]["content"]