from fastapi import APIRouter, Depends, HTTPException, Request
from urllib.parse import parse_qsl

from app.api.dependencies import get_api_client
from app.utils.client import EverythingMoeAPI

router = APIRouter(prefix="/backend", tags=["Backend Actions"])


@router.post("/info", summary="Post client telemetry statistics")
async def post_telemetry(request: Request, client: EverythingMoeAPI = Depends(get_api_client)):
    """Submit client platform telemetry parameters (ref, screen, ispwa, bookmark, platform, out, pageType)."""
    try:
        body_bytes = await request.body()
        payload = dict(parse_qsl(body_bytes.decode("utf-8")))
        return client.post_telemetry(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to submit telemetry: {exc}")


@router.post("/api", summary="Submit suggestion report")
async def post_suggestion(request: Request, client: EverythingMoeAPI = Depends(get_api_client)):
    """Submit site addition, edit, or report suggestion to EverythingMoe backend.

    Accepts form parameters:
    - **suggesttype**: The submission category ('add', 'edit', 'remove', 'info', 'general', 'inquiry').
    - **suggestion**: Detailed message contents (prefixed with domain if applicable).
    - **Ttoken**: Cloudflare Turnstile verification token.
    """
    try:
        body_bytes = await request.body()
        form_data = dict(parse_qsl(body_bytes.decode("utf-8")))
        
        suggest_type = form_data.get("suggesttype", "")
        suggestion = form_data.get("suggestion", "")
        t_token = form_data.get("Ttoken", "")

        if not suggest_type or not suggestion:
            raise HTTPException(status_code=400, detail="Missing suggesttype or suggestion form parameters.")

        return client.post_suggestion(suggest_type, suggestion, t_token)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to submit suggestion: {exc}")

