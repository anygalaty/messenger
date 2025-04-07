from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import db_settings
from core.logger import setup_logging
import logging

setup_logging()
logger = logging.getLogger("db")

async_engine = create_async_engine(
    f"postgresql+asyncpg://{db_settings.user}:{db_settings.password}@"
    f"{db_settings.host}:{db_settings.port}/{db_settings.name}",
    echo=True
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def async_get_db():
    logger.info("Connecting to database")
    async with async_session() as session:
        yield session
    logger.info("Disconnecting from database")
        