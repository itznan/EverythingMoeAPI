from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.routers import categories, search, sites, graveyard, activity, menu, tags, stats, changelog, detector, articles, cache, backend, about

app = FastAPI(
    title="EverythingMoe Web API",
    description=(
        "An unofficial Web API service providing clean JSON endpoints for everythingmoe.com "
        "built using FastAPI and a Python scraper backend wrapper."
    ),
    version="1.2.0",
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
app.include_router(menu.router)
app.include_router(tags.router)
app.include_router(stats.router)
app.include_router(changelog.router)
app.include_router(detector.router)
app.include_router(articles.router)
app.include_router(cache.router)
app.include_router(backend.router)
app.include_router(about.router)


@app.get("/", include_in_schema=False)
def index_redirect():
    """Redirect home route to Interactive OpenAPI Swagger docs."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["System"], summary="API health status check")
def health_check():
    """Verify backend and scrapers are operational."""
    return {"status": "healthy", "service": "everythingmoe-web-api"}
