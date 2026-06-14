from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from routers import categories, search, sites, graveyard, activity

app = FastAPI(
    title="EverythingMoe Web API",
    description=(
        "An unofficial Web API service providing clean JSON endpoints for everythingmoe.com "
        "built using FastAPI and a Python scraper backend wrapper."
    ),
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount APIRouters
app.include_router(categories.router)
app.include_router(search.router)
app.include_router(sites.router)
app.include_router(graveyard.router)
app.include_router(activity.router)


@app.get("/", include_in_schema=False)
def index_redirect():
    """Redirect home route to Interactive OpenAPI Swagger docs."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["System"], summary="API health status check")
def health_check():
    """Verify backend and scrapers are operational."""
    return {"status": "healthy", "service": "everythingmoe-web-api"}
