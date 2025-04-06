from core.db.db import async_get_db
from fastapi import Depends, APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from schemas.group import GroupCreate, GroupOut
from services.group_service import create_group as create_group_service
from core.security import require_auth
from services.auth_service import get_user_from_cookie

router = APIRouter()


@router.post("/create", response_model=GroupOut)
@require_auth
async def create_group(
        request: Request,
        name: str = Form(...),
        group_type: str = Form(...),
        participants: str = Form(...),
        db=Depends(async_get_db)
):
    creator_id = await get_user_from_cookie(request)
    participants_list = [p.strip() for p in participants.split(",") if p.strip()]
    group = GroupCreate(
        name=name,
        creator_id=creator_id,
        group_type=group_type,
        participants=participants_list
    )
    group.participants.append(creator_id)
    await create_group_service(group, db)
    return RedirectResponse(url='/messenger', status_code=status.HTTP_303_SEE_OTHER)
    # TODO лучше редиректить в группу  
