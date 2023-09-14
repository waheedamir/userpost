from pydantic import BaseModel, Field


class PostBase(BaseModel):
    content: str = Field(min_length=5)


class Post(PostBase):
    id: int


class UserBase(BaseModel):
    username: str = Field(min_length=5)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100)


class User(UserCreate):
    id: int


class UserPosts(UserBase):
    id: int
    posts: list[Post] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None
