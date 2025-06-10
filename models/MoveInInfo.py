import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from models.users import User

class MoveInInfo(SQLModel, table=True):
    __tablename__ = "MoveInInfo"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    rrn: str
    email: str
    beforeAddr: str
    afterAddr: str
    regDt: Optional[datetime.datetime]
    approvalDt: Optional[datetime.datetime] = None
    moveInDt: Optional[datetime.datetime]
    isApproval: Optional[bool] = None
    # user_id: Optional[int] = Field(default=None, foreign_key="User.id")
    userId: int = Field(foreign_key="User.id", alias="userId")


# 전입 신고 수정 모델
class MoveInInfoUpdate(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    rrn: Optional[str]
    email: Optional[EmailStr]
    beforeAddr: Optional[str]
    afterAddr: Optional[str]
    regDt: Optional[datetime.datetime]
    approvalDt: Optional[datetime.datetime]
    moveInDt: Optional[datetime.date]
    isApproval: Optional[bool]   

class MoveInInfoResponse(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    rrn: Optional[str]
    email: Optional[EmailStr]
    beforeAddr: Optional[str]
    afterAddr: Optional[str]
    regDt: Optional[datetime.datetime]
    approvalDt: Optional[datetime.datetime]
    moveInDt: Optional[datetime.date]
    isApproval: Optional[bool] 
    userId: int = Field(foreign_key="User.id", alias="userId")