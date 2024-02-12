   
from fastapi import Depends,Query ,FastAPI,BackgroundTasks,APIRouter, HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import crud, crud_jwt, models, schemas, database
from .database import SessionLocal, engine
from fastapi import Path
from fastapi.responses import RedirectResponse
from enum import Enum
from typing import Annotated, Union, List

models.Base.metadata.create_all(bind = engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/login")
app = FastAPI()

class Tags(Enum):
    all_tasks = "all tasks"
    authenticated_tasks = "user task"
    users = "users"
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from apscheduler.schedulers.background import BackgroundScheduler        
scheduler = BackgroundScheduler()
@app.on_event("startup")
def check_exp():
    scheduler.add_job(crud.send_notification, "interval", days = 1)
    scheduler.start()
#response_model=schemas.User
@app.post("/users/", status_code=status.HTTP_201_CREATED, tags=[Tags.users])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail = "Email already registered")
    return crud.create_user(db = db, user = user)

@app.get("/users", response_model=list[schemas.User], tags=[Tags.users])
def read_users(skip: int , limit:int=100, db:Session = Depends(get_db)):
    
    users = crud.get_users(db,skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User, tags=[Tags.users])
def read_user(user_id: int, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)):
    active_user = crud_jwt.get_current_active_user(db=db,token=token)
    db_user = crud.get_user(db, user_id=user_id)
    if db_user !=  active_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wrong user ID!")
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@app.post("/users/{user_id}/tasks/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED, tags=[Tags.authenticated_tasks])
def create_task_for_user(
    user_id: int, task: schemas.TaskCreate, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)
):
    active_user = crud_jwt.get_current_active_user(db=db,token=token)
    
    if active_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wrong user ID!")
    return crud.create_user_task(db=db, task=task, user_id=user_id)

@app.delete("/users/{user_id}/tasks", tags=[Tags.authenticated_tasks])
def delete_task_for_user(user_id: int, name: str, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)
):
    active_user = crud_jwt.get_current_active_user(db=db,token=token)
    
    if active_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wrong user ID!")
    crud.delete_user_task(db,name,user_id)
    return {"message": f"Task {name} deleted"}
    
"""@app.put("/users/{user_id}/tasks", tags=[Tags.authenticated_tasks])
def update_task_for_user(name:str, user_id:int,date:str, time:str, completed:bool, db:Session =  Depends(get_db)):
    
    crud.update_user_task(db, name, date, time, completed, user_id)
    return {"message": f"Task {name}  has been updated!"}
"""
@app.put("/users/{user_id}/tasks", tags=[Tags.authenticated_tasks])
def update_task_for_user(name:str, user_id:int,date:str, time:str, completed:bool,token: Annotated[str, Depends(oauth2_scheme)], db:Session =  Depends(get_db)):
    active_user = crud_jwt.get_current_active_user(db=db,token=token)
    
    #username = active_user.username
    #user = crud.get_user_by_username(db=db,username=username)
    if active_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wrong user ID!")
    crud.update_user_task(db, name, date, time, completed, user_id)
    return {"message": f"Task {name}  has been updated!"}
    
@app.get("/tasks/", response_model=list[schemas.Task], tags=[Tags.all_tasks])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@app.post("/users/login", tags=[Tags.users])
def login(email: str, password:str, db: Session = Depends(get_db)):
    return crud.login(db,email,password)
    
@app.post("/users/{username}", response_model=schemas.User,tags=[Tags.users])
def get_username(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/me/", response_model=schemas.User, tags=[Tags.users])
async def read_users_me(
    token: Annotated[str, Depends(oauth2_scheme)],db:Session = Depends(get_db)
):
    return await crud_jwt.get_current_active_user(db,token)
        
    
router = APIRouter()

@router.post("/token/login")
async def login_alt(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:Session = Depends(get_db)):
    username = form_data.username
    user = crud_jwt.get_user_by_username(db,username)
    user_id = user.id
    response = await crud_jwt.login_for_access_token(db,form_data)
    return response


@router.get("/user/{user_id}", response_model=schemas.User)
def user_page(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
app.include_router(router)
@app.get("/docs/{user_id}", response_model=schemas.User)  # Endpoint for user's tasks page
def user_docs(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Retrieve tasks specific to the user
    user_tasks = crud.get_tasks_by_id(db, user_id)
    user_out = schemas.User(
        id=db_user.id,
        username=db_user.username,
        email = db_user.email,
        is_active = db_user.is_active,
        tasks = user_tasks
    )
    return user_out
@app.post("/users/{username}")
def expiration_check(username: str,db:Session = Depends(get_db)):
    return {"tasks expired": crud.check_expired(db=db,username=username)}
@app.delete("/users/eliminate", tags=[Tags.users])
def eliminate_expired(db:Session = Depends(get_db), notif:str = "You have expired tasks come check it!"):
#def eliminate_expired(notif:str = "You have expired tasks come check it!"):
    
    users = crud.get_users(db=db)
    print(users)
    for user in users:
        expired = crud.check_expired(db=db,username=user.username)
        for task in expired:  
             
            crud.delete_user_task(db=db, user_id=user.id,name=task.name)
            