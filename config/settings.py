from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str
    OLLAMA_URL: str = "http://ollama:11434"
    VLLM_URL: str = "http://vllm:8000"
    RESULTS_DIR: str = "/app/results"
    
    class Config:
        env_file = ".env"

settings = Settings()
