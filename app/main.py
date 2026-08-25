from fastapi import FastAPI

from .database import Base, engine
from .routes import todos

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API for Python MC Batch 02")

app.include_router(todos.router)
