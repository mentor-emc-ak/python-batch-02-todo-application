"""Tool functions the AI can call to read and mutate todos.

Each function takes the db session first, returns a plain JSON-serialisable
dict/list, and never raises for "not found" - the model needs to read the
failure and recover, not get a 500.
"""
from typing import Optional

from sqlalchemy.orm import Session

from ..models import TodoModel


def _serialize(todo: TodoModel) -> dict:
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
        "priority": todo.priority,
        "end_time": todo.end_time,
    }


def list_todos(db: Session, completed: Optional[bool] = None) -> list:
    query = db.query(TodoModel)
    if completed is not None:
        query = query.filter(TodoModel.completed == completed)

    return [_serialize(t) for t in query.all()]


def get_todo(db: Session, todo_id: int) -> dict:
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        return {"error": f"No todo with id {todo_id}"}

    return _serialize(todo)


def search_todos(db: Session, query: str) -> list:
    pattern = f"%{query}%"
    todos = (
        db.query(TodoModel)
        .filter(TodoModel.title.ilike(pattern) | TodoModel.description.ilike(pattern))
        .all()
    )

    return [_serialize(t) for t in todos]


def create_todo(
    db: Session,
    title: str,
    description: str = "",
    priority: int = 1,
    end_time: Optional[str] = None,
) -> dict:
    todo = TodoModel(
        title=title,
        description=description,
        priority=priority,
        end_time=end_time,
        completed=False,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    return _serialize(todo)


def update_todo(
    db: Session,
    todo_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[int] = None,
    completed: Optional[bool] = None,
    end_time: Optional[str] = None,
) -> dict:
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        return {"error": f"No todo with id {todo_id}"}

    changes = {
        "title": title,
        "description": description,
        "priority": priority,
        "completed": completed,
        "end_time": end_time,
    }
    for key, value in changes.items():
        if value is not None:
            setattr(todo, key, value)

    db.commit()
    db.refresh(todo)

    return _serialize(todo)


def complete_todo(db: Session, todo_id: int) -> dict:
    return update_todo(db, todo_id, completed=True)


def delete_todo(db: Session, todo_id: int) -> dict:
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        return {"error": f"No todo with id {todo_id}"}

    deleted = _serialize(todo)
    db.delete(todo)
    db.commit()

    return {"deleted": deleted}
