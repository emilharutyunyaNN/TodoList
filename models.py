from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .database import Base
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique = True, index = True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default = True)
    
    tasks = relationship("Task", back_populates="owner")
    
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index = True)
    date = Column(String,index = True)
    time = Column(String, index = True)
    completed = Column(Boolean, index =True, default = False)
    owner_id = Column(Integer, ForeignKey("users.id")) 
    
    owner = relationship("User", back_populates="tasks")
    
    