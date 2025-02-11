from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from schemas import UserCreate, UserResponse
from models import UserDB
from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError
from security import hash_password

class UserHandler:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> UserResponse:
        existing_user = self.db.query(UserDB).filter(UserDB.email == str(user.email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = UserDB(
            first_name=user.first_name,
            last_name=user.last_name,
            nickname=user.nickname,
            email=str(user.email),  # Convert EmailStr to str
            password=hash_password(user.password),
        )

        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        return UserResponse(
            id=int(new_user.id),
            first_name=str(new_user.first_name),
            last_name=str(new_user.last_name),
            nickname=str(new_user.nickname),
            email=str(new_user.email),
        )

    def get_user(self, user_id: str) -> UserResponse:
        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(
            id=int(user.id),
            first_name=str(user.first_name),
            last_name=str(user.last_name),
            nickname=str(user.nickname),
            email=user.email,
        )

    def update_user(self, user_id: int, user_update: UserCreate) -> UserResponse:
        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.first_name = user_update.first_name
        user.last_name = user_update.last_name
        user.nickname = user_update.nickname
        user.email = user_update.email
        user.password = hash_password(user_update.password)

        try:
            self.db.commit()
            self.db.refresh(user)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

        return UserResponse(
            id=int(user.id),
            first_name=str(user.first_name),
            last_name=str(user.last_name),
            nickname=str(user.nickname),
            email=str(user.email),
        )

    def delete_user(self, user_id: int):
        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        self.db.delete(user)
        self.db.commit()
        return {"message": "User deleted successfully"}

    def list_users(self) -> list[UserResponse]:
        users = self.db.query(UserDB).all()
        return [
            UserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                nickname=user.nickname,
                email=user.email,
            )
            for user in users
        ]