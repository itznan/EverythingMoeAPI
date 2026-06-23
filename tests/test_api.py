import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.dependencies import get_api_client
from app.models.schemas import SearchResult, SiteDetails, Review, Screenshot, RecentActivity, ChangelogEntry, DetectorStatus, ArticleEntry, DetectorSiteStatus, CacheData, InfoSection
from app.utils.exceptions import EverythingMoeNotFoundError

mock_client = MagicMock()

# Configure dependency override for testing
app.dependency_overrides[get_api_client] = lambda: mock_client

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "everythingmoe-web-api"}


def test_index_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_get_categories():
    mock_client.get_categories.return_value = {"streaming": "Anime", "manga": "Manga"}
    response = client.get("/categories")
    assert response.status_code == 200
    assert response.json() == {"streaming": "Anime", "manga": "Manga"}
    mock_client.get_categories.assert_called_once()


def test_get_category_items_success():
    mock_client.get_category_items.return_value = [
        SearchResult(
            id="anikoto",
            title="Anikoto",
            url="https://anikoto.com",
            icon_url="",
            rank="1 Streaming",
            type="streaming",
            filter_tags=["Self-host"],
            is_nsfw=False,
            is_licensed=False,
            is_dead=False
        )
    ]
    response = client.get("/categories/streaming/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "anikoto"
    mock_client.get_category_items.assert_called_once_with("streaming")


def test_get_category_items_not_found():
    mock_client.get_category_items.side_effect = EverythingMoeNotFoundError("Category not found")
    response = client.get("/categories/invalid/items")
    assert response.status_code == 404
    assert "Category not found" in response.json()["detail"]


def test_search_items():
    mock_client.search.return_value = []
    response = client.get("/search?q=anikoto&category=streaming")
    assert response.status_code == 200
    assert response.json() == []
    mock_client.search.assert_called_once_with("anikoto", "streaming")


def test_get_by_genre():
    mock_client.get_by_genre.return_value = []
    response = client.get("/genres/Torrent")
    assert response.status_code == 200
    assert response.json() == []
    mock_client.get_by_genre.assert_called_once_with("Torrent")


def test_get_site_details_success():
    mock_client.get_site.return_value = SiteDetails(
        id="anikoto",
        title="Anikoto",
        url="https://anikoto.com",
        icon_url="",
        rank="1 Streaming",
        type="streaming",
        filter_tags=[],
        positive_reviews=[],
        negative_reviews=[],
        info_notes=[],
        alternative_links={},
        screenshots=[],
        user_reviews=[],
        is_dead=False
    )
    response = client.get("/sites/anikoto")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "anikoto"
    mock_client.get_site.assert_called_once_with("anikoto")


def test_get_site_details_not_found():
    mock_client.get_site.side_effect = EverythingMoeNotFoundError("Site not found")
    response = client.get("/sites/invalid")
    assert response.status_code == 404
    assert "Site not found" in response.json()["detail"]


def test_get_graveyard():
    mock_client.get_graveyard.return_value = []
    response = client.get("/graveyard")
    assert response.status_code == 200
    assert response.json() == []
    mock_client.get_graveyard.assert_called_once()


def test_get_activity():
    mock_client.get_latest.return_value = RecentActivity(
        changelog=[ChangelogEntry(timestamp=123, message="Test msg")],
        reviews=[],
        comments=[]
    )
    response = client.get("/activity")
    assert response.status_code == 200
    data = response.json()
    assert len(data["changelog"]) == 1
    assert data["changelog"][0]["message"] == "Test msg"
    mock_client.get_latest.assert_called_once()


def test_get_detector_status():
    mock_client.get_detector_status.return_value = DetectorStatus(
        last_cron_start_at=123,
        last_cron_at=456,
        last_cron_ms=789,
        sites=[]
    )
    response = client.get("/detector?history=true")
    assert response.status_code == 200
    data = response.json()
    assert data["last_cron_start_at"] == 123
    mock_client.get_detector_status.assert_called_once_with(include_history=True)


def test_get_articles():
    mock_client.get_articles.return_value = [
        ArticleEntry(title="Guide", url="http://test.com", date="2026-06-23", icons=[])
    ]
    response = client.get("/articles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Guide"
    mock_client.get_articles.assert_called_once()


def test_get_site_detector_status_success():
    mock_client.get_site_detector_status.reset_mock()
    mock_client.get_site_detector_status.return_value = DetectorSiteStatus(
        id="anikoto",
        url="https://anikoto.com",
        keyword="Top",
        ping=True,
        is_api=False,
        status="up",
        response_ms=100,
        down_since=None,
        history=[]
    )
    response = client.get("/detector/anikoto")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "anikoto"
    mock_client.get_site_detector_status.assert_called_once_with("anikoto")


def test_get_site_detector_status_not_found():
    mock_client.get_site_detector_status.reset_mock()
    mock_client.get_site_detector_status.side_effect = EverythingMoeNotFoundError("Site not found")
    response = client.get("/detector/invalid")
    assert response.status_code == 404
    assert "Site not found" in response.json()["detail"]
    mock_client.get_site_detector_status.assert_called_once_with("invalid")


def test_get_cache_main():
    mock_client.get_cache_main.reset_mock()
    mock_client.get_cache_main.return_value = CacheData(sites={}, sections={})
    response = client.get("/cache/main")
    assert response.status_code == 200
    assert response.json() == {"sites": {}, "sections": {}}
    mock_client.get_cache_main.assert_called_once()


def test_get_cache_dead():
    mock_client.get_cache_dead.reset_mock()
    mock_client.get_cache_dead.return_value = CacheData(sites={}, sections={})
    response = client.get("/cache/dead")
    assert response.status_code == 200
    assert response.json() == {"sites": {}, "sections": {}}
    mock_client.get_cache_dead.assert_called_once()


def test_post_telemetry():
    mock_client.post_telemetry.reset_mock()
    mock_client.post_telemetry.return_value = {"status": "ok"}
    response = client.post("/backend/info", data={"pageType": "idx", "out": "/test"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_client.post_telemetry.assert_called_once_with({"pageType": "idx", "out": "/test"})


def test_post_suggestion_success():
    mock_client.post_suggestion.reset_mock()
    mock_client.post_suggestion.return_value = {"success": True}
    response = client.post("/backend/api", data={
        "suggesttype": "general",
        "suggestion": "nice site",
        "Ttoken": "token123"
    })
    assert response.status_code == 200
    assert response.json() == {"success": True}
    mock_client.post_suggestion.assert_called_once_with("general", "nice site", "token123")


def test_post_suggestion_missing_params():
    response = client.post("/backend/api", data={"suggesttype": "general"})
    assert response.status_code == 400
    assert "Missing suggesttype or suggestion" in response.json()["detail"]


def test_get_info_page():
    mock_client.get_info_page.reset_mock()
    mock_client.get_info_page.return_value = [
        InfoSection(title="Section A", content=["Info A"])
    ]
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Section A"
    mock_client.get_info_page.assert_called_once()


def test_get_kuroiru_page():
    mock_client.get_kuroiru_page.reset_mock()
    mock_client.get_kuroiru_page.return_value = [
        InfoSection(title="Tracker", content=["MAL Sync"])
    ]
    response = client.get("/kuroiru")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Tracker"
    mock_client.get_kuroiru_page.assert_called_once()



