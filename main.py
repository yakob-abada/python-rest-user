from fastapi import FastAPI, Depends
from database import get_db
from handlers import UserHandler
from schemas import UserCreate, UserResponse
from sqlalchemy.orm import Session
from typing import List

app = FastAPI()

def get_handler(db: Session = Depends(get_db)):
    return UserHandler(db)

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, handler: UserHandler = Depends(get_handler)):
    return handler.create_user(user)

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, handler: UserHandler = Depends(get_handler)):
    return handler.get_user(user_id)

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserCreate, handler: UserHandler = Depends(get_handler)):
    return handler.update_user(user_id, user_update)

@app.delete("/users/{user_id}")
def delete_user(user_id: int, handler: UserHandler = Depends(get_handler)):
    return handler.delete_user(user_id)

@app.get("/users", response_model=List[UserResponse])
def list_users(handler: UserHandler = Depends(get_handler)):
    return handler.list_users()
