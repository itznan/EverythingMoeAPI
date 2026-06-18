from fastapi import APIRouter, Depends, HTTPException
from typing import List

from api.dependencies import get_api_client
from models.schemas import CategoryMenuItem
from utils.client import EverythingMoeAPI

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("", response_model=List[CategoryMenuItem], summary="Get category navigation menu")
def get_menu(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch the site's category navigation menu entries.

    Each item includes the category ID, display name (short/shortextra),
    accent color, and whether the category is NSFW.
    """
    try:
        return client.get_menu()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch menu: {exc}")
