# TodoList
This is a FastAPI backend for a simple todo list (with user database and task database for each user)
Todolists are very important for organizing our day and being productive. I myself create todo lists everyday and try to stick
to them as much as possible to stay productive and have progress. Which served as a motivation for me to develop the system.

How to run:
  uvicorn main:app --reload

Properties:
  --linked to a database (with sqlalchemy) of users and their tasks \\
  --users need to go through authentication process to be able to edit tasks in their account\\
  --tasks include (name, date, time, urgent, complete) attributes\\
  --system checks if tasks are expired or not periodically and sends notifications if they are expired\\
  --system also can automatically mark expired tasks as complete and remove them from database\\
  --after authentication CRUD operation available\\
  --password hashing\\

