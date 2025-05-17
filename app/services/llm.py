import httpx
from app.core.config import settings
from typing import List, Dict, Any

async def get_llm_response(messages: List[Dict[str, str]], system_prompt: str = None):
    """
    Get a response from the OpenRouter API using the configured LLM model.
    """
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": messages,
    }
    
    if system_prompt:
        payload["messages"].insert(0, {"role": "system", "content": system_prompt})
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60.0
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.text}")
        
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]