import pytest
from unittest.mock import MagicMock, patch
import requests
from app.utils.client import EverythingMoeAPI
from app.utils.exceptions import (
    EverythingMoeError,
    EverythingMoeNetworkError,
    EverythingMoeNotFoundError,
    EverythingMoeParseError,
)
from app.models.schemas import RecentActivity, SearchResult, SiteDetails

@pytest.fixture
def api():
    return EverythingMoeAPI(base_url="https://testmoe.com", timeout=5.0)

def test_api_init():
    api = EverythingMoeAPI(base_url="https://testmoe.com/", timeout=10.0, include_nsfw=False)
    assert api.base_url == "https://testmoe.com"
    assert api.timeout == 10.0
    assert "Cookie" not in api.session.headers

    api_nsfw = EverythingMoeAPI(include_nsfw=True)
    assert api_nsfw.session.headers["Cookie"] == "nsfw=true"

@patch("requests.Session.request")
def test_request_success(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_request.return_value = mock_response

    resp = api._request("GET", "/test-path")
    assert resp == mock_response
    mock_request.assert_called_once_with("GET", "https://testmoe.com/test-path", timeout=5.0)

@patch("requests.Session.request")
def test_request_404(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_request.return_value = mock_response

    with pytest.raises(EverythingMoeNotFoundError):
        api._request("GET", "/not-found")

@patch("requests.Session.request")
def test_request_http_error(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Internal Server Error", response=mock_response)
    mock_request.return_value = mock_response

    with pytest.raises(EverythingMoeNetworkError):
        api._request("GET", "/error")

@patch("requests.Session.request")
def test_request_network_exception(mock_request, api):
    mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(EverythingMoeNetworkError):
        api._request("GET", "/disconnect")

@patch("requests.Session.request")
def test_get_categories(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <body>
            <select id="section-input">
                <option value="streaming">Anime</option>
                <option value="manga">Manga</option>
            </select>
        </body>
    </html>
    """
    mock_request.return_value = mock_response

    cats = api.get_categories()
    assert cats == {"streaming": "Anime", "manga": "Manga"}
    mock_request.assert_called_once_with("GET", "https://testmoe.com/", timeout=5.0)

@patch("requests.Session.request")
def test_get_categories_parse_error(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>No select tag here</html>"
    mock_request.return_value = mock_response

    with pytest.raises(EverythingMoeParseError):
        api.get_categories()

@patch("requests.Session.request")
def test_get_category_items(mock_request, api):
    # Setup mocks for two requests:
    # 1. Homepage GET
    # 2. lowsec JSON GET
    mock_resp_home = MagicMock()
    mock_resp_home.status_code = 200
    mock_resp_home.text = """
    <div id="sec-streaming" class="section">
        <div class="section-item" data-rank="1">
            <a href="/s/anikoto" data-link="https://anikototv.to/home">Anikoto</a>
        </div>
    </div>
    """

    mock_resp_lowsec = MagicMock()
    mock_resp_lowsec.status_code = 200
    mock_resp_lowsec.json.return_value = [
        {"id": "otakuu", "title": "Otakuu", "link": "https://otakuu.com"}
    ]

    mock_request.side_effect = [mock_resp_home, mock_resp_lowsec]

    items = api.get_category_items("streaming")
    assert len(items) == 2
    assert items[0].id == "anikoto"
    assert items[0].rank == "1 Streaming"
    assert items[1].id == "otakuu"
    assert items[1].rank == "2 Streaming"

    assert mock_request.call_count == 2
    mock_request.assert_any_call("GET", "https://testmoe.com/", timeout=5.0)
    mock_request.assert_any_call("GET", "https://testmoe.com/data/lowsec/streaming.json", timeout=5.0)

@patch("requests.Session.request")
def test_get_category_items_not_found(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html></html>"
    mock_request.return_value = mock_response

    with pytest.raises(EverythingMoeNotFoundError):
        api.get_category_items("streaming")

@patch("requests.Session.request")
def test_get_graveyard(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <div class="section-item" data-rank="1">
        <a href="/s/AniWave" data-link="https://aniwave.live/">AniWave</a>
    </div>
    """
    mock_request.return_value = mock_response

    dead_items = api.get_graveyard()
    assert len(dead_items) == 1
    assert dead_items[0].id == "AniWave"
    assert dead_items[0].is_dead is True

@patch("requests.Session.request")
def test_search_by_query(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "anikoto", "title": "Anikoto", "link": "https://anikototv.to/home"}
    ]
    mock_request.return_value = mock_response

    results = api.search("anikoto", category="streaming")
    assert len(results) == 1
    assert results[0].id == "anikoto"
    mock_request.assert_called_once_with(
        "POST",
        "https://testmoe.com/backend/search",
        data={"q": "anikoto", "section": "streaming"},
        timeout=5.0
    )

@patch("requests.Session.request")
def test_search_by_tag(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_request.return_value = mock_response

    results = api.search("tag:Torrent")
    assert len(results) == 0
    mock_request.assert_called_once_with(
        "POST",
        "https://testmoe.com/backend/search",
        data={"tag": "Torrent"},
        timeout=5.0
    )

@patch("requests.Session.request")
def test_get_site_details(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <script>
    var siteData = {
        "id": "anikoto",
        "title": "Anikoto",
        "link": "https://anikototv.to/home"
    };
    </script>
    """
    mock_request.return_value = mock_response

    details = api.get_site("anikoto")
    assert details.id == "anikoto"
    assert details.title == "Anikoto"
    mock_request.assert_called_once_with("GET", "https://testmoe.com/s/anikoto", timeout=5.0)

@patch("requests.Session.request")
def test_get_latest_activity(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "changelog": ["123456#Update details"],
        "reviews": [],
        "comments": []
    }
    mock_request.return_value = mock_response

    activity = api.get_latest()
    assert isinstance(activity, RecentActivity)
    assert len(activity.changelog) == 1
    assert activity.changelog[0].message == "Update details"
    mock_request.assert_called_once_with("GET", "https://testmoe.com/comments/api?activity=true", timeout=5.0)

@patch.object(EverythingMoeAPI, "get_categories")
@patch.object(EverythingMoeAPI, "get_category_items")
@patch.object(EverythingMoeAPI, "search")
def test_get_by_genre(mock_search, mock_cat_items, mock_cats, api):
    # Case 1: Genre is a category ID
    mock_cats.return_value = {"streaming": "Anime", "manga": "Manga"}
    mock_cat_items.return_value = [SearchResult(id="x", title="X", url="", icon_url="", rank="", type="manga", filter_tags=[])]
    
    res = api.get_by_genre("manga")
    assert len(res) == 1
    assert res[0].type == "manga"
    mock_cat_items.assert_called_once_with("manga")
    mock_search.assert_not_called()

    # Case 2: Genre is a category label
    mock_cat_items.reset_mock()
    res = api.get_by_genre("Anime")
    assert len(res) == 1
    mock_cat_items.assert_called_once_with("streaming")
    mock_search.assert_not_called()

    # Case 3: Genre is not a category (searches by tag)
    mock_cat_items.reset_mock()
    mock_search.return_value = [SearchResult(id="y", title="Y", url="", icon_url="", rank="", type="streaming", filter_tags=["Torrent"])]
    res = api.get_by_genre("Torrent")
    assert len(res) == 1
    mock_search.assert_called_once_with("tag:Torrent")
    mock_cat_items.assert_not_called()

def test_get_episodes(api):
    # Verify get_episodes returns empty list directly without network request
    episodes = api.get_episodes("anikoto")
    assert episodes == []
