from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_api_client
from models.schemas import RecentActivity
from utils.client import EverythingMoeAPI

router = APIRouter(prefix="/activity", tags=["Activity"])


@router.get("", response_model=RecentActivity, summary="Get recent activity updates")
def get_activity(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch recent changelogs, review submissions, and user comments from EverythingMoe."""
    try:
        return client.get_latest()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch activity: {exc}")
