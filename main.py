from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# origins = [
#     "http://localhost",
#     "http://localhost:3000",
#     "https://localhost:3000",
#     "https://todo-2-five.vercel.app/"
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TodoBase(BaseModel):
    done: bool
    task: str
    rate: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.head("/")
async def head_root():
    return {}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 4000))
    uvicorn.run(app, host="0.0.0.0", port=port)

@app.get("/tasks/{task_id}")
async def read_task(task_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Todos).filter(models.Todos._id == task_id).first()

    if not result:
        raise HTTPException(status_code=404, detail='Task is not found')
        
    return result

@app.get("/tasks/")
async def read_tasks(db: Session = Depends(get_db)):
    result = db.query(models.Todos).all()

    if not result:
        raise HTTPException(status_code=404, detail='Tasks is not found')
    
    return result

@app.post('/todos/')
async def create_todos(task: TodoBase, db: Session = Depends(get_db)):
    db_todos = models.Todos(task=task.task, rate=task.rate, done=task.done)

    db.add(db_todos)
    db.commit()
    db.refresh(db_todos)

    return db_todos 

@app.patch('/tasks/{task_id}')
async def edit_task(task_id: int, task: TodoBase, db: Session = Depends(get_db)):
    db_todos = db.query(models.Todos).filter(models.Todos._id == task_id).first()
    
    if db_todos is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_todos.task = task.task
    db_todos.rate = task.rate
    db_todos.done = task.done

    db.commit()
    db.refresh(db_todos)

    return db_todos  

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_todos = db.query(models.Todos).filter(models.Todos._id == task_id).first()
    if db_todos is None:
        raise HTTPException(status_code=404, detail="Task not found")
     
    db.delete(db_todos)
    db.commit()

    return {"message": "Task deleted successfully"}  
