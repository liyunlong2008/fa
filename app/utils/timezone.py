from datetime import datetime, timezone
from typing import Union, Optional


def utc_now() -> datetime:
    """获取当前UTC时间"""
    return datetime.now(timezone.utc)


def utc_timestamp() -> int:
    """获取当前UTC时间戳（毫秒）"""
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def datetime_to_timestamp(dt: Optional[datetime] = None) -> int:
    """
    将datetime对象转换为时间戳（毫秒）

    Args:
        dt: datetime对象，如果为None则使用当前UTC时间

    Returns:
        时间戳（毫秒）
    """
    if dt is None:
        dt = utc_now()
    elif dt.tzinfo is None:
        # 如果没有时区信息，假设是UTC时间
        dt = dt.replace(tzinfo=timezone.utc)

    return int(dt.timestamp() * 1000)


def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
    """
    将时间戳转换为datetime对象（UTC）

    Args:
        timestamp: 时间戳（毫秒或秒）

    Returns:
        UTC时间的datetime对象
    """
    # 如果是毫秒时间戳，转换为秒
    if timestamp > 1e10:
        timestamp = timestamp / 1000

    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
