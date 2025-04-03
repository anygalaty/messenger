from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings

async_engine = create_async_engine(
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
    echo=True,  # TODO отключить после тестирования
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def async_get_db():
    async with async_session() as session:
        yield session
        