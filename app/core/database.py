from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
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