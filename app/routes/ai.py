from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models import TodoModel
from ..openrouter import get_openrouter_response, chat_completion
from ..database import get_db
from ..tools import TOOL_SCHEMAS, execute_tool

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


class ChatRequest(BaseModel):
    message: str


SYSTEM_PROMPT = """You are the personal assistant inside a todo app.
You can read and change the user's todos by calling the provided tools - do that
instead of guessing or asking the user to do it themselves. Look up ids with
list_todos or search_todos before updating or deleting.
Answer in plain text, no markdown. Keep it short and useful."""

MAX_TOOL_ROUNDS = 5


@router.post("/chat")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": payload.message},
    ]
    used_tools = []

    for _ in range(MAX_TOOL_ROUNDS):
        response = chat_completion(messages, tools=TOOL_SCHEMAS)
        body = response.json()
        print(body)
        try:
            message = body["choices"][0]["message"]
        except (KeyError, IndexError):
            raise HTTPException(status_code=502, detail=f"[AI] unexpected response: {body}")

        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            return {"reply": message.get("content", ""), "tools_used": used_tools}

        messages.append(message)
        for call in tool_calls:
            name = call["function"]["name"]
            result = execute_tool(db, name, call["function"].get("arguments"))
            used_tools.append(name)
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "name": name,
                "content": result,
            })

    raise HTTPException(status_code=502, detail="[AI] gave up after too many tool rounds")
