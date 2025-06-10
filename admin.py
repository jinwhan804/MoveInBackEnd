from auth import hash_password
from database.connection import SessionLocal
from models.users import User
from sqlmodel import Session, select


# 관리자 계정 생성
def create_admin_user():
    session: Session = SessionLocal()
    search_admin = session.exec(select(User).where(User.role == "Y")).first()

    hasher = hash_password.HashPassword()
    if not search_admin:
        admin_user = User(
            username="admin",
            email="admin@test.com",
            password=hasher.hash_password("1234"),
            role="Y",
        )
        session.add(admin_user)
        session.commit()
        session.refresh(admin_user)