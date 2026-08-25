from pydantic import BaseModel


class TodoCreateOrUpdate(BaseModel):
    title: str
    description: str
    completed: bool = False
    priority: int = 1
    end_time: str = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    priority: int
    end_time: str = None

    class Config:
        orm_mode = True
