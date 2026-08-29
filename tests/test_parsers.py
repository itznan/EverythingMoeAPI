import pytest
from app.utils.parsers import (
    parse_categories,
    parse_section_items,
    parse_lowsec_items,
    parse_graveyard_items,
    parse_search_results,
    parse_site_data,
    parse_activity,
    parse_altlinks,
    parse_detector_status,
    parse_articles,
    parse_cache_data,
    parse_info_page,
    parse_thread_comments,
    parse_full_changelog,
    parse_simple_directory,
)
from app.models.schemas import SearchResult, SiteDetails, Review, Screenshot, ThreadDetails, ThreadComment, FullChangelogEntry

def test_parse_categories():
    html = """
    <html>
        <body>
            <select id="section-input">
                <option value="any">Any</option>
                <option value="streaming">Anime</option>
                <option value="manga">Manga</option>
            </select>
        </body>
    </html>
    """
    cats = parse_categories(html)
    assert cats == {"streaming": "Anime", "manga": "Manga"}

def test_parse_categories_empty():
    assert parse_categories("<html></html>") == {}

def test_parse_section_items():
    html = """
    <div id="sec-streaming" class="section">
        <div class="section-item" data-rank="1" data-filter="Scraper,Self-host">
            <a href="/s/anikoto" data-link="https://anikototv.to/home">
                <img src="/icons/anikoto.png" />
                Anikoto
            </a>
        </div>
        <div class="section-item section-expandbtn">
            <button class="section-morebtn" onclick="expandsection(this, 'streaming', 22)">More</button>
        </div>
    </div>
    """
    items, found = parse_section_items(html, "streaming")
    assert found is True
    assert len(items) == 1
    item = items[0]
    assert isinstance(item, SearchResult)
    assert item.id == "anikoto"
    assert item.title == "Anikoto"
    assert item.url == "https://anikototv.to/home"
    assert item.icon_url == "/icons/anikoto.png"
    assert item.rank == "1 Streaming"
    assert item.type == "streaming"
    assert item.filter_tags == ["Scraper", "Self-host"]
    assert item.is_nsfw is False
    assert item.is_licensed is False
    assert item.is_dead is False

def test_parse_section_items_not_found():
    items, found = parse_section_items("<html></html>", "streaming")
    assert found is False
    assert items == []

def test_parse_lowsec_items():
    data = [
        {
            "id": "otakuu",
            "title": "Otakuu",
            "link": "https://otakuu.com",
            "icon": "/icons/otakuu.png",
            "filter": "Dub friendly",
            "tags": "nsfw licensed dead"
        }
    ]
    items = parse_lowsec_items(data, "streaming", 22)
    assert len(items) == 1
    item = items[0]
    assert item.id == "otakuu"
    assert item.title == "Otakuu"
    assert item.url == "https://otakuu.com"
    assert item.icon_url == "/icons/otakuu.png"
    assert item.rank == "22 Streaming"
    assert item.type == "streaming"
    assert item.filter_tags == ["Dub friendly"]
    assert item.is_nsfw is True
    assert item.is_licensed is True
    assert item.is_dead is True

def test_parse_graveyard_items():
    html = """
    <div class="section-item" data-rank="1">
        <a href="/s/AniWave" data-link="https://aniwave.live/">
            <img src="/icons/aniwave.png" />
            AniWave
        </a>
    </div>
    """
    items = parse_graveyard_items(html)
    assert len(items) == 1
    item = items[0]
    assert item.id == "AniWave"
    assert item.title == "AniWave"
    assert item.url == "https://aniwave.live/"
    assert item.rank == "1 Dead"
    assert item.is_dead is True

def test_parse_search_results():
    data = [
        {
            "id": "anikoto",
            "title": "Anikoto",
            "link": "https://anikototv.to/home",
            "icon": "/icons/anikoto.png",
            "rank": "1 Anime",
            "type": "streaming",
            "filter": "Scraper,Self-host",
            "tags": "nsfw"
        }
    ]
    results = parse_search_results(data)
    assert len(results) == 1
    r = results[0]
    assert r.id == "anikoto"
    assert r.is_nsfw is True
    assert r.is_dead is False

def test_parse_altlinks():
    assert parse_altlinks("mirrors<<https://anikoto.site#anisuge<</anisuge.tv", "https://base.com") == {
        "mirrors": "https://anikoto.site",
        "anisuge": "https://base.com/anisuge.tv"
    }
    assert parse_altlinks("") == {}
    assert parse_altlinks(None) == {}

def test_parse_site_data():
    html = """
    <script>
    var siteData = {
        "id": "anikoto",
        "title": "Anikoto",
        "link": "https://anikototv.to/home",
        "icon": "/icons/anikoto.png",
        "rank": "1 Streaming",
        "type": "streaming",
        "filter": "Scraper,Self-host",
        "expand": {
            "positive": "Large library#Provides both soft & hard subs",
            "negative": "Bad ads",
            "info": "Notes",
            "altlink": "mirrors<<https://anikoto.site#anisuge<</anisuge.tv"
        },
        "ss": [
            {"img": "desk1.png", "type": "desk"}
        ],
        "reviews": [
            {
                "id": 123,
                "name": "fred",
                "type": "1",
                "review": "good sub",
                "time": 1780000000,
                "pic": "pic1.png",
                "vote": 5
            }
        ]
    };
    </script>
    """
    details = parse_site_data(html, "https://base.com")
    assert details is not None
    assert isinstance(details, SiteDetails)
    assert details.id == "anikoto"
    assert details.positive_reviews == ["Large library", "Provides both soft & hard subs"]
    assert details.negative_reviews == ["Bad ads"]
    assert details.info_notes == ["Notes"]
    assert details.alternative_links == {
        "mirrors": "https://anikoto.site",
        "anisuge": "https://base.com/anisuge.tv"
    }
    assert len(details.screenshots) == 1
    assert details.screenshots[0] == Screenshot(img="desk1.png", type="desk")
    assert len(details.user_reviews) == 1
    assert details.user_reviews[0] == Review(
        id=123,
        name="fred",
        rating=1,
        review_text="good sub",
        time=1780000000,
        has_pic=True,
        votes=5
    )

def test_parse_site_data_not_found():
    assert parse_site_data("<html></html>") is None

def test_parse_activity():
    data = {
        "changelog": [
            "1780045556#removed > Kagane",
            "invalid_timestamp#something changed"
        ],
        "reviews": [{"id": 1}],
        "comments": [{"id": 2}]
    }
    act = parse_activity(data)
    assert len(act.changelog) == 2
    assert act.changelog[0].timestamp == 1780045556
    assert act.changelog[0].message == "removed > Kagane"
    assert act.changelog[1].timestamp == 0
    assert act.changelog[1].message == "something changed"
    assert act.reviews == [{"id": 1}]
    assert act.comments == [{"id": 2}]


def test_parse_detector_status():
    status_data = {
        "lastCronStartAt": 100,
        "lastCronAt": 200,
        "lastCronMs": 300,
        "sites": [
            {
                "url": "http://test.com",
                "keyword": "Test",
                "ping": True,
                "isApi": False,
                "status": "up",
                "responseMs": 50,
                "downSince": None,
                "id": "TestSite"
            }
        ]
    }
    history_data = {
        "history": {
            "http://test.com": ["up", "up"]
        }
    }
    status = parse_detector_status(status_data, history_data)
    assert status.last_cron_start_at == 100
    assert len(status.sites) == 1
    assert status.sites[0].id == "TestSite"
    assert status.sites[0].history == ["up", "up"]


def test_parse_articles():
    html = """
    <a href="/post/test.html"><div class="icons-box"><img src="/icons/test.png"></div>
    <h3>Test Article</h3></a>
    <div class="about-gray">23 Jun 2026</div>
    """
    articles = parse_articles(html, "http://base.com")
    assert len(articles) == 1
    assert articles[0].title == "Test Article"
    assert articles[0].url == "http://base.com/post/test.html"
    assert articles[0].date == "23 Jun 2026"
    assert articles[0].icons == ["http://base.com/icons/test.png"]


def test_parse_cache_data():
    raw_data = {
        "anikoto": {
            "positive": "Good pros#Excellent subtitles",
            "negative": "Ads",
            "info": "Some info notes",
            "altlink": "mirror<<https://anikoto.com"
        },
        "sectionanime": [
            {
                "id": "animepahe",
                "title": "AnimePahe",
                "link": "https://animepahe.com",
                "icon": "https://static.com/icon.png",
                "DEAD": False
            }
        ]
    }
    cache = parse_cache_data(raw_data, "https://everythingmoe.com")
    assert len(cache.sites) == 1
    assert "anikoto" in cache.sites
    assert cache.sites["anikoto"].positive_reviews == ["Good pros", "Excellent subtitles"]
    assert len(cache.sections) == 1
    assert "sectionanime" in cache.sections
    assert cache.sections["sectionanime"][0].title == "AnimePahe"
    assert cache.sections["sectionanime"][0].DEAD is False


def test_parse_info_page():
    html = """
    <div id="about-base">
        <h2>Section Title 1</h2>
        Paragraph text description.
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
        </ul>
        <a href="http://link.com">Click here</a>
    </div>
    """
    sections = parse_info_page(html)
    assert len(sections) == 1
    assert sections[0].title == "Section Title 1"
    assert "Paragraph text description." in sections[0].content
    assert "List item 1" in sections[0].content
    assert "Click here (http://link.com)" in sections[0].content


def test_parse_thread_comments():
    raw_data = {
        "id": 1,
        "uid": "anikoto",
        "title": "Anikoto Thread",
        "link": "https://anikoto.com",
        "created": 1700000000,
        "isclosed": False,
        "pinned": [
            {
                "id": 999,
                "message": "Welcome to Anikoto discussion!",
                "created": 1700000001,
                "username": "Admin",
                "pic": 456,
                "parent": 0,
                "vote": 50
            }
        ],
        "post": [
            {
                "id": 101,
                "message": "Great site, super fast!",
                "created": 1700000010,
                "username": "1:User1",
                "pic": 123,
                "parent": 0,
                "vote": 5
            },
            {
                "id": 102,
                "message": "Agreed!",
                "created": 1700000020,
                "username": "User2",
                "pic": False,
                "parent": 101,
                "vote": 2
            }
        ]
    }
    thread = parse_thread_comments(raw_data, "https://everythingmoe.com")
    assert thread.title == "Anikoto Thread"
    assert thread.post_count == 2
    assert len(thread.pinned) == 1
    assert thread.pinned[0].username == "Admin"
    assert thread.pinned[0].pic_url == "https://everythingmoe.com/comments/pic/456.jpg"
    assert thread.posts[0].username == "User1"
    assert thread.posts[0].pic_url == "https://everythingmoe.com/comments/pic/123.jpg"
    assert thread.posts[1].parent == 101
    assert thread.posts[1].pic_url is None


def test_parse_full_changelog():
    raw_text = """
    1787736011#add > ReChapters, novel reading site
    1787736289#updated Anistream info & rank
    1787812456#removed > 1Anime, Shiroko, site broken
    1787813167#re-add > AniCipse, anime streaming site
    1787816415#rejected > BadSite, malware
    1787816500#Other maintenance notice
    """
    entries = parse_full_changelog(raw_text)
    assert len(entries) == 6
    assert entries[0].action_type == "add"
    assert entries[0].timestamp == 1787736011
    assert entries[1].action_type == "updated"
    assert entries[2].action_type == "removed"
    assert entries[3].action_type == "re-add"
    assert entries[4].action_type == "rejected"
    assert entries[5].action_type == "other"


def test_parse_simple_directory():
    html = """
    <html>
        <body>
            <div class="index-group" id="sec-anime">
                <span class="index-section">Anime Streaming</span>
                <div class="index-grid">
                    <div class="index-item" data-rank="1">
                        1.
                        <a href="/s/anikoto" data-link="https://anikototv.to">
                            <img src="/icons/anikoto.png" />
                            Anikoto
                        </a>
                    </div>
                </div>
            </div>
            <div class="index-group" id="sec-manga">
                <span class="index-section">Manga Reading</span>
                <div class="index-grid">
                    <div class="index-item" data-rank="1">
                        1.
                        <a href="/s/mangadex" data-link="https://mangadex.org">
                            <img src="/icons/mangadex.png" />
                            MangaDex
                        </a>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    cats = parse_simple_directory(html)
    assert "anime" in cats
    assert len(cats["anime"]) == 1
    assert cats["anime"][0].id == "anikoto"
    assert cats["anime"][0].url == "https://anikototv.to"
    assert "manga" in cats
    assert cats["manga"][0].id == "mangadex"



