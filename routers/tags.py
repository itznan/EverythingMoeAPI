from fastapi import APIRouter, Depends, HTTPException
from typing import List

from api.dependencies import get_api_client
from models.schemas import TagDefinition
from utils.client import EverythingMoeAPI

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=List[TagDefinition], summary="Get all tag definitions")
def get_tags(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch all tag/filter definitions from EverythingMoe.

    Each tag has a short identifier (e.g. 'nsfw', 'licensed', 'hia') and a
    human-readable description explaining what it means when applied to a site.
    """
    try:
        return client.get_tags()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tags: {exc}")
