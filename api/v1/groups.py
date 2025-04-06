from core.db.db import async_get_db
from fastapi import Depends, APIRouter, Request
from schemas.group import GroupCreate, GroupOut
from services.group_service import create_group as create_group_service
from core.security import require_auth
from services.auth_service import get_user_from_cookie

router = APIRouter()


@router.post("/create", response_model=GroupOut)
@require_auth
async def create_group(request: Request, group: GroupCreate, db=Depends(async_get_db)):
    creator_id = await get_user_from_cookie(request)
    group.participants.append(creator_id)
    new_group = await create_group_service(group, db)
    return new_group
