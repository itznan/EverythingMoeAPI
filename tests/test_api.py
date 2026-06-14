import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import get_api_client
from models.schemas import SearchResult, SiteDetails, Review, Screenshot, RecentActivity, ChangelogEntry
from utils.exceptions import EverythingMoeNotFoundError

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
