from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.dependencies import get_api_client
from app.models.schemas import SearchResult
from app.utils.client import EverythingMoeAPI

router = APIRouter(tags=["Search & Genres"])


@router.get("/search", response_model=List[SearchResult], summary="Search indexed items")
def search_items(q: str, category: str = "any", client: EverythingMoeAPI = Depends(get_api_client)):
    """Search for items by query name or prefix with 'tag:' to search for a specific tag."""
    try:
        return client.search(q, category)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search query failed: {exc}")


@router.get("/genres/{genre}", response_model=List[SearchResult], summary="Filter items by genre or tag")
def get_by_genre(genre: str, client: EverythingMoeAPI = Depends(get_api_client)):
    """Retrieve items matching a genre/tag. If the term matches a category name, it returns the category's items."""
    try:
        return client.get_by_genre(genre)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to filter by genre: {exc}")
