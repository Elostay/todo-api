from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from databse import engine, SesionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class TodoBase(BaseModel):
	done: bool
	task: str
	rate: int
	

def get_db():
	db = SesionLocal()
	try:
		yield db
	finally:
		db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/tasks/{task_id}")
async def read_task(_id: int, db:db_dependency):
	result = db.query(models.Todos).filter(models.Todos._id == _id).first()

	if not result:
		raise HTTPException(status_code=404, detail='Task is not found')
		
	return result

@app.get("/tasks/")
async def read_tasks(db:db_dependency):
	result = db.query(models.Todos).all()

	if not result:
		raise HTTPException(status_code=404, detail='Tasks is not found')
	
	return result

@app.post('/todos/')
async def create_todos(task: TodoBase, db: db_dependency):
	db_todos = models.Todos(task=task.task, rate=task.rate, done=task.done)

	db.add(db_todos)
	db.commit()
	db.refresh(db_todos)

@app.patch('/tasks/{task_id}')
async def edit_task(_id: int, task: str, rate: int, db: db_dependency):
	db_todos = db.query(models.Todos).filter(models.Todos._id == _id).first()
	
	if db_todos is None:
		raise HTTPException(status_code=404, detail="Task not found")
	
	db_todos.task = task
	db_todos.rate = rate

	db.commit()
	db.refresh(db_todos)
	
@app.delete("/tasks/{task_id}")
async def delete_task(_id: int, db: db_dependency):
    db_todos = db.query(models.Todos).filter(models.Todos._id == _id).first()
    if db_todos is None:
        raise HTTPException(status_code=404, detail="Task not found")
	 
    db.delete(db_todos)
    db.commit()

    