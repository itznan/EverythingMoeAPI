from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_api_client
from models.schemas import SiteDetails, SiteExpand, SiteCommentCount
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


@router.get("/{id_or_slug}/expand", response_model=SiteExpand, summary="Get expand data for a site")
def get_site_expand(id_or_slug: str, client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch lightweight expanded pros/cons/info/alternative-links for a site directly from /data/expand/.

    This is a fast alternative to GET /sites/{id} — it avoids scraping the full site page.
    Works for both active sites and dead (graveyard) sites.
    """
    try:
        return client.get_site_expand(id_or_slug)
    except EverythingMoeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch expand data: {exc}")


@router.get("/{id_or_slug}/comments", response_model=SiteCommentCount, summary="Get comment count for a site")
def get_site_comment_count(id_or_slug: str, client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch the number of user comments posted on a specific site's page."""
    try:
        return client.get_site_comment_count(id_or_slug)
    except EverythingMoeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch comment count: {exc}")
