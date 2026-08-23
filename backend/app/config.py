import os

class Settings:
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS", "password")

    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "granite4.1:3b")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual:278m")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")

    # Note: JWT Secret configuration is kept for backwards compatibility but is bypassed for Basic Auth.
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-government-clearance-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

settings = Settings()