from time import time # 현재 시간을 가져오기 위한 time 모듈 import
from fastapi import HTTPException, status # FastAPI에서 예외 처리 및 상태 코드를 사용하기 위한 모듈 import
from jose import jwt # python-jose 라이브러리에서 JWT 인코딩/디코딩 기능 import
from config.settings import Settings # 환경 설정 및 시크릿 키를 가져오는 Settings 클래스 import

# 설정 인스턴스 생성 (예: settings.SECRET_KEY 접근용)
settings = Settings()

# JWT 토큰 생성 함수
def create_jwt_token(email: str, user_id: int, role: str) -> str:
    # payload: 토큰 안에 담을 데이터 정의 (발급 시각 iat, 만료 시각 exp 포함)
    payload = {
        "sub": str(user_id),  # 사용자 ID (subject)
        "user": email,             # 사용자 이메일
        "user_id": user_id,        # 사용자 ID
        'role': role,
        "iat": time(),             # 발급 시각 (issued at)
        "exp": time() + 3600       # 만료 시각 (현재 시각 + 1시간)
    }
    # payload를 기반으로 JWT 토큰 생성 (HS256 알고리즘 사용)
    token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    return token

# JWT 토큰 검증 함수
def verify_jwt_token(token: str):
    try:
        # 전달받은 토큰을 디코딩하여 payload 추출
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        exp = payload.get("exp")  # 만료 시각 추출

        # 만료 시각이 없으면 잘못된 토큰으로 간주
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )

        # 현재 시간이 만료 시각보다 크면 토큰 만료 처리
        if time() > exp:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expired"
            )

        return payload  # 유효한 경우 payload 반환

    except:
        # 디코딩 실패 또는 예외 발생 시 400 에러로 응답
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
