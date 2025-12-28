import os
from datetime import datetime
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo(os.getenv("TIMEZONE", "Europe/Bucharest"))

def format_dt(dt: datetime, fmt="%Y-%m-%d %H:%M"):
    """ Date formatter """
    
    if dt is None: return ""
    return dt.astimezone(TIMEZONE).strftime(fmt)

def format_duration(seconds: int):
    """ Duration formatter """

    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)

    if h: return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
