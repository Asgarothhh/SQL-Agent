from langchain_openai import ChatOpenAI
from services.config import Config

config = Config()


model = ChatOpenAI(
    model = config.model,
    base_url=config.api_url,
    api_key=config.api_key,
    temperature=0.1
)