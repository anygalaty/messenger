from models.user import User
from sqlalchemy import select
from schemas.user import UserCreate, UserOut
from core.security import hash_password
from fastapi import HTTPException, status


async def create_user(user: UserCreate, db) -> UserOut:
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserOut.from_orm(new_user)


async def get_user_by_email(email: str, db) -> UserOut | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def register_user(user: UserCreate, db) -> UserOut | HTTPException:
    check_user = await get_user_by_email(user.email, db)
    if check_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already in use')

    new_user = await create_user(user, db)
    return new_user


async def get_users_by_ids(users_ids: list[str], db) -> list[User]:
    stmt = select(User).where(
        User.id.in_(users_ids)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
