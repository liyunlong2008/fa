import redis
from .config import settings

# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

# 创建Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)

# 会话存储相关方法
class RedisSession:
    """Redis会话管理类"""

    @staticmethod
    def set_session(session_id: str, data: dict, expire: int = 1800):
        """设置会话数据"""
        redis_client.hmset(f"session:{session_id}", data)
        redis_client.expire(f"session:{session_id}", expire)

    @staticmethod
    def get_session(session_id: str) -> dict:
        """获取会话数据"""
        data = redis_client.hgetall(f"session:{session_id}")
        return data

    @staticmethod
    def delete_session(session_id: str):
        """删除会话数据"""
        redis_client.delete(f"session:{session_id}")

    @staticmethod
    def update_session_expire(session_id: str, expire: int = 1800):
        """更新会话过期时间"""
        redis_client.expire(f"session:{session_id}", expire)