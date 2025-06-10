# config/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 읽기

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    rrn_secret_key: str = os.getenv("RRN_SECRET_KEY")

    # Naver Cloud Platform 설정
    # ncp_access_key: str = os.getenv("NCP_ACCESS_KEY")
    # ncp_secret_key: str = os.getenv("NCP_SECRET_KEY")
    # bucket_name: str = os.getenv("BUCKET_NAME")
    # endpoint_url: str = os.getenv("ENDPOINT_URL")

    # AWS S3 설정
    aws_access_key: str = Field(..., alias="AWS_ACCESS_KEY_ID")
    aws_secret_key: str = Field(..., alias="AWS_SECRET_ACCESS_KEY")
    bucket_name: str = Field(..., alias="BUCKET_NAME")
    endpoint_url: str = Field(..., alias="ENDPOINT_URL")

    class Config:
        env_file = ".env"
        populate_by_name = True  # alias 이름과 변수 이름이 다를 경우 허용

settings = Settings()