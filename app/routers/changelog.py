from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_api_client
from app.models.schemas import ChangelogRSS
from app.utils.client import EverythingMoeAPI

router = APIRouter(prefix="/changelog", tags=["Changelog"])


@router.get("", response_model=ChangelogRSS, summary="Get full changelog")
def get_changelog(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch the full changelog from EverythingMoe RSS feed."""
    try:
        return client.get_changelog()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch changelog: {exc}")
