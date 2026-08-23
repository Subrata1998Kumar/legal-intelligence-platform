import httpx
from ..config import settings

class ChatService:
    @staticmethod
    async def generate_response(prompt: str, system_prompt: str = "You are a professional legal AI assistant. Keep responses grounded in the context.") -> str:
        url = f"{settings.OLLAMA_URL}/api/chat"
        payload = {
            "model": settings.CHAT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "options": {
                "temperature": 0.1
            },
            "stream": False
        }
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return response.json().get("message", {}).get("content", "").strip()
        except Exception:
            return f"[Offline Mode] Local model connection to Ollama could not be established. Falling back to structured response parsing."
        return "No response could be generated."