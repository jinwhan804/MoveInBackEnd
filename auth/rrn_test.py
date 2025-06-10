from cryptography.fernet import Fernet, InvalidToken

key = "bN30FgDgikd03_RiU0a0PdhYN4w0fAPaqeo6SGIc1Nk="
fernet = Fernet(key.encode())

try:
    token = fernet.encrypt(b"900101-1234567")
    print("[✅ 암호화]:", token)
    print("[🔓 복호화]:", fernet.decrypt(token).decode())
except InvalidToken:
    print("❌ 키가 틀렸습니다.")