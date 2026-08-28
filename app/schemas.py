from typing import Optional

from pydantic import BaseModel, ConfigDict


class TodoCreateOrUpdate(BaseModel):
    title: str
    description: str
    completed: bool = False
    priority: int = 1
    end_time: Optional[str] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    priority: int
    end_time: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
