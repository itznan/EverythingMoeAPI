from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_api_client
from app.models.schemas import ChangelogRSS, FullChangelogEntry
from app.utils.client import EverythingMoeAPI

router = APIRouter(prefix="/changelog", tags=["Changelog"])


@router.get("", response_model=ChangelogRSS, summary="Get changelog RSS feed")
def get_changelog(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch the recent changelog items from EverythingMoe RSS feed."""
    try:
        return client.get_changelog()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch changelog: {exc}")


@router.get("/full", response_model=List[FullChangelogEntry], summary="Get complete historical changelog database")
def get_full_changelog(
    action: Optional[str] = Query(None, description="Filter by action type: 'add', 'removed', 'rejected', 're-add', 'updated', or 'other'"),
    limit: Optional[int] = Query(None, ge=1, le=5000, description="Limit number of returned entries"),
    client: EverythingMoeAPI = Depends(get_api_client),
):
    """Fetch all 2,500+ historical directory update logs from the EverythingMoe changelog database."""
    try:
        return client.get_full_changelog(action=action, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch complete changelog: {exc}")

