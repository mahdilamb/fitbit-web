"""Utility functions for the Web client."""
import datetime
import urllib.parse
from typing import Annotated, Any, Literal


def format_date(
    date: datetime.date | Literal["today"] | Annotated[str, "yyyy-MM-dd"]
) -> str:
    """Format a date."""
    if date == "today":
        date = datetime.datetime.now().date()
    if not isinstance(date, datetime.date):
        date = datetime.datetime.strptime(date, r"%Y-%m-%d").date()
    return f"{date:%Y-%m-%d}"


def format_time(time: datetime.time | Annotated[str, "HH:mm"]) -> str:
    """Format a time."""
    if not isinstance(time, datetime.time):
        time = datetime.datetime.strptime(time, r"%H:%M").time()
    return f"{time:%H:%M}"


def format_timestamp(
    timestamp: datetime.datetime | Annotated[str, "yyyy-MM-ddTHH:mm:ss"]
) -> str:
    """Format a timestamp."""
    if not isinstance(timestamp, datetime.datetime):
        timestamp = datetime.datetime.strptime(timestamp, r"%Y-%m-%dT%H:%M:%S")
    return f"{timestamp:%Y-%m-%dT%H:%M:%S}"


def format_date_or_timestamp(
    date_or_timestamp: datetime.datetime
    | Annotated[str, "yyyy-MM-ddTHH:mm:ss"]
    | datetime.date
    | Literal["today"]
    | Annotated[str, "yyyy-MM-dd"]
    | None
):
    """Format a date or timestamp."""
    if date_or_timestamp is None:
        return None
    try:
        if not isinstance(date_or_timestamp, datetime.date):
            return format_timestamp(date_or_timestamp)
    except ValueError:
        return format_date(date_or_timestamp)


def format_url(
    url: str,
    param_kwargs: dict[str, Any] | None = None,
    query_kwargs: dict[str, Any] | None = None,
):
    """Format the url."""
    if not url.startswith("http"):
        url = "https://api.fitbit.com/" + url.lstrip("/")
    url = url.format(**filter_dict(param_kwargs))
    if query_kwargs:
        url += "?" + urllib.parse.urlencode(filter_dict(query_kwargs))
    return url


def filter_dict(dictionary: dict[str, Any | None] | None) -> dict[str, Any]:
    """Remove `None` values from a dictionary."""
    return {k: v for k, v in (dictionary or {}).items() if v is not None}

