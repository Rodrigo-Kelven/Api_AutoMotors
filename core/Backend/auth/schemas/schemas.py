from pydantic import BaseModel
from typing import Optional



# Modelos Pydantic para validação
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class User(BaseModel):
    username: Optional[str]
    email: Optional[str]
    full_name: Optional[str]


class UserResponse(BaseModel):
    username: str
    email: str
    full_name: str
    hashed_password: str
    disabled: bool
    role: str


class UserResponseEdit(BaseModel):
    username: str
    email: str
    full_name: str


class UserResponseCreate(BaseModel):
    username: str
    email: str
    full_name: str


class UserInDB(User):
    hashed_password: str