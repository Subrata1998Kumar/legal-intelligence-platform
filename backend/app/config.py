import os
from pathlib import Path
from dotenv import load_dotenv

class config_data:
    def __init__(self):
        PROJECT_ROOT = Path(__file__).resolve().parent
        ENV_FILE = PROJECT_ROOT / "env_files" / "dev.env"
        load_dotenv(ENV_FILE)
        self.DATABASE_URL = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASS = os.getenv("DB_PASS")
        self.CHAT_MODEL = os.getenv("CHAT_MODEL")
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
        self.OLLAMA_URL = os.getenv("OLLAMA_URL")

if __name__=='__main__':
    conf_data = config_data()
    print(conf_data.DATABASE_URL)
    print(conf_data.EMBEDDING_MODEL)