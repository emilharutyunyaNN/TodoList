from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from . import models, schemas
from .database import SessionLocal
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_user(db: Session, user_id:int):
    return db.query(models.User).filter(models.User.id ==user_id).first()

def get_user_by_username(db: Session, username:str):
    return db.query(models.User).filter(models.User.username ==username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email==email).first()

def get_users(db:Session, skip: int=0, limit: int=100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    if "$" not in user.password and "." not in user.password and "_" not in user.password and "/" not in user.password :
        return {"message": "Password not safe, should contain these characters $._/"}
    hashed_password = get_password_hash(user.password)
    #print(hashed_password)
    db_user = models.User(username = user.username, email = user.email, hashed_password = hashed_password)
    if len(db_user.username)<=20 and len(db_user.username)>8:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        return {"message": "Username should be longer than 8 characters and shorter than 20"}
    return db_user

def get_tasks(db:Session,skip: int = 0, limit:int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()
def get_tasks_by_id(db:Session, id:int):
    return db.query(models.Task).filter(models.Task.owner_id==id).all()
def create_user_task(db:Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(**task.dict(), owner_id = user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def create_task_by_username(db:Session, task: schemas.TaskCreate, username: str):
    pass

def get_task_by_name(db:Session, name:str, user_id:str):
    return db.query(models.Task).filter(models.Task.name == name, models.Task.owner_id==user_id).first()

def delete_user_task(db:Session, name: str, user_id):
    db_task = get_task_by_name(db,name,user_id)

    if db_task:  
        db.delete(db_task)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Task doesn't exist")

def update_user_task(
    db: Session, name: str, date: str, time: str, completed: bool
 ,user_id):
    db_task = get_task_by_name(db,name,user_id)  # Ensure user_id is a string
    print(db_task.name)
    if db_task:
        print("***")
        db_task.name = name
        db_task.date = date
        db_task.time = time
        db_task.completed = completed

        db.commit()
        db.refresh(db_task)
        #return {"message": f"Task {name} for user {user_id} has been updated!"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task doesn't exist")
    
from datetime import datetime, timedelta, timezone
def login(db:Session, email: str, password: str):
    user = get_user_by_email(db = db, email=email)
    if not verify_password(password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {"Your tasks" : user.tasks}

def check_expired(db:Session, username:str):
    user = get_user_by_username(db=db,username=username)
    user_id = user.id
    tasks = get_tasks_by_id(db=db,id=user_id)
    current_time = datetime.now()
    
    current_date_str = current_time.strftime("%Y-%m-%d")
    #print("Day:", day)
    time_part = current_time.strftime("%H:%M:%S")
    current_date_dt = datetime.strptime(current_date_str, "%Y-%m-%d")
    days = [task.date for task in tasks]
    times = [task.time for task in tasks]
    expired = []
    for day,time,task in zip(days,times,tasks):
        dt = datetime.strptime(time, "%I%p")
        original_format = datetime.strptime(day,"%m/%d/%Y")
        correct_format = original_format.strftime("%Y-%m-%d")
        if current_date_str>correct_format:
            task.completed = True
            expired.append(task)
            #return True
        if current_date_str == correct_format:
            if time_part> dt.strftime("%H:%M:%S"):
                task.completed = True
                expired.append(task)
        
    return expired

def send_notification(notif:str = "You have expired tasks come check it!"):
    db = SessionLocal()
    users = get_users(db=db)
    print(users)
    for user in users:
        expired = check_expired(db=db,username=user.username)
        for task in expired:
            with open(f"log_{user.username}.txt", mode="w") as email_file:
                content = f"notification for {user.email}: {notif}. Details: expired tasks: {task.name}"
                email_file.write(content) 
    