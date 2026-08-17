from dotenv import load_dotenv
from pydantic import BaseModel
import os

load_dotenv()

class Config(BaseModel):
    db_url: str = os.getenv("POSTGRES")
    model: str = os.getenv("LLM_MODEL")
    api_key: str = os.getenv("API_KEY")
    api_url: str = os.getenv("PROVIDER_URL")
