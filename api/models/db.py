from sqlalchemy import exc
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from setting import settings

engine = create_async_engine(
    settings.DB_URL,
    echo=True,
)

SessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,

)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        except exc.SQLAlchemyError as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
