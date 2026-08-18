from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    user_message: str = Field(description="Запрос пользователя в SQL агент")