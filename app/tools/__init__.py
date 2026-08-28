"""Registry mapping OpenRouter tool schemas to the functions in todo_tools."""
import json

from sqlalchemy.orm import Session

from . import todo_tools

REGISTRY = {
    "list_todos": todo_tools.list_todos,
    "get_todo": todo_tools.get_todo,
    "search_todos": todo_tools.search_todos,
    "create_todo": todo_tools.create_todo,
    "update_todo": todo_tools.update_todo,
    "complete_todo": todo_tools.complete_todo,
    "delete_todo": todo_tools.delete_todo,
}


def _tool(name, description, properties, required=None):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
            },
        },
    }


TOOL_SCHEMAS = [
    _tool(
        "list_todos",
        "List every todo, optionally filtered by completion state.",
        {"completed": {"type": "boolean", "description": "Only return todos with this completed state."}},
    ),
    _tool(
        "get_todo",
        "Fetch a single todo by its id.",
        {"todo_id": {"type": "integer"}},
        ["todo_id"],
    ),
    _tool(
        "search_todos",
        "Find todos whose title or description contains the given text.",
        {"query": {"type": "string"}},
        ["query"],
    ),
    _tool(
        "create_todo",
        "Create a new todo.",
        {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "priority": {"type": "integer", "description": "1 is lowest. Higher is more urgent."},
            "end_time": {"type": "string", "description": "Due date/time as free text, e.g. 2026-09-01 17:00."},
        },
        ["title"],
    ),
    _tool(
        "update_todo",
        "Update fields on an existing todo. Omitted fields are left unchanged.",
        {
            "todo_id": {"type": "integer"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "priority": {"type": "integer"},
            "completed": {"type": "boolean"},
            "end_time": {"type": "string"},
        },
        ["todo_id"],
    ),
    _tool(
        "complete_todo",
        "Mark a todo as completed.",
        {"todo_id": {"type": "integer"}},
        ["todo_id"],
    ),
    _tool(
        "delete_todo",
        "Permanently delete a todo.",
        {"todo_id": {"type": "integer"}},
        ["todo_id"],
    ),
]


def execute_tool(db: Session, name: str, arguments) -> str:
    """Run one tool call and return its JSON result string for the model."""
    func = REGISTRY.get(name)
    if not func:
        return json.dumps({"error": f"Unknown tool {name}"})

    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments or "{}")
        except json.JSONDecodeError:
            return json.dumps({"error": f"Arguments for {name} were not valid JSON"})

    try:
        result = func(db, **arguments)
    except TypeError as e:
        return json.dumps({"error": f"Bad arguments for {name}: {e}"})
    except Exception as e:
        db.rollback()
        print(f"[Tools] {name} failed: {e}")
        return json.dumps({"error": f"{name} failed: {e}"})

    return json.dumps(result)
