from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import TodoModel
from ..openrouter import get_openrouter_response
from ..database import get_db

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("")
def get_ai_response(db: Session = Depends(get_db)):
    todos = db.query(TodoModel).all()
    todo_prompt = []

    for todo in todos:
        todo_prompt.append({
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "completed": todo.completed
        })


    ai_response = get_openrouter_response(f"""
Here are my todos, provide a summary about these, no markdown only text act as my personal assistant
{todo_prompt}
""")
    print(f"AI Response: {ai_response.json()}")

    return ai_response.json()
