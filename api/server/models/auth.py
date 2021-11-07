from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str

class UserNaunce(BaseModel):
    pubkey: str
    naunce: str
    is_new: bool

class LoginModel(BaseModel):
    pubkey: str
    signature: str
