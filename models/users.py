from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    username: str

class UpdateUserName(BaseModel):
    username: str

class UserData(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    username: str
    password: str
    email: EmailStr

