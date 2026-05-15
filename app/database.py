from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.base_class import Base
from app.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables():


    print(f"Вижу таблицы в Base: {Base.metadata.tables.keys()}")  # Проверка

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы созданы")


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())