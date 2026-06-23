from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_api_client
from app.models.schemas import CacheData
from app.utils.client import EverythingMoeAPI

router = APIRouter(prefix="/cache", tags=["Cache Databases"])


@router.get("/main", response_model=CacheData, summary="Get full main site cache database")
def get_cache_main(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch the full main site cache database, containing detailed expands for active sites and section listings."""
    try:
        return client.get_cache_main()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch main cache database: {exc}")


@router.get("/dead", response_model=CacheData, summary="Get full dead site cache database")
def get_cache_dead(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch the full dead site cache database, containing detailed expands for shutdown sites and section listings."""
    try:
        return client.get_cache_dead()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dead cache database: {exc}")
