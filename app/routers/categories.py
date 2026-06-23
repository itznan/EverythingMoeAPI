from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List

from app.api.dependencies import get_api_client
from app.models.schemas import SearchResult
from app.utils.client import EverythingMoeAPI
from app.utils.exceptions import EverythingMoeNotFoundError

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=Dict[str, str], summary="List all categories")
def get_categories(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch all available categories mapping ID to human-readable names."""
    try:
        return client.get_categories()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {exc}")


@router.get("/{category}/items", response_model=List[SearchResult], summary="List items in a category")
def get_category_items(category: str, client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch all active items (both high-rank and low-rank) listed under a specific category."""
    try:
        return client.get_category_items(category)
    except EverythingMoeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch category items: {exc}")
