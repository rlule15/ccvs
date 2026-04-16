from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import user_routes
from app.db.db_config import Base, engine

Base.metadata.create_all(engine)

app = FastAPI(title="Collaborative Chess Voting System", version="1.0.0")

app.add_middleware(
    SessionMiddleware,
    secret_key="my-super-secret-key",
    session_cookie="ccvs_session",
    max_age=3600,
    same_site="lax",
    https_only=False,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/")
def health_check():
    return {"message": "Hello World!"}


app.include_router(user_routes.router, prefix="/api/v1/users", tags=["users"])
