from datetime import datetime
from zoneinfo import ZoneInfo


def calculate_cursor(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
) -> int:
    dt = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo("Asia/Taipei"))
    timestamp_ms = int(dt.timestamp() * 1000)
    seconds, milliseconds = divmod(timestamp_ms, 1000)
    cursor = (seconds << 20) | milliseconds

    return cursor
