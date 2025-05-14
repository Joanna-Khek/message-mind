from datetime import datetime, time
from zoneinfo import ZoneInfo
from bson import ObjectId


def get_today_utc_date():
    """
    Get the current time in Singapore timezone.
    """
    utc_time = ZoneInfo("UTC")
    today = datetime.now(utc_time).date()
    date = datetime.combine(today, time(0, 0), tzinfo=utc_time)
    return date


def convert_objectids(obj):
    """
    Convert ObjectId instances in a dictionary or list to strings.
    """
    if isinstance(obj, dict):
        return {k: convert_objectids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectids(v) for v in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj
