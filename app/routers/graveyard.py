from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.dependencies import get_api_client
from app.models.schemas import SearchResult
from app.utils.client import EverythingMoeAPI

router = APIRouter(prefix="/graveyard", tags=["Graveyard"])


@router.get("", response_model=List[SearchResult], summary="List graveyard / dead sites")
def get_graveyard(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch all sites that are marked dead, along with details and links if available."""
    try:
        return client.get_graveyard()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch graveyard: {exc}")
