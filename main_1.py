from fastapi import FastAPI,BackgroundTasks, Depends, HTTPException, status
import heapq
from pydantic import BaseModel
from typing import Annotated, Union, List
from datetime import datetime, timedelta, timezone, date, time
from fastapi.encoders import jsonable_encoder
from jose import JWTError, jwt
from passlib.context import CryptContext

        
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
#app = FastAPI()
scheduler = BackgroundScheduler()
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
        "tasks": current_tasks
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Union[str, None] = None
    
class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    tasks: dict = {}
    
    def __call__(self):
        pass
    

johndoe = User(**fake_users_db["johndoe"])

class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    #user.tasks = fake_users_db.get(token)["tasks"]
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    johndoe_temp = User(**fake_users_db[current_user.username])
    return johndoe_temp


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
   
    return current_user

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
def task_to_dict(task):
    dict = {}
    dict["name"] = task.name
    dict["date"] = task.date
    dict["time"] = task.time
    dict["complete"] = task.complete
    dict["urgent"] = task.urgent
    return dict

def compare_task(task):
    # Use the urgency value as the priority (True comes first)
    return not task.urgent

@app.post("/send-reminder/{email}")
async def send_notification(email: str, background_task: BackgroundTasks):
    set_of_tasks = [current_tasks[key] for key in current_tasks]
    for task in set_of_tasks:
        background_task.add_task(expiration_checkup, task, email)
    return {"message": "Task Expired! "}
@app.put("/user/priority",  description= "Path operation that puts tasks prioritized according to urgency")
async def add_with_priority(prioritize: bool, current_user: Annotated[User, Depends(get_current_active_user)]):
   
    #- **priority: Task().urgent

    tasks = current_user.tasks
    priority_queue = []
    converted_tasks = [convert_to_task(tasks[key]) for key in tasks]
    for i in range(len(converted_tasks)):
        heapq.heappush(priority_queue, (compare_task(converted_tasks[i]), converted_tasks[i]))

    prioritized_tasks = [task[1] for task in priority_queue]
    print(len(prioritized_tasks))
    if prioritize:
        dict = {}
        for i in range(len(prioritized_tasks)):
            dict[f"Task_{i}"] = task_to_dict(prioritized_tasks[i])
        current_user.tasks = dict
        return {"Prioritized" : dict}
    return prioritized_tasks

completed_tasks = {}

@app.post("/user/todo/{id}", response_model=Task)
async def return_list(id: int, current_user: Annotated[User, Depends(get_current_active_user)], limit: int = 100):
    tasks = current_user.tasks
    return tasks[list(tasks.keys())[id]]
from typing import Any
@app.post("/user/{id}", response_model=Any)
async def return_list(current_user: Annotated[User, Depends(get_current_active_user)],id: int , token_dict: Annotated[dict, Depends(login)], limit: int = 100):
    if not (token_dict.get("access_token")).task_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "No task found!")
    return (token_dict.get("access_token")).task_list
@app.put("/user/add")
async def add_tasks(current_user: Annotated[User, Depends(get_current_active_user)], name: Union[str, None], date: Union[str, None], 
                    time: Union[str, None], urgent:Union[bool, None]= None):
    
    tasks = current_user.tasks
    new_task = Task()
    new_task.name = name
    new_task.date = date
    new_task.time = time
    new_task.urgent = urgent
    names = [tasks[key]["name"] for key in tasks]
    if name in names:
        id_new = names.index(name)
        tasks[f"Task_{id_new}"] = new_task
        current_user.tasks = tasks
        raise HTTPException(status_code=status.HTTP_205_RESET_CONTENT, detail="Item exists resetting the task!")
    else:
        id_new = len(tasks)
        tasks[f"Task_{id_new+1}"] = {"name": new_task.name, "date":new_task.date, "time":new_task.time, "complete":new_task.complete, "urgent":new_task.urgent}
        current_user.tasks = tasks
    print("New task Added!")
    if urgent:
        return {"New_task": f"{new_task.name}, should be completed on {new_task.date} at {new_task.time} o'clock it is urgent"}
    
    return {"New_task": f"{new_task.name}, {new_task.date} at {new_task.time} o'clock"}, {"All the tasks": current_user.tasks}

"""
@app.put("/user/add/auth")
async def add_tasks(token_dict: Annotated[dict, Depends(login)], name: Union[str, None], date: Union[str, None], 
                    time: Union[str, None], urgent:Union[bool, None]= None):
    new_task = Task()
    new_task.name = name
    new_task.date = date
    new_task.time = time
    new_task.urgent = urgent
    names =[]
    if token_dict.get("access_token").task_list:
        names = [token_dict.get("access_token").task_list[key]["name"] for key in current_tasks]
       
    if name in names:
        id_new = names.index(name)
        token_dict.get("access_token").task_list[f"Task_{id_new}"] = new_task
        raise HTTPException(status_code=status.HTTP_205_RESET_CONTENT, detail="Item exists resetting the task!")
    else:
        id_new = len(current_tasks)
        token_dict.get("access_token").task_list[f"Task_{id_new+1}"] = {"name": new_task.name, "date":new_task.date, "time":new_task.time, "complete":new_task.complete, "urgent":new_task.urgent}
    print("New task Added!")
    if urgent:
        return {"New_task": f"{new_task.name}, should be completed on {new_task.date} at {new_task.time} o'clock it is urgent"}, {"All the tasks": token_dict.get("access_token").task_list}
    
    return {"New_task": f"{new_task.name}, {new_task.date} at {new_task.time} o'clock"}, {"All the tasks": token_dict.get("access_token").task_list}

"""


@app.delete("/user/delete")
async def delete_task(current_user: Annotated[User, Depends(get_current_active_user)],name: str):
    
    tasks = current_user.tasks
    names = [tasks[key]["name"] for key in tasks]
    if name in names:
        id_new = names.index(name)
        #id_comp = len(completed_tasks)
        tasks[f"Task_{id_new+1}"]["complete"] = True
        completed_tasks[f"Task_{id_new+1}"] = tasks[f"Task_{id_new+1}"]
        del tasks[f"Task_{id_new+1}"]
        current_user.tasks = tasks
        print(f"Task '{name}' completed.")
        return {"All the tasks": tasks}, {"Completed Tasks": completed_tasks}
    else:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Task doesn't exist!")

# Stop the scheduler when the FastAPI app shuts down
@app.on_event("shutdown")
async def stop_scheduler():
    scheduler.shutdown()