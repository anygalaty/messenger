from fastapi import FastAPI
from api.v1.chats import router as chats_router
from api.v1.users import router as users_router

app = FastAPI(title="Messenger")

app.include_router(
    chats_router,
    prefix="/api/v1/chats",
    tags=["chats"]
)

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["users"]
)

