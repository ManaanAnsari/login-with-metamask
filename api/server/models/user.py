from typing import Optional
from pydantic import BaseModel, EmailStr, Field



class UserSchema(BaseModel):
    id: str = Field(...)
    username: str = Field(...)
    naunce: str = Field(...)
    email: Optional[EmailStr]
    name: Optional[str]
    bio: Optional[str]
    insta_link: Optional[str]
    disabled: Optional[bool] = False

    class Config:
        schema_extra = {
            "example": {
                "id": "0xAnfknf...ccd",
                "username": "0xAnfknf...ccd",
                "naunce": "random validator string",
                "email": "jdoe@x.edu.ng",
                "name": "Joker",
                "bio": "awesomne person ;)",
                "insta_link": "insta.com/awesomeperson",
            }
        }


class UpdateUserModel(BaseModel):
    email: Optional[EmailStr]
    name: Optional[str]
    bio: Optional[str]
    insta_link: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "email": "jdoe@x.edu.ng",
                "name": "Joker",
                "bio": "awesomne person ;)",
                "insta_link": "insta.com/awesomeperson",
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}