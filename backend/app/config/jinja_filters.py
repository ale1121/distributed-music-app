import os
from datetime import datetime
from zoneinfo import ZoneInfo


TIMEZONE = ZoneInfo(os.getenv("TIMEZONE", "Europe/Bucharest"))

def format_dt(dt: datetime, fmt="%Y-%m-%d %H:%M"):
    """ Date formatter """
    
    if dt is None: return ""
    return dt.astimezone(TIMEZONE).strftime(fmt)
