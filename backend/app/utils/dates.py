from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc)


def ensure_aware_utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def validate_date_range(start_date, end_date):
    if start_date and end_date and start_date > end_date:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="start_date cannot be after end_date")