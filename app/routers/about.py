from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.dependencies import get_api_client
from app.models.schemas import InfoSection
from app.utils.client import EverythingMoeAPI

router = APIRouter(tags=["About & Info"])


@router.get("/info", response_model=List[InfoSection], summary="Get About & Info page details")
def get_info_page(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch and parse sections, ranking criteria, and disclaimer text from the EverythingMoe About page."""
    try:
        return client.get_info_page()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch About page details: {exc}")


@router.get("/kuroiru", response_model=List[InfoSection], summary="Get Kuroiru tracking sub-project details")
def get_kuroiru_page(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch and parse features, tracking info, and specs of the EverythingMoe Kuroiru sub-project."""
    try:
        return client.get_kuroiru_page()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Kuroiru sub-project details: {exc}")
