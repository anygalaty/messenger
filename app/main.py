from fastapi import FastAPI
from api.v1.chats import router as chats_router
from api.v1.users import router as users_router
from api.v1.auth import router as auth_router
from api.v1.messages import router as messages_router
from api.v1.views import router as views_router


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

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["auth"]
)

app.include_router(
    messages_router,
    prefix="/api/v1/messages",
    tags=["messages"]
)

app.include_router(
    views_router,
    tags=["views"]
)

# TODO сделать механизм 'typing...'