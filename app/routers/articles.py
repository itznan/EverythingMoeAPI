from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.dependencies import get_api_client
from app.models.schemas import ArticleEntry
from app.utils.client import EverythingMoeAPI

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("", response_model=List[ArticleEntry], summary="Get all articles and guides")
def get_articles(client: EverythingMoeAPI = Depends(get_api_client)):
    """Fetch all guides, posts, and setup articles published on EverythingMoe."""
    try:
        return client.get_articles()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {exc}")
