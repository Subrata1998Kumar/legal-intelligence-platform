"""  Local Chat and Embedding Model Initialization """
import json
import requests
from typing import Iterator
from langchain_ollama import OllamaEmbeddings
from config import config_data

class Models:
    def __init__(self):
        cnf = config_data()
        self.__ollama_url = cnf.OLLAMA_URL
        self.__chat_model = cnf.CHAT_MODEL 
        self.embedding_model = OllamaEmbeddings(model=cnf.EMBEDDING_MODEL) 
    def generate_response(self, prompt: str) -> Iterator[str]:
        try:
            response = requests.post(
                f"{self.__ollama_url}/api/generate",
                json={
                    "model": self.__chat_model,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue

                chunk = json.loads(line)
                content = chunk.get("response", "")

                if content:
                    yield content

                if chunk.get("done"):
                    break
        except Exception as e:
            raise RuntimeError(f"Unexpected error in generate_response: {e}") from e

if __name__=='__main__':
    models = Models()
    for response_chunk in models.generate_response("Tell 5 important things about Ratan Tata in Bengali"):
        print(response_chunk, end="", flush=True)