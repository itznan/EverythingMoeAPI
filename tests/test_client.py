import pytest
from unittest.mock import MagicMock, patch
import httpx
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
    assert "Cookie" not in api.client.headers

    api_nsfw = EverythingMoeAPI(include_nsfw=True)
    assert api_nsfw.client.headers["Cookie"] == "nsfw=true"

def test_api_context_manager():
    with EverythingMoeAPI(base_url="https://testmoe.com") as client:
        assert client.base_url == "https://testmoe.com"
        assert not client.client.is_closed
    assert client.client.is_closed

@patch("httpx.Client.request")
def test_request_success(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_request.return_value = mock_response

    resp = api._request("GET", "/test-path")
    assert resp == mock_response
    mock_request.assert_called_once_with("GET", "https://testmoe.com/test-path")

@patch("httpx.Client.request")
def test_request_404(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_request.return_value = mock_response

    with pytest.raises(EverythingMoeNotFoundError):
        api._request("GET", "/not-found")

@patch("httpx.Client.request")
def test_request_http_error(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Internal Server Error", request=MagicMock(), response=mock_response
    )
    mock_request.return_value = mock_response

    with pytest.raises(EverythingMoeNetworkError):
        api._request("GET", "/error")

@patch("httpx.Client.request")
def test_request_network_exception(mock_request, api):
    mock_request.side_effect = httpx.ConnectError("Connection failed")

    with pytest.raises(EverythingMoeNetworkError):
        api._request("GET", "/disconnect")

@patch("httpx.Client.request")
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
    mock_request.assert_called_once_with("GET", "https://testmoe.com/")

@patch("httpx.Client.request")
def test_get_categories_parse_error(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>No select tag here</html>"
    mock_request.return_value = mock_response

    with pytest.raises(EverythingMoeParseError):
        api.get_categories()

@patch("httpx.Client.request")
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
    mock_request.assert_any_call("GET", "https://testmoe.com/")
    mock_request.assert_any_call("GET", "https://testmoe.com/data/lowsec/streaming.json")

@patch("httpx.Client.request")
def test_get_category_items_not_found(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html></html>"
    mock_request.return_value = mock_response

    with pytest.raises(EverythingMoeNotFoundError):
        api.get_category_items("streaming")

@patch("httpx.Client.request")
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

@patch("httpx.Client.request")
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
    )

@patch("httpx.Client.request")
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
    )

@patch("httpx.Client.request")
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
    mock_request.assert_called_once_with("GET", "https://testmoe.com/s/anikoto")

@patch("httpx.Client.request")
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
    mock_request.assert_called_once_with("GET", "https://testmoe.com/comments/api?activity=true")

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

@patch("httpx.Client.request")
def test_get_menu(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": "streaming", "short": "Anime", "color": "#ff0000"}]
    mock_request.return_value = mock_response

    menu = api.get_menu()
    assert len(menu) == 1
    assert menu[0].id == "streaming"
    mock_request.assert_called_once_with("GET", "https://testmoe.com/data/cache/menu.json")

@patch("httpx.Client.request")
def test_get_tags(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Torrent": "Torrent distribution"}
    mock_request.return_value = mock_response

    tags = api.get_tags()
    assert len(tags) == 1
    assert tags[0].tag == "Torrent"
    mock_request.assert_called_once_with("GET", "https://testmoe.com/data/tags.json")

@patch("httpx.Client.request")
def test_get_stats(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"entries": 100, "category": 20, "users": 50, "comments": 300, "reviews": 40, "time": 12345}
    mock_request.return_value = mock_response

    stats = api.get_stats()
    assert stats.entries == 100
    mock_request.assert_called_once_with("GET", "https://testmoe.com/data/cache/site-stats.json")

@patch("httpx.Client.request")
def test_get_stats_history(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"entries": 90, "category": 19, "users": 40, "comments": 200, "reviews": 30, "time": 12300}
    mock_request.return_value = mock_response

    history = api.get_stats_history("20260101")
    assert history.entries == 90
    assert history.date == "20260101"
    mock_request.assert_called_once_with("GET", "https://testmoe.com/data/cache/statshistory/20260101.json")

@patch("httpx.Client.request")
def test_get_site_expand(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"positive": ["Fast"], "negative": ["Ads"]}
    mock_request.return_value = mock_response

    expand = api.get_site_expand("anikoto")
    assert expand.positive_reviews == ["Fast"]
    mock_request.assert_called_once_with("GET", "https://testmoe.com/data/expand/anikoto.json")

@patch("httpx.Client.request")
def test_get_site_comment_count(mock_request, api):
    mock_tc = MagicMock(status_code=200)
    mock_tc.json.return_value = {"/s/anikoto": 15}
    mock_trc = MagicMock(status_code=200)
    mock_trc.json.return_value = {}
    mock_request.side_effect = [mock_tc, mock_trc]

    cc = api.get_site_comment_count("anikoto")
    assert cc.comment_count == 15
    assert cc.site_id == "anikoto"

@patch("httpx.Client.request")
def test_get_changelog(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <rss><channel>
        <item>
            <title>Added new site</title>
            <link>https://everythingmoe.com</link>
            <guid>123</guid>
            <pubDate>2026-01-01</pubDate>
        </item>
    </channel></rss>
    """
    mock_request.return_value = mock_response

    cl = api.get_changelog()
    assert len(cl.items) == 1
    assert cl.items[0].title == "Added new site"
    mock_request.assert_called_once_with("GET", "https://static.everythingmoe.com/feeds/changelog.xml")

@patch("httpx.Client.request")
def test_get_detector_status(mock_request, api):
    mock_status = MagicMock(status_code=200)
    mock_status.json.return_value = {
        "lastCronStartAt": 100,
        "lastCronAt": 101,
        "lastCronMs": 5,
        "sites": [{"id": "anikoto", "url": "https://anikoto.com", "keyword": "anime", "ping": True, "isApi": False, "status": "up"}]
    }
    mock_hist = MagicMock(status_code=200)
    mock_hist.json.return_value = {"history": {"https://anikoto.com": ["up", "up"]}}
    mock_request.side_effect = [mock_status, mock_hist]

    status = api.get_detector_status(include_history=True)
    assert len(status.sites) == 1
    assert status.sites[0].id == "anikoto"
    assert status.sites[0].history == ["up", "up"]

@patch.object(EverythingMoeAPI, "get_detector_status")
def test_get_site_detector_status(mock_get_det, api):
    from app.models.schemas import DetectorStatus, DetectorSiteStatus
    mock_get_det.return_value = DetectorStatus(
        last_cron_start_at=100,
        last_cron_at=101,
        last_cron_ms=5,
        sites=[DetectorSiteStatus(id="anikoto", url="https://anikoto.com", keyword="anime", ping=True, status="up")]
    )
    site_status = api.get_site_detector_status("anikoto")
    assert site_status.id == "anikoto"

    with pytest.raises(EverythingMoeNotFoundError):
        api.get_site_detector_status("nonexistent")

@patch("httpx.Client.request")
def test_get_articles(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<div><a href="/post/test.html"><h3>Guide to Anime</h3></a><div class="about-gray">2026-01-01</div></div>'
    mock_request.return_value = mock_response

    articles = api.get_articles()
    assert len(articles) == 1
    assert articles[0].title == "Guide to Anime"
    mock_request.assert_called_once_with("GET", "https://testmoe.com/post/")

@patch("httpx.Client.request")
def test_get_cache_main(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"anikoto": {"positive": ["Fast"]}, "sectionstreaming": [{"id": "anikoto"}]}
    mock_request.return_value = mock_response

    data = api.get_cache_main()
    assert "anikoto" in data.sites
    mock_request.assert_called_once_with("GET", "https://testmoe.com/data/cache/main.json")

@patch("httpx.Client.request")
def test_get_cache_dead(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"aniwave": {"positive": ["Archive"]}, "sectiondead": [{"id": "aniwave"}]}
    mock_request.return_value = mock_response

    data = api.get_cache_dead()
    assert "aniwave" in data.sites
    mock_request.assert_called_once_with("GET", "https://testmoe.com/data/cache/dead.json")

@patch("httpx.Client.request")
def test_post_telemetry(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_request.return_value = mock_response

    resp = api.post_telemetry({"screen": "1920x1080"})
    assert resp == {"status": "ok"}
    mock_request.assert_called_once_with("POST", "https://testmoe.com/backend/info", data={"screen": "1920x1080"})

@patch("httpx.Client.request")
def test_post_suggestion(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response

    resp = api.post_suggestion("add", "Please add site X", "token123")
    assert resp == {"status": "success"}
    mock_request.assert_called_once_with(
        "POST",
        "https://testmoe.com/backend/api",
        data={"suggesttype": "add", "suggestion": "Please add site X", "Ttoken": "token123"}
    )

@patch("httpx.Client.request")
def test_get_info_page(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<div id="about-base"><h2>About Us</h2><p>Description text</p></div>'
    mock_request.return_value = mock_response

    sections = api.get_info_page()
    assert len(sections) == 1
    assert sections[0].title == "About Us"
    mock_request.assert_called_once_with("GET", "https://testmoe.com/post/info.html")

@patch("httpx.Client.request")
def test_get_kuroiru_page(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<div id="about-base"><h2>Kuroiru Tracker</h2><p>Tracker details</p></div>'
    mock_request.return_value = mock_response

    sections = api.get_kuroiru_page()
    assert len(sections) == 1
    assert sections[0].title == "Kuroiru Tracker"
    mock_request.assert_called_once_with("GET", "https://testmoe.com/post/kuroiru.html")

@patch("httpx.Client.request")
def test_get_site_thread(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "title": "Anikoto Thread",
        "post": [{"id": 1, "message": "hello", "created": 123, "username": "Tester"}]
    }
    mock_request.return_value = mock_response

    thread = api.get_site_thread("anikoto")
    assert thread.title == "Anikoto Thread"
    assert len(thread.posts) == 1
    mock_request.assert_called_once_with("GET", "https://testmoe.com/comments/cache/s-anikoto.json")

@patch("httpx.Client.request")
def test_get_full_changelog(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "100#add > Site A\n200#removed > Site B\n"
    mock_request.return_value = mock_response

    cl = api.get_full_changelog(action="add", limit=5)
    assert len(cl) == 1
    assert cl[0].action_type == "add"
    mock_request.assert_called_once_with("GET", "https://testmoe.com/data/changelog/changelog.txt")

@patch("httpx.Client.request")
def test_get_rules_page(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<div id="about-base"><h2>Guidelines</h2><p>Rules</p></div>'
    mock_request.return_value = mock_response

    sections = api.get_rules_page()
    assert len(sections) == 1
    assert sections[0].title == "Guidelines"
    mock_request.assert_called_once_with("GET", "https://testmoe.com/post/rules.html")

@patch("httpx.Client.request")
def test_get_simple_directory(mock_request, api):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<div class="index-group" id="sec-anime"><span class="index-section">Anime</span><div class="index-grid"><div class="index-item" data-rank="1"><a href="/s/anikoto" data-link="https://anikoto.com">Anikoto</a></div></div></div>'
    mock_request.return_value = mock_response

    res = api.get_simple_directory()
    assert "anime" in res
    assert len(res["anime"]) == 1
    mock_request.assert_called_once_with("GET", "https://testmoe.com/simple")


