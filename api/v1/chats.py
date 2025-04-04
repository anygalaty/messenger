from core.db.db import async_get_db
from fastapi import Depends, APIRouter

router = APIRouter()


@router.get("/chats")
async def get_chats():
    return {
        'chats': []
    }
