import os
import json
import shutil
from pathlib import Path
from datetime import datetime

import mimetypes
from uuid import uuid4

from auth.authenticate import authenticate
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, Session
from typing import List, Optional

from models.users import User
from models.files import Files
from database.connection import get_session
from auth.hash_password import HashPassword
from auth.jwt_handler import create_jwt_token, verify_jwt_token
from service.s3_service import upload_file_to_s3, delete_file_from_s3

# tag은 API 문서화에 사용되는 태그 ( docs 상에 같은 태그로 묶임 )
user_router = APIRouter(tags=["User"])

# 비밀번호 해시 유틸
hash_password = HashPassword()  

# 회원가입 API
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_new_user(
    data: str = Form(...),
    image: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    Authorization: Optional[str] = Header(None)  # 관리자 인증 헤더 받기
) -> dict:
    # JSON 파싱
    try:
        parsed = json.loads(data)
        email = parsed.get("email")
        if not email:
            raise ValueError("이메일이 누락되었습니다.")
    except Exception:
        raise HTTPException(status_code=400, detail="요청 데이터 형식이 잘못되었습니다.")

    # 관리자 권한 체크 (권한 없으면 403)
    if Authorization:
        try:
            token = Authorization.replace("Bearer ", "")
            payload = verify_jwt_token(token)
            if payload.get("role") != "Y":
                raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다.")
        except Exception as e:
            raise HTTPException(status_code=403, detail=f"권한 확인 실패: {str(e)}")
    else:
        raise HTTPException(status_code=403, detail="토큰이 필요합니다.")

    # 이메일 중복 검사
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="동일한 사용자가 존재합니다.")

    # 사용자 등록 (flush로 ID 확보)
    new_user = User(
        username=parsed.get("username"),
        email=email,
        password=hash_password.hash_password(parsed.get("password")),
        role=parsed.get("role", "N"),
        created_at=datetime.utcnow()
    )
    session.add(new_user)
    session.flush()  # ID 확보 (commit은 나중에 한 번만)

    # 이미지 업로드 및 파일 테이블 저장
    file_url = None
    if image:
        try:
            file_size = str(image.size)
            file_url = upload_file_to_s3(image.file, image.filename)

            file_name = os.path.basename(file_url)
            file_path = "/".join(file_url.split("/")[:-1])
            org_file_name = image.filename

            new_file = Files(
                userId=new_user.id,
                fileName=file_name,
                filePath=file_path,
                orgFileName=org_file_name,
                fileSize=file_size,
                fileUrl=file_url
            )
            session.add(new_file)
        except Exception as e:
            session.rollback()
            print(f"S3 파일 업로드 또는 Files 객체 생성 중 오류: {e}")
            raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"!!! 데이터베이스 커밋 실패 오류: {e}")
        print(f"!!! 오류 타입: {type(e)}")
        raise HTTPException(status_code=500, detail=f"사용자 등록 중 데이터베이스 오류: {str(e)}")

    return {
        "message": "사용자 등록이 완료되었습니다.",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
            "profile_image_url": file_url
        }
    }

# 사용자 로그인
@user_router.post("/signin")
async def sign_in(data: OAuth2PasswordRequestForm = Depends(), session = Depends(get_session)) -> dict:
    statement = select(User).where(User.email == data.username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="사용자를 찾을 수 없습니다.")    

    # if user.password != data.password:
    if hash_password.verify_password(data.password, user.password) == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="패스워드가 일치하지 않습니다.")
    
    return {
        "message": "로그인에 성공했습니다.",
        "username": user.username,
        "user_id": user.id, #추가
        "email": user.email, #추가
        "role": user.role,
        # "access_token": create_jwt_token(user.email, user.id),
        "access_token": create_jwt_token(user.email, user.id, user.role),  # JWT 토큰 생성
    }

@user_router.get("/profile")
async def get_profile(Authorization: str = Header(...), session: Session = Depends(get_session)):
    try:
        # Bearer 토큰에서 토큰만 추출
        token = Authorization.replace("Bearer ", "")
        payload = verify_jwt_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="토큰이 유효하지 않습니다.")

        # 사용자 조회
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 프로필 이미지 조회 (없을 수도 있음)
        file = session.exec(select(Files).where(Files.userId == user.id)).first()

        return {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "profile_image_url": file.fileUrl if file else None
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@user_router.put("/profile", status_code=200)
async def update_profile(
    data: str = Form(...),
    image: Optional[UploadFile] = File(None),
    Authorization: str = Header(...),
    session: Session = Depends(get_session)
):
    try:
        token = Authorization.replace("Bearer ", "")
        payload = verify_jwt_token(token)
        user_id = payload.get("sub")

        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        parsed = json.loads(data)
        new_username = parsed.get("username")

        if new_username:
            user.username = new_username

        # 이미지 수정
        if image:
            # 기존 이미지 삭제
            old_file = session.exec(select(Files).where(Files.userId == user.id)).first()
            if old_file:
                delete_file_from_s3(old_file.fileUrl)
                session.delete(old_file)

            # 새 이미지 업로드
            file_url = upload_file_to_s3(image.file, image.filename)
            file_name = os.path.basename(file_url)
            file_path = "/".join(file_url.split("/")[:-1])
            file_size = str(image.size)

            new_file = Files(
                userId=user.id,
                fileName=file_name,
                filePath=file_path,
                orgFileName=image.filename,
                fileSize=file_size,
                fileUrl=file_url
            )
            session.add(new_file)

        session.commit()

        return {"message": "프로필이 성공적으로 수정되었습니다."}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"프로필 수정 실패: {str(e)}")

# 사용자 목록 조회
@user_router.get("/", response_model=List[User])
async def list_users(session: Session = Depends(get_session), user_id: int = Depends(authenticate)):
    user = session.get(User, user_id)
    if (user.role != 'Y'):  
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
    users = session.exec(select(User)).all()
    return users

# 사용자 삭제
@user_router.delete("/{userId}", status_code=status.HTTP_200_OK)
async def delete_user(userId: int, session: Session = Depends(get_session)):
    user = session.get(User, userId)
    if not user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")

    file = session.exec(select(Files).where(Files.userId == userId)).first()
    if file:
        try:
            delete_file_from_s3(file.fileUrl)  # ✅ 속성명 수정
            session.delete(file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"S3 파일 삭제 실패: {str(e)}")

    session.delete(user)
    session.commit()
    return {"message": "사용자가 삭제되었습니다."}
