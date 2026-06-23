from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Optional
import re

from app.api.dependencies import get_api_client
from app.models.schemas import SiteStats, StatsHistory
from app.utils.client import EverythingMoeAPI
from app.utils.exceptions import EverythingMoeNotFoundError

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("", response_model=SiteStats, summary="Get current site-wide statistics")
def get_stats(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch the latest aggregate statistics for the EverythingMoe directory.

    Includes total site entries, category count, registered users, total comments,
    and total reviews. The ``time`` field is a Unix timestamp of the last update.
    """
    try:
        return client.get_stats()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {exc}")


@router.get(
    "/history/{date}",
    response_model=StatsHistory,
    summary="Get historical statistics for a specific date",
)
def get_stats_history(
    date: str = Path(
        ...,
        description="Date in YYYYMMDD format (e.g. 20260617)",
        pattern=r"^\d{8}$",
    ),
    client: EverythingMoeAPI = Depends(get_api_client),
):
    """Fetch a historical snapshot of EverythingMoe statistics for a given date.

    The date must be in **YYYYMMDD** format (e.g. ``20260617``).
    Returns 404 if no snapshot exists for the requested date.
    """
    if not re.match(r"^\d{8}$", date):
        raise HTTPException(status_code=422, detail="Date must be in YYYYMMDD format, e.g. 20260617")
    try:
        return client.get_stats_history(date)
    except EverythingMoeNotFoundError:
        raise HTTPException(status_code=404, detail=f"No stats history found for date: {date}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats history: {exc}")
