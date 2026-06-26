from datetime import datetime


def utc_timestamp() -> str:
    return datetime.utcnow().isoformat()
