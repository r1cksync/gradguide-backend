from openai import AsyncOpenAI
from app.core.config import settings
import logging
import httpx

logger = logging.getLogger("gradguide")

class LLMService:
    def __init__(self):
        try:
            self.client = AsyncOpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                timeout=30.0,
                max_retries=3
            )
        except Exception as e:
            logger.error(f"Failed to initialize AsyncOpenAI: {str(e)}", exc_info=True)
            raise

    async def get_llm_response(self, messages):
        try:
            response = await self.client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                extra_headers={
                    "HTTP-Referer": "http://localhost",
                    "X-Title": "GradGuide"
                }
            )
            return response.choices[0].message.content
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during LLM call: {str(e)}", exc_info=True)
            return f"Error: Failed to generate response - HTTP error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during LLM call: {str(e)}", exc_info=True)
            return f"Error: Failed to generate response - {str(e)}"

llm_service = LLMService()

async def get_llm_response(messages):
    return await llm_service.get_llm_response(messages)