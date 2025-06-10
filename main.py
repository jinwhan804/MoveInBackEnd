from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from admin import create_admin_user
from routes.users import user_router
from database.connection import conn
from routes.MoveInInfo import moveininfo_router
from routes.users import user_router
from database.connection import conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작될 때 실행되는 코드
    print("애플리케이션 시작")
    conn()

    yield
    # 애플리케이션 종료될 때 실행되는 코드
    print("애플리케이션 종료")


app = FastAPI(lifespan=lifespan)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
# from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    # CORS 설정
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # 허용할 도메인
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"], # 모든 헤더 허용
)

# prefix는 app.py에 설정할 수도 있다.
app.include_router(user_router, prefix="/users")
app.include_router(moveininfo_router, prefix="/movein")

# import 될 때 실행되어서 2번 실행되는 문제를 방지하기 위해 명시적으로 import 할 파일을 직접 실행할 때만 실행되도록 명시적으로 해주는 문법
# 어떻게 실행 되냐에 따라서 __name__이 변경 된다는 것 ( 파이썬을 모듈화해서 직접적으로 호출할 때는 __name__이 __main__으로 바뀌고, import 될 때는 __name__이 모듈 이름으로 바뀜  )
if __name__ == "__main__":
    create_admin_user()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
