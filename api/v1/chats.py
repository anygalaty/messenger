from core.db.db import async_get_db
from fastapi import Depends, APIRouter, HTTPException, status
from models.chat import Chat
from schemas.chat import ChatCreate, ChatOut, ChatType

router = APIRouter()


@router.post("/chats/create", response_model=ChatOut)
async def create_chat(chat: ChatCreate, db=Depends(async_get_db)):
    if len(chat.participants) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough participants")

    new_chat = Chat(
        chat_type=ChatType.personal if len(chat.participants) == 2 else ChatType.group,
        participants=chat.participants,  # TODO перенести в свервис и реализовать логику получения списка юзеров по id
    )
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)
    return ChatOut.from_orm(new_chat)
