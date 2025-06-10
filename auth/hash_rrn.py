from passlib.context import CryptContext
from cryptography.fernet import Fernet
from config.settings import settings

# class HashRrn:
#     def __init__(self):
#         self.rrn_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#     def hash_rrn(self, rrn: str):
#         return self.rrn_context.hash(rrn)
    
#     def verify_rrn(self, plain_rrn: str, hashed_rrn: str):
#         return self.rrn_context.verify(plain_rrn, hashed_rrn)

# Fernet 인스턴스 생성
fernet = Fernet(settings.rrn_secret_key.encode())

# 주민번호 암호화
def encrypt_rrn(rrn: str) -> str:
    return fernet.encrypt(rrn.encode()).decode()

# 주민번호 복호화
def decrypt_rrn(encrypted_rrn: str) -> str:
    print("[🔓 복호화 시도]", encrypted_rrn)
    return fernet.decrypt(encrypted_rrn.encode()).decode()