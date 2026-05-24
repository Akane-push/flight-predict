import datetime
from fastapi import HTTPException, status

def validate_date_format(date_str: str) -> None:
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"[ERROR] Invalid date format: '{date_str}'. Expected YYYY-MM-DD."
        )

def validate_time_format(time_str: str) -> None:
    try:
        datetime.datetime.strptime(time_str, "%H:%M")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"[ERROR] Invalid time format: '{time_str}'. Expected HH:mm."
        )