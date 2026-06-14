from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_api_client
from models.schemas import SiteDetails
from utils.client import EverythingMoeAPI
from utils.exceptions import EverythingMoeNotFoundError

router = APIRouter(prefix="/sites", tags=["Sites"])


@router.get("/{id_or_slug}", response_model=SiteDetails, summary="Get details of a specific site")
def get_site(id_or_slug: str, client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch complete metadata, reviews, pros/cons, and screenshot urls of an indexed site."""
    try:
        return client.get_site(id_or_slug)
    except EverythingMoeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch site details: {exc}")
