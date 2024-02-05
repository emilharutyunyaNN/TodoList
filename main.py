from fastapi import FastAPI,BackgroundTasks, Depends, HTTPException, status
import heapq
from pydantic import BaseModel
from typing import Annotated, Union, List
from datetime import datetime, timedelta, timezone, date, time
from fastapi.encoders import jsonable_encoder


"""from fastapi import FastAPI
import heapq
from pydantic import BaseModel
from typing import Union, List
from datetime import datetime
app = FastAPI()


class Task(BaseModel):
    name: Union[str, None] = None
    date: Union[str, None] = None
    time: Union[str, None] = None
    complete: Union[bool, None] = None
    urgent: bool = False
    
    def __lt__(self, other):
        return self.urgent < other.urgent


current_tasks = {
    "Task_1": {"name": "Morning routine", "date": "1/30/2024", "time": "7am", "complete": False, "urgent": False},
    "Task_2": {"name": "Lunch", "date": "1/30/2024", "time": "10am", "complete": False, "urgent": False},
    "Task_3": {"name": "Hang out with Julia", "date": "1/29/2024", "time": "5pm", "complete": False, "urgent": True},
    "Task_4": {"name": "Paint", "date": "1/30/2024", "time": "1pm", "complete": False, "urgent": True}
}
async def expiration_checkup(task: Task, email: str, notif: str = "will be deleted"):
    current_time = datetime.now()

# Extract day
    current_date_str = current_time.strftime("%Y-%m-%d")
    #print("Day:", day)
    current_date_dt = datetime.strptime(current_date_str, "%Y-%m-%d")

# Extract time
    current_time_str = current_time.strftime("%H:%M:%S")
    current_time_dt = datetime.strptime(current_time_str, "%H:%M:%S")
    
# Task date
    day = task["date"]
    original_format = datetime.strptime(day,"%m/%d/%Y")
    correct_format = original_format.strftime("%Y-%m-%d")    
    print("**")
    print(current_date_str ,"\n", correct_format)
    if current_date_str > correct_format:
        print(f"Task {task} expired")
        task["complete"] = True
        with open("log.txt", mode="w") as email_file:
            content = f"notification for {email}: Task {task} {notif}"
            email_file.write(content)


def convert_to_task(task_dict):
    task = Task(**task_dict)
    return task


def compare_task(task):
    # Use the urgency value as the priority (True comes first)
    return not task.urgent

@app.post("/send-reminder/{email}")
async def send_notification(email: str, background_task: BackgroundTasks):
    set_of_tasks = [current_tasks[key] for key in current_tasks]
    for task in set_of_tasks:
        background_task.add_task(expiration_checkup, task, email)
    return {"message": "Task Expired! "}
@app.put("/user/priority", response_model=List[Task], description= "Path operation that puts tasks prioritized according to urgency")
async def add_with_priority():
   
    #- **priority: Task().urgent

    priority_queue = []
    converted_tasks = [convert_to_task(current_tasks[key]) for key in current_tasks]
    for i in range(len(converted_tasks)):
        heapq.heappush(priority_queue, (compare_task(converted_tasks[i]), converted_tasks[i]))

    prioritized_tasks = [task[1] for task in priority_queue]
    return prioritized_tasks

completed_tasks = {}

@app.get("/user/todo/{id}", response_model=Task)
async def return_list(id: int , limit: int = 100):
    
    return current_tasks[list(current_tasks.keys())[id]]

@app.put("/user/add")
async def add_tasks(name: Union[str, None], date: Union[str, None], 
                    time: Union[str, None], urgent:Union[bool, None]= None):
    new_task = Task()
    new_task.name = name
    new_task.date = date
    new_task.time = time
    new_task.urgent = urgent
    names = [current_tasks[key]["name"] for key in current_tasks]
    if name in names:
        id_new = names.index(name)
        current_tasks[f"Task_{id_new}"] = new_task
        raise HTTPException(status_code=status.HTTP_205_RESET_CONTENT, detail="Item exists resetting the task!")
    else:
        id_new = len(current_tasks)
        current_tasks[f"Task_{id_new+1}"] = {"name": new_task.name, "date":new_task.date, "time":new_task.time, "complete":new_task.complete, "urgent":new_task.urgent}
    print("New task Added!")
    if urgent:
        return {"New_task": f"{new_task.name}, should be completed on {new_task.date} at {new_task.time} o'clock it is urgent"}
    
    return {"New_task": f"{new_task.name}, {new_task.date} at {new_task.time} o'clock"}, {"All the tasks": current_tasks}
@app.delete("/user/delete")
async def delete_task(name: str):
    names = [current_tasks[key]["name"] for key in current_tasks]
    if name in names:
        id_new = names.index(name)
        #id_comp = len(completed_tasks)
        current_tasks[f"Task_{id_new+1}"]["complete"] = True
        completed_tasks[f"Task_{id_new+1}"] = current_tasks[f"Task_{id_new+1}"]
        del current_tasks[f"Task_{id_new+1}"]
        
        print(f"Task '{name}' completed.")
        return {"All the tasks": current_tasks}, {"Completed Tasks": completed_tasks}
    else:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Task doesn't exist!")
        """
"""        
class Task(BaseModel):
    name: Union[str, None] = None
    date: Union[str, None] = None
    time: Union[str, None] = None
    complete: Union[bool, None] = None
    urgent: bool = False
    
    def __lt__(self, other):
        return self.urgent < other.urgent
current_tasks = {
    "Task_1": {"name": "Morning routine", "date": "1/30/2024", "time": "7am", "complete": False, "urgent": False},
    "Task_2": {"name": "Lunch", "date": "1/30/2024", "time": "10am", "complete": False, "urgent": False},
    "Task_3": {"name": "Hang out with Julia", "date": "1/29/2024", "time": "5pm", "complete": False, "urgent": True},
    "Task_4": {"name": "Paint", "date": "1/30/2024", "time": "1pm", "complete": False, "urgent": True}
}     
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, BackgroundTasks
from datetime import datetime, timedelta
from fastapi import FastAPI
import heapq
from pydantic import BaseModel
from typing import Union, List
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


app = FastAPI()
scheduler = BackgroundScheduler()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}"""
"""# Define a function to check and update expired tasks
def check_expired_tasks():
    current_time = datetime.now()

    for task_id, task in current_tasks.items():
        task_date = datetime.strptime(task["date"], "%m/%d/%Y")

        if current_time > task_date:
            # Task is expired, update the task or mark it as completed
            task["complete"] = True
            print(f"Task {task_id} has expired.")

# Start the scheduler when the FastAPI app starts
@app.on_event("startup")
async def start_scheduler():
    scheduler.add_job(check_expired_tasks, "interval", days=1)
    scheduler.start()

# Use a background task to periodically check expired tasks
@app.post("/send-reminder/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(check_expired_tasks)

# ... (rest of your FastAPI code)

async def expiration_checkup(task: Task, email: str, notif: str = "will be deleted"):
    current_time = datetime.now()

# Extract day
    current_date_str = current_time.strftime("%Y-%m-%d")
    #print("Day:", day)
    current_date_dt = datetime.strptime(current_date_str, "%Y-%m-%d")

# Extract time
    current_time_str = current_time.strftime("%H:%M:%S")
    current_time_dt = datetime.strptime(current_time_str, "%H:%M:%S")
    
# Task date
    day = task["date"]
    original_format = datetime.strptime(day,"%m/%d/%Y")
    correct_format = original_format.strftime("%Y-%m-%d")    
    print("**")
    print(current_date_str ,"\n", correct_format)
    if current_date_str > correct_format:
        print(f"Task {task} expired")
        task["complete"] = True
        with open("log.txt", mode="w") as email_file:
            content = f"notification for {email}: Task {task} {notif}"
            email_file.write(content)

def convert_to_task(task_dict):
    task = Task(**task_dict)
    return task


def compare_task(task):
    # Use the urgency value as the priority (True comes first)
    return not task.urgent

@app.post("/send-reminder/{email}")
async def send_notification(email: str, background_task: BackgroundTasks):
    set_of_tasks = [current_tasks[key] for key in current_tasks]
    for task in set_of_tasks:
        background_task.add_task(expiration_checkup, task, email)
    return {"message": "Task Expired! "}
@app.put("/user/priority", response_model=List[Task], description= "Path operation that puts tasks prioritized according to urgency")
async def add_with_priority():
   
    #- **priority: Task().urgent

    priority_queue = []
    converted_tasks = [convert_to_task(current_tasks[key]) for key in current_tasks]
    for i in range(len(converted_tasks)):
        heapq.heappush(priority_queue, (compare_task(converted_tasks[i]), converted_tasks[i]))

    prioritized_tasks = [task[1] for task in priority_queue]
    return prioritized_tasks

completed_tasks = {}

@app.get("/user/todo/{id}", response_model=Task)
async def return_list(id: int , limit: int = 100, ):
    
    return current_tasks[list(current_tasks.keys())[id]]

@app.put("/user/add")
async def add_tasks(name: Union[str, None], date: Union[str, None], 
                    time: Union[str, None], urgent:Union[bool, None]= None):
    new_task = Task()
    new_task.name = name
    new_task.date = date
    new_task.time = time
    new_task.urgent = urgent
    names = [current_tasks[key]["name"] for key in current_tasks]
    if name in names:
        id_new = names.index(name)
        current_tasks[f"Task_{id_new}"] = new_task
        raise HTTPException(status_code=status.HTTP_205_RESET_CONTENT, detail="Item exists resetting the task!")
    else:
        id_new = len(current_tasks)
        current_tasks[f"Task_{id_new+1}"] = {"name": new_task.name, "date":new_task.date, "time":new_task.time, "complete":new_task.complete, "urgent":new_task.urgent}
    print("New task Added!")
    if urgent:
        return {"New_task": f"{new_task.name}, should be completed on {new_task.date} at {new_task.time} o'clock it is urgent"}
    
    return {"New_task": f"{new_task.name}, {new_task.date} at {new_task.time} o'clock"}, {"All the tasks": current_tasks}
@app.delete("/user/delete")
async def delete_task(name: str):
    names = [current_tasks[key]["name"] for key in current_tasks]
    if name in names:
        id_new = names.index(name)
        #id_comp = len(completed_tasks)
        current_tasks[f"Task_{id_new+1}"]["complete"] = True
        completed_tasks[f"Task_{id_new+1}"] = current_tasks[f"Task_{id_new+1}"]
        del current_tasks[f"Task_{id_new+1}"]
        
        print(f"Task '{name}' completed.")
        return {"All the tasks": current_tasks}, {"Completed Tasks": completed_tasks}
    else:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Task doesn't exist!")

# Stop the scheduler when the FastAPI app shuts down
@app.on_event("shutdown")
async def stop_scheduler():
    scheduler.shutdown()"""
    
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas, database
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind = engine)


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail = "Email already registered")
    return crud.create_user(db = db, user = user)

@app.get("/users", response_model=list[schemas.User])
def read_users(skip: int = 0, limit:int=100, db:Session = Depends(get_db)):
    
    users = crud.get_users(db,skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/tasks/", response_model=schemas.Task)
def create_task_for_user(
    user_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)
):
    return crud.create_user_task(db=db, task=task, user_id=user_id)

@app.delete("/users/{user_id}/tasks")
def delete_task_for_user(user_id: int, name: str, db: Session = Depends(get_db)
):
    crud.delete_user_task(db,name,user_id)
    return {"message": f"Task {name} deleted"}
    
@app.put("/users/{user_id}/tasks")
def update_task_for_user(name:str, user_id:int,date:str, time:str, completed:bool, db:Session =  Depends(get_db)):
    
    crud.update_user_task(db, name, date, time, completed, user_id)
    return {"message": f"Task {name}  has been updated!"}
    
@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@app.post("/users/login")
def login(email: str, password:str, db: Session = Depends(get_db)):
    crud.login(db,email,password)
    
