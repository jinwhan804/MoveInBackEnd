from config.settings import settings  # 설정 인스턴스 import
from sqlmodel import SQLModel, create_engine, Session  # SQLModel 및 세션 관련 모듈 import
from sqlalchemy.orm import sessionmaker
from models.users import User  # User 모델 import
from models.MoveInInfo import MoveInInfo  # 전입 신고 모델 import
from models.files import Files  # 파일 모델 import

# settings에서 불러온 DB URL로 엔진 생성
engine = create_engine(settings.database_url, echo=True)

# 테이블 생성
def conn():
    SQLModel.metadata.create_all(engine)

# 세션 제공
def get_session():
    with Session(engine) as session:
        yield session

# 세션 로컬 생성
SessionLocal = sessionmaker(bind=engine, class_=Session, autocommit=False, autoflush=False)