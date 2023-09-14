from fastapi import HTTPException
from starlette import status

from . import db_actions
from .auth import authenticate_user, create_access_token

# In-memory cache for response caching
from cachetools import TTLCache
response_cache = TTLCache(maxsize=100, ttl=300)  # 5-minute cache


def create_user_view(user, db):
    db_user = db_actions.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = db_actions.create_user(db=db, user=user)
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


def login_user(user, db):
    user = authenticate_user(user.username, user.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or Password is incorrect!",
                            headers={"WWW-Authenticate": "Bearer"}, )
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


def create_post_for_user(user, post, db):
    return db_actions.create_user_post(db=db, post=post, user_id=user.id)


def list_user_posts(user, db):
    cached_posts = response_cache.get(user.id)
    if cached_posts:
        return cached_posts
    posts = db_actions.get_user_posts(user, db)

    user_posts = {"id": user.id, "username": user.username, "posts": posts}
    # Store the result in the cache
    response_cache[user.id] = user_posts

    return user_posts


def delete_user_post(_id, user, db):
    post = db_actions.get_post(db, _id)

    if not post:
        raise HTTPException(
            status_code=404,
            detail=f"ID {_id}: Does not Exists!"
        )

    if not post.owner_id == user.id:
        raise HTTPException(
            status_code=400,
            detail=f"This post {_id} belongs to another user"
        )

    db_actions.delete_user_post(db, _id)
    return {"detail": "Post has deleted successfully!"}
