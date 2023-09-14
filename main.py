from fastapi import Depends
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from app.auth import jwt_auth
from app.database import engine, SessionLocal
from app.db_actions import *
from app.schemas import *
from app.views import *

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Handle payload size limitation using request validation middleware
@app.middleware("http")
async def validate_request_size(request, call_next):
    max_payload_size = 1024 * 1024  # 1 MB
    content_length = int(request.headers.get("content-length", 0))
    if content_length > max_payload_size:
        return JSONResponse(status_code=413, content={'detail': "Payload is larger than 1 MB"})
    return await call_next(request)


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return jwt_auth(token, db)


# Signup endpoint
@app.post("/signup", response_model=Token)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user_view(user, db)


# Login endpoint
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return login_user(form_data, db)


@app.get("/users", response_model=UserBase)
def get_user(user: UserBase = Depends(get_current_user)):
    return user


@app.get("/posts/", response_model=UserPosts)
def list_post(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_user_posts(user, db)


@app.post("/posts/")
def create_post(post: PostBase, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_post_for_user(user, post, db)


@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return delete_user_post(post_id, user, db)
