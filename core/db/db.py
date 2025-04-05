from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import db_settings

async_engine = create_async_engine(
    f"postgresql+asyncpg://{db_settings.user}:{db_settings.password}@"
    f"{db_settings.host}:{db_settings.port}/{db_settings.name}",
    echo=True,  # TODO отключить после тестирования
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def async_get_db():
    async with async_session() as session:
        yield session
        