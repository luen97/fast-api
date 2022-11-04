
# Python
from uuid import UUID
from datetime import (
    date, datetime)
from typing import Optional

# Pydantic
from pydantic import (
    BaseModel, EmailStr, Field,
    validator
)


# FastAPI
from fastapi import FastAPI

app = FastAPI()


# Models

class UserBase(BaseModel):
    user_id: UUID = Field(...)
    email: EmailStr = Field(...)

class UserLogin(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=64
    )

class User(UserBase):

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example="Emilio"
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example="Contentillo"
    )
    birth_date: Optional[date] = Field(
        default=None,
        example="1994-11-04"
    )
    # Decorador de pydantic para hacer validaciones personalizadas
    # https://pydantic-docs.helpmanual.io/usage/validators/
    @validator('birth_date')  
    def is_over_eighteen(cls, v):
        todays_date = date.today()
        delta = todays_date - v

        if delta.days/365 <= 18:
            raise ValueError('Must be over 18!')
        else:
            return v

class Tweet():
    tweet_id: UUID = Field(...)
    content: str = Field(
        ...,
        min_length=1,
        max_length=256
    )
    created_at: datetime = Field(default=datetime.now())
    update_at: Optional[datetime] = Field(default=None)
    by: User = Field(...)


@app.get(
    path="/")
def home():
    return {"Twitter API": "Working"}

