from models.chat import ChatParticipant
from schemas.message import MessageOut, MessageCreate
from core.db.db import async_get_db
from models.message import Message, MessageRead
from fastapi import HTTPException, status
from core.constants import MAX_MESSAGE_LENGTH
from services.chat_service import check_user
from sqlalchemy import select, update, exists
from services.user_service import get_users_by_ids
from services.chat_service import get_chat_participants, get_chat_by_id


async def create_message(message: MessageCreate, db: async_get_db) -> MessageOut | None:
    if len(message.text) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Message too long')
    new_message = Message(
        chat_id=message.chat_id,
        sender_id=message.sender_id,
        text=message.text
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return MessageOut.from_orm(new_message)


async def get_messages_history(
        chat_id: str,
        user_id: str,
        limit: int,
        offset: int,
        db: async_get_db
) -> list[MessageOut]:
    await check_user(user_id, chat_id, db)
    stmt = select(Message).where(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return [MessageOut.from_orm(msg) for msg in messages]


async def get_messages_history_payload(
        chat_id: str,
        limit: int,
        db: async_get_db
) -> dict:
    stmt = select(Message).where(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    messages = result.scalars().all()
    user_ids = list({m.sender_id for m in messages})
    users = await get_users_by_ids(user_ids, db)
    user_map = {u.id: {"name": u.name, "email": u.email} for u in users}
    history_payload = {
        "event": "history",
        "messages": [
            {
                "id": msg.id,
                "chat_id": msg.chat_id,
                "sender_id": msg.sender_id,
                "sender_name": user_map.get(msg.sender_id, {}).get("name", "Unknown"),
                "sender_email": user_map.get(msg.sender_id, {}).get("email", ""),
                "text": msg.text,
                "created_at": msg.created_at.strftime("%d.%m.%Y, %H:%M"),
                "is_read": msg.is_read,
            }
            for msg in messages
        ]
    }

    return history_payload


async def mark_as_read(user_id: str, message_id: str, db: async_get_db):
    stmt_check = select(MessageRead).where(
        MessageRead.message_id == message_id,
        MessageRead.user_id == user_id
    )
    result = await db.execute(stmt_check)

    if not result.scalar():
        new_mark = MessageRead(message_id=message_id, user_id=user_id)
        db.add(new_mark)

        stmt = update(Message).where(
            Message.id == message_id
        ).values(is_read=True)
        await db.execute(stmt)

        await db.commit()
        await db.refresh(new_mark)

    return {
        "event": "read",
        "message_id": message_id
    }


async def get_unread_chats_for_user(user_id: str, db: async_get_db) -> list[str]:
    stmt_participated = select(ChatParticipant.chat_id).where(ChatParticipant.user_id == user_id)
    result = await db.execute(stmt_participated)
    chat_ids = [row[0] for row in result.all()]

    unread_chat_ids = set()

    for chat_id in chat_ids:
        stmt_unread = select(Message.id).where(
            Message.chat_id == chat_id,
            ~exists().where(
                (MessageRead.message_id == Message.id) &
                (MessageRead.user_id == user_id)
            ),
            Message.sender_id != user_id
        ).limit(1)

        result_unread = await db.execute(stmt_unread)
        if result_unread.first():
            unread_chat_ids.add(chat_id)

    return list(unread_chat_ids)


async def get_fully_read_messages(message_id: str, participants: list[str], db) -> bool:
    stmt_msg = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt_msg)
    message = result.scalar_one_or_none()

    if not message:
        return False

    expected_readers = set(participants) - {message.sender_id}

    if not expected_readers:
        return False

    stmt_reads = select(MessageRead.user_id).where(MessageRead.message_id == message_id)
    result = await db.execute(stmt_reads)
    actual_readers = set(row[0] for row in result.fetchall())

    return expected_readers.issubset(actual_readers)


async def build_and_broadcast_message(
        data: dict,
        chat_id: str,
        db,
        chat_ws_manager,
        get_user_by_id_func):
    new_message = MessageCreate(
        chat_id=chat_id,
        sender_id=data["sender_id"],
        text=data["text"]
    )
    created_message = await create_message(new_message, db)
    user = await get_user_by_id_func(data["sender_id"], db)

    data['sender_name'] = user.name
    data['sender_email'] = user.email
    data['created_at'] = created_message.created_at.strftime("%d.%m.%Y, %H:%M")
    data['id'] = created_message.id

    await chat_ws_manager.broadcast(chat_id, data)
    return created_message


async def notify_unread_chats(chat_id: str, sender_id: str, db, status_ws_manager):
    participants = await get_chat_participants(chat_id, db)
    for user_id in participants:
        if user_id != sender_id:
            await status_ws_manager.send_to_user(user_id, {
                "event": "unread_chats",
                "chat_ids": [chat_id]
            })


async def handle_message_read(user_id: str, message_id: str, chat_id: str, db, chat_ws_manager, status_ws_manager):
    payload = await mark_as_read(user_id, message_id, db)
    payload["user_id"] = user_id
    await chat_ws_manager.broadcast(chat_id, payload)

    participants = await get_chat_participants(chat_id, db)
    fully_read = await get_fully_read_messages(message_id, participants, db)
    if fully_read:
        chat = await get_chat_by_id(chat_id, db)

        participants_names = await get_users_by_ids(participants, db)
        name_map = {u.id: u.name for u in participants_names}

        for participant_id in participants:
            if participant_id != user_id:
                await status_ws_manager.send_to_user(participant_id, {
                    "event": "fully_read",
                    "message_id": message_id,
                    "chat_id": chat_id,
                    "chat_name": f"{chat.chat_type.capitalize()} чат с "
                                 f"{', '.join(name for uid, name in name_map.items() if uid != participant_id)}"
                })
