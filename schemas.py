from typing import Union

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: Union[str, None] = None

class TaskBase(BaseModel):
    name: str 
    date: str 
    time: str 
    completed: bool = False
    
class TaskCreate(TaskBase):
    pass 

class Task(TaskBase):
    id: int
    owner_id:int
    
    class Config:
        orm_mode = True
        
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    tasks: list[Task] = []

    class Config:
        orm_mode = True