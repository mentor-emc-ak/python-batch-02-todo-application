from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import TodoModel
from ..schemas import TodoCreateOrUpdate, TodoResponse

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("", response_model=List[TodoResponse]) # /todos
def get_todos(db: Session = Depends(get_db)):
    return db.query(TodoModel).all()


@router.get("/{todo_id}", response_model=TodoResponse) # /todos/{todo_id}
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return todo


@router.post("", response_model=TodoResponse)
def create_todo(todo: TodoCreateOrUpdate, db: Session = Depends(get_db)):
    new_todo = TodoModel(**todo.dict())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoCreateOrUpdate, db: Session = Depends(get_db)):
    existing_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    for key, value in todo.dict().items():
        setattr(existing_todo, key, value)

    db.commit()
    db.refresh(existing_todo)

    return existing_todo


@router.delete("/{todo_id}", response_model=TodoResponse)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    existing_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(existing_todo)
    db.commit()

    return existing_todo
