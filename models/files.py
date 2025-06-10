from sqlmodel import SQLModel, Field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.users import User

class Files(SQLModel, table=True):
    __tablename__ = "Files"  # 대문자 그대로 사용되도록 명시

    fileSeq: Optional[int] = Field(default=None, primary_key=True, description="저장 순번")
    userId: Optional[int] = Field(default=None, foreign_key="User.id")
    fileName: str = Field(nullable=False, max_length=130, description="저장된 이미지 파일 이름")
    filePath: str = Field(nullable=False, max_length=150, description="저장된 이미지 파일의 파일 저장 경로")
    orgFileName: str = Field(nullable=False, max_length=100, description="원래 파일 이름")
    fileSize: str = Field(nullable=False, max_length=50, description="파일 크기")
    fileUrl: str = Field(nullable=False, max_length=500, description="저장된 이미지 파일 URL")

class FilesInsert(SQLModel):
    userId: Optional[int] = Field(default=None, foreign_key="User.id")
    fileName: str = Field(nullable=False, max_length=130, description="저장된 이미지 파일 이름")
    filePath: str = Field(nullable=False, max_length=150, description="저장된 이미지 파일의 파일 저장 경로")
    orgFileName: str = Field(nullable=False, max_length=100, description="원래 파일 이름")
    fileSize: str = Field(nullable=False, max_length=50, description="파일 크기")
    fileUrl: str = Field(nullable=False, max_length=500, description="저장된 이미지 파일 URL")
