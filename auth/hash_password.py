# passlib의 CryptContext는 여러 암호화 알고리즘을 관리하고 사용할 수 있게 해주는 클래스입니다
from passlib.context import CryptContext

# 비밀번호 해싱과 검증 기능을 제공하는 클래스 정의
class HashPassword:
    # 클래스 생성자: CryptContext를 초기화
    def __init__(self):
        # bcrypt 알고리즘을 사용하며, deprecated 설정은 자동으로 관리
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # 사용자의 평문 비밀번호를 bcrypt로 해싱하여 반환하는 함수
    def hash_password(self, password: str):
        return self.pwd_context.hash(password)

    # 사용자가 입력한 평문 비밀번호와 저장된 해시된 비밀번호가 일치하는지 검증
    def verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)