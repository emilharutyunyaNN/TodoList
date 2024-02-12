from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, FastAPI, HTTPException, status
from . import models, schemas

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
    hashed_password = get_password_hash(user.password)
    print(hashed_password)
    db_user = models.User(username = user.username, email = user.email, hashed_password = hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_tasks(db:Session,skip: int = 0, limit:int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()

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
    
    



def authenticate_user(db:Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_active_user(db:Session, token: Annotated[str, Depends(oauth2_scheme)]):
    #print("**")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        #print(token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       # print("***")
        username: str = payload.get("sub")
        #print(username)
        
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


"""async def get_current_active_user(db:Session,
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user"""



async def login_for_access_token(
    db:Session, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> schemas.Token:
    
    print("***")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")
