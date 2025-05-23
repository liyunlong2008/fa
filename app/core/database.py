from sqlmodel import SQLModel, Session, create_engine
from typing import Generator, Any
from contextlib import asynccontextmanager
from .config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# 创建所有表
def create_db_and_tables():
    """创建数据库和表"""
    SQLModel.metadata.create_all(engine)

# 获取数据库会话
def get_session() -> Generator[Session, None, None]:
    """获取数据库会话"""
    with Session(engine) as session:
        yield session


# 获取异步数据库会话
@asynccontextmanager
async def get_async_session():
    """获取异步数据库会话

    这个函数返回一个可在异步上下文中使用的数据库会话。
    使用方式：
    ```
    async with get_async_session() as session:
        # 使用session进行数据库操作
    ```
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()