# 수정 적용: 주민번호 암호화 후 저장
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlmodel import Session, select
from typing import List, Optional

from auth.authenticate import authenticate
from database.connection import get_session
from models.MoveInInfo import MoveInInfo, MoveInInfoUpdate, MoveInInfoResponse
from models.users import User
from auth.hash_rrn import encrypt_rrn, decrypt_rrn  # 새 유틸 함수 임포트

moveininfo_router = APIRouter(tags=["MoveIn"])

# 전입 신고 등록
@moveininfo_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_movein(
    data: MoveInInfo,
    user_id: int = Depends(authenticate),
    session: Session = Depends(get_session)
) -> dict:

    # 주민번호 암호화
    if data.rrn:
        try:
            data.rrn = encrypt_rrn(data.rrn)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"주민번호 암호화 실패: {str(e)}")

    data.regDt = datetime.now()
    data.userId = user_id
    session.add(data)
    session.commit()
    session.refresh(data)

    return {"message": "전입 신고 등록이 완료되었습니다."}

# 신고 내역 삭제
@moveininfo_router.delete("/{moveIn_id}")
async def delete_movein(moveIn_id: int, session: Session = Depends(get_session)) -> dict:
    moveIn = session.get(MoveInInfo, moveIn_id)
    if moveIn:
        session.delete(moveIn)
        session.commit()
        return {"message": "해당 전입 신고 내역이 삭제되었습니다."}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="데이터가 존재하지 않습니다.")

# 신고 내역 수정
@moveininfo_router.put("/{moveIn_id}", response_model=MoveInInfo)
async def update_event(data: MoveInInfoUpdate, moveIn_id: int = Path(...), session: Session = Depends(get_session)) -> MoveInInfo:
    moveIn = session.get(MoveInInfo, moveIn_id)
    if moveIn:
        moveIn_data = data.model_dump(exclude_unset=True)

        for key, value in moveIn_data.items():
            if key == "rrn" and value:
                try:
                    value = encrypt_rrn(value)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"주민번호 암호화 실패: {str(e)}")
            setattr(moveIn, key, value)

        session.add(moveIn)
        session.commit()
        session.refresh(moveIn)
        return moveIn

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일치하는 전입 신고 내역을 찾을 수 없습니다.")

# 전입신청 목록 (검색 포함)
@moveininfo_router.get("/", response_model=List[MoveInInfo])
def list_moveins(name: Optional[str] = Query(None), session: Session = Depends(get_session), user_id: int = Depends(authenticate)):
    query = select(MoveInInfo)
    if name:
        query = query.where(MoveInInfo.name.contains(name))
    return session.exec(query).all()

# 전입신고 상세 조회
@moveininfo_router.get("/{movein_id}", response_model=MoveInInfoResponse)
def detail_movein(
    movein_id: int,
    session: Session = Depends(get_session),
    user_id: int = Depends(authenticate)
):
    print(f"[📥 상세조회 요청] movein_id={movein_id}, user_id={user_id}")
    
    movein = session.get(MoveInInfo, movein_id)
    if not movein:
        raise HTTPException(status_code=404, detail="해당 신청 정보를 찾을 수 없습니다.")

    try:
        print(f"[✅ 복호화 시도]: {movein.rrn}")
        movein.rrn = decrypt_rrn(movein.rrn)
        print(f"[✅ 복호화 성공]: {movein.rrn}")
    except Exception as e:
        print(f"[❌ 복호화 실패]: {e}")
        movein.rrn = "복호화 실패"

    return movein

# 전입신고 승인
@moveininfo_router.put("/approval/{movein_id}", status_code=status.HTTP_200_OK)
async def approve_movein(movein_id: int, session: Session = Depends(get_session), user_id: int = Depends(authenticate)):
    movein = session.get(MoveInInfo, movein_id)
    if not movein:
        raise HTTPException(status_code=404, detail="해당 전입 신고 내역을 찾을 수 없습니다.")

    movein.isApproval = True
    movein.approvalDt = datetime.now()
    session.add(movein)
    session.commit()
    session.refresh(movein)

    return movein