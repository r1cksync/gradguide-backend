import logging
from app.services.llm import get_llm_response
from typing import List, Dict

logger = logging.getLogger("gradguide")

class SimpleChatbot:
    async def query(self, query: str, user_id: str = None, session_id: str = None, history: List[Dict[str, str]] = None) -> str:
        try:
            # Build context
            context = ""
            if history:
                context = "Previous conversation in this session (use this to answer questions about prior messages):\n"
                for msg in history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    context += f"{role}: {msg['content']}\n"
                context += "\n"
                logger.info(f"Using history context: {context}")

            prompt = f"""
            You are an expert college admission counselor for Indian B.Tech programs, specializing in engineering entrance exams like JEE Main, JEE Advanced, WBJEE, VITEEE, and BITSAT. Your goal is to provide accurate, helpful, and concise advice to students based on their queries. Use your knowledge of Indian engineering colleges, including their reputation, branches (e.g., Computer Science, Mechanical), and general admission trends (e.g., cutoffs, placements).

            Guidelines:
            - For queries about college or branch selection, provide recommendations based on typical rank ranges and college prestige (e.g., NITs, IITs, IIITs).
            - If the query specifies a rank and exam (e.g., 'JEE Main rank 200'), suggest top colleges and branches realistically achievable for that rank.
            - Handle requests for multiple colleges (e.g., 'best and second best') by ranking colleges based on reputation and placement trends.
            - For general queries (e.g., 'best colleges for CSE'), provide a list of well-known colleges and relevant advice.
            - If the query asks about previous messages (e.g., 'what was my last question?'), use the provided conversation context to answer accurately, referencing specific prior questions or answers.
            - Use integer values for placements (e.g., 20 LPA).
            - Be concise, friendly, and professional.
            - Always use the previous conversation context to ensure consistent and relevant responses, especially for follow-up questions.

            {context}
            Question: {query}

            Response:
            """
            messages = [{"role": "user", "content": prompt}]
            response = await get_llm_response(messages)
            if not response.strip():
                logger.warning("LLM returned empty response")
                return "Sorry, I couldn't find relevant information. Could you clarify your query?"
            logger.info(f"SimpleChatbot response: {response}")
            return response
        except Exception as e:
            logger.error(f"SimpleChatbot error: {e}")
            return "Error: Failed to process query."