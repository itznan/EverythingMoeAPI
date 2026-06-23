from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_api_client
from app.models.schemas import DetectorStatus, DetectorSiteStatus
from app.utils.client import EverythingMoeAPI
from app.utils.exceptions import EverythingMoeNotFoundError

router = APIRouter(prefix="/detector", tags=["Detector"])


@router.get("", response_model=DetectorStatus, summary="Get Downtime Detector status")
def get_detector_status(
    history: bool = Query(True, description="Whether to include check history"),
    client: EverythingMoeAPI = Depends(get_api_client)
):
    """Fetch live uptime monitoring status, ping times, and status history for checked sites."""
    try:
        return client.get_detector_status(include_history=history)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch detector status: {exc}")


@router.get("/{id_or_slug}", response_model=DetectorSiteStatus, summary="Get detector status for a specific site")
def get_site_detector_status(
    id_or_slug: str,
    client: EverythingMoeAPI = Depends(get_api_client)
):
    """Fetch uptime status, keyword details, and ping history for a specific monitored site slug."""
    try:
        return client.get_site_detector_status(id_or_slug)
    except EverythingMoeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch detector status: {exc}")
