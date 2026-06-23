# EverythingMoe API & Web Service

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Tests Status](https://img.shields.io/badge/Tests-53%20Passed-success?style=for-the-badge&logo=pytest)](https://pytest.org)

An unofficial, robust **Python scraper client wrapper** and **FastAPI Web Service** that exposes clean JSON API endpoints for [everythingmoe.com](https://everythingmoe.com/). 

Easily query categories, search items, filter tags/genres, track graveyard dead sites, monitor site statistics and changelog activity, lookup lightweight expand data, submit user contributions, verify live uptime status maps, list guides/articles, and retrieve parsed static description layouts.

> [!NOTE]
> This project is designed as a standalone, deployable web service. It translates server-side rendered website contents and dynamic pagination endpoints into clean, validated JSON schemas.

---

## What Can This API Be Used For?

This API turns the community-curated [EverythingMoe](https://everythingmoe.com/) directory into a programmable data source. Here are some practical things you can build with it:

| Use Case | How |
|---|---|
| **Anime / Manga Site Aggregator** | Pull ranked listings across 26+ categories (streaming, manga, novel, donghua, music, etc.) and display them in your own frontend or mobile app. |
| **Discord / Telegram Bot** | Let users search for sites, browse categories, or check if a site is dead — all via bot commands backed by the `/search`, `/categories`, and `/graveyard` endpoints. |
| **Site Health Monitor** | Poll the `/graveyard` and `/activity` endpoints on a schedule to detect when a popular site goes down or comes back, and send alerts. |
| **Recommendation / Discovery Engine** | Use tag-based filtering (`tag:Torrent`, `tag:Dub`, etc.) and genre endpoints to build a personalised recommendation feed. |
| **Research & Analytics Dashboard** | Aggregate category sizes, review sentiments, dead-site trends, and changelog frequency into charts and reports. |
| **Mirror / Proxy Finder** | Query `/sites/{slug}` to programmatically retrieve a site's alternative/mirror links, screenshots, and community reviews. |
| **NSFW Content Filter Testing** | Toggle the `nsfw` parameter to compare filtered vs. unfiltered results for content-moderation research. |
| **Automated Testing & CI Pipelines** | Integrate the Python library (`EverythingMoeAPI` class) into test harnesses that verify third-party site availability. |

> [!TIP]
> The API is fully stateless — every endpoint returns clean JSON with Pydantic-validated schemas, making it trivial to integrate into any language or framework.

---

## Features

- **Asynchronous Web Server**: Powered by **FastAPI** & **Uvicorn** for high-concurrency performance.
- **Pydantic V2 Validation**: All request and response structures are validated with robust, strict Pydantic models.
- **Universal Search**: Supports general text search as well as tag-based filtering (e.g. `tag:Torrent`).
- **NSFW Bypass**: Built-in toggle to bypass NSFW filtering (`nsfw=true` cookie integration).
- **Deep Category Extraction**: Extracts both high-ranked items (server-side rendered) and low-ranked items (from dynamic lowsec JSON endpoints).
- **Graveyard & Activity Monitors**: Built-in routes to extract dead sites with downing reasons and activity updates.
- **Menu & Tag Definitions**: Structured category navigation menu and full tag/filter glossary endpoints.
- **Site Statistics**: Current and historical aggregate stats (entries, users, comments, reviews).
- **Lightweight Expand**: Fast `/expand` endpoint for pros/cons/altlinks without full page scraping.
- **Comment Counts**: Per-site comment count lookup from EverythingMoe's thread counters.
- **Uptime Monitoring & Uptime History**: Mapped status pings and 30-hour status check history logs.
- **Guides & Articles List**: Parsed guides, quickstarts, and extension repositories list.
- **Informational Pages Parsers**: Dynamic HTML parsing of info pages into clean structured headers/contents.
- **100% Mocked Test Coverage**: 53 clean unit/integration/API tests that run offline in milliseconds.

---

## Project Architecture

The workspace follows a highly structured, scalable FastAPI layout:

- [.github/workflows/test.yml](file:///E:/NAN/Github/everythingmoe-api/.github/workflows/test.yml) - GitHub Actions CI workflow configuration.
- [app/api/main.py](file:///E:/NAN/Github/everythingmoe-api/app/api/main.py) - FastAPI Application, CORS configuration, and router entrypoint.
- [app/api/dependencies.py](file:///E:/NAN/Github/everythingmoe-api/app/api/dependencies.py) - Client dependency injection container.
- [app/models/schemas.py](file:///E:/NAN/Github/everythingmoe-api/app/models/schemas.py) - Pydantic serialization & validation models.
- [app/routers/](file:///E:/NAN/Github/everythingmoe-api/app/routers) - Folder housing individual API endpoint routers.
- [app/utils/client.py](file:///E:/NAN/Github/everythingmoe-api/app/utils/client.py) - Core scraping client orchestration.
- [app/utils/parsers.py](file:///E:/NAN/Github/everythingmoe-api/app/utils/parsers.py) - BeautifulSoup scraping parser methods.
- [app/utils/constants.py](file:///E:/NAN/Github/everythingmoe-api/app/utils/constants.py) - App constants, headers, and mapping rules.
- [app/utils/exceptions.py](file:///E:/NAN/Github/everythingmoe-api/app/utils/exceptions.py) - Custom scrap/parse exception structures.
- [tests/](file:///E:/NAN/Github/everythingmoe-api/tests) - Tests directory featuring client, parser, and router tests.
- [start.bat](file:///E:/NAN/Github/everythingmoe-api/start.bat) - One-click Windows launch script.

---

## Getting Started

### 1. Installation

Clone this repository and install the package with dev dependencies (required for testing):

`git clone https://github.com/itznan/EverythingMoeAPI.git`
`cd EverythingMoeAPI`
`pip install -e .[dev]`

### 2. Running the Server

#### Windows (One-Click)
Simply double-click the **[start.bat](file:///E:/NAN/Github/everythingmoe-api/start.bat)** file.

#### Command Line
`uvicorn app.api.main:app --reload`

The server will spin up on **`http://127.0.0.1:8000`**.

### 3. Open API Documentation
Navigate to:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Interactive testing playground)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## REST API Documentation

### System
- `GET /health` : Check service status.

### Categories
- `GET /categories` : Get ID-to-label mapping for all 26 categories.
- `GET /categories/{category}/items` : Fetch all listings in a category (e.g. `streaming`, `manga`, `novel`, `game`, `western`, `gacha`, `quiz`).

### Search & Genres
- `GET /search?q={query}&category={category}` : Search items. Filter tags by prefixing query with `tag:` (e.g. `/search?q=tag:Torrent`).
- `GET /genres/{genre}` : Filter items by tag name or redirect directly to category if name matches.

### Menu & Navigation
- `GET /menu` : Fetch the site's full category navigation menu with display names, accent colors, and NSFW flags.

### Tag Definitions
- `GET /tags` : Fetch all tag/filter definitions with descriptions (e.g. what `nsfw`, `hia`, `scan`, `mtl`, `ddl` mean).

### Details & Metadata
- `GET /sites/{id_or_slug}` : Get full metadata, editorial pros/cons, community reviews, and screenshot links (scrapes the full page).
- `GET /sites/{id_or_slug}/expand` : **Lightweight** — fetch only pros/cons/info/alt-links from `/data/expand/{id}.json` (works for active **and** dead sites, much faster).
- `GET /sites/{id_or_slug}/comments` : Get the comment count for a specific site's page.

### Statistics
- `GET /stats` : Get the latest aggregate directory statistics (entries, users, comments, reviews, timestamp).
- `GET /stats/history/{date}` : Get a historical snapshot of stats for a date in `YYYYMMDD` format (e.g. `20260617`).

### Graveyard & Logs
- `GET /graveyard` : List all dead/archived sites.
- `GET /activity` : Retrieve recent changelogs, review submissions, and comments.

### Uptime Status Checks
- `GET /detector` : Fetch current live ping and API status maps, alongside 30-hour check status histories.
- `GET /detector/{site_id}` : Get uptime status stats for a single monitored site.

### Cache Databases (Advanced)
- `GET /cache/main` : Fetch the parsed `main.json` database containing all active site expands and section arrays.
- `GET /cache/dead` : Fetch the parsed `dead.json` database containing all dead site expands and dead streaming lists.

### Backend Actions (Proxy Forms)
- `POST /backend/info` : Proxy client platform telemetry metrics (referrers, platform, resolution, bookmarks count).
- `POST /backend/api` : Submit site recommendations, edits, or feedback to EverythingMoe backend (Turnstile token required).

### Static Info & Project Descriptions
- `GET /info` : Retrieve structured parsed text blocks of About, Otaku Culture, Rank Criteria, and Requirements from `/post/info.html`.
- `GET /kuroiru` : Retrieve structured parsed text blocks of the Kuroiru tracking sub-project from `/post/kuroiru.html`.
- `GET /articles` : Retrieve dynamic OTAC/ACG guides, quickstarts, and extension repositories listed under `/post/`.

---

## API vs Raw JSON Files — What This API Adds

[everythingmoe.com](https://everythingmoe.com/) exposes two raw cache files:
- `/data/cache/main.json` — **896 active site entries**
- `/data/cache/dead.json` — **200+ dead site entries**

Each entry contains only **4-5 raw unparsed text blobs**:

```json
"anikoto": {
  "positive": "Large library#Reupload Hianime videos#...",
  "negative": "Hard subs depend on AniNeko#Bad ads",
  "info":     "note: It has many alt domain and brand names.",
  "altlink":  "mirrors<<https://anikoto.site#anisuge<<https://anisuge.tv/home#..."
}
```

### **11 Additional Features Not Available in Raw JSON Files**

This API provides **11 major features** that don't exist in `main.json` or `dead.json`:

1. **Search Functionality** — Full-text and tag-based search via backend API
2. **Real-time Activity Feed** — Live changelogs, reviews, and comments
3. **Statistics & Analytics** — Aggregate directory stats (entries, users, comments)
4. **Historical Statistics** — Time-series stats snapshots by date
5. **Tag Definitions** — Human-readable glossary for all filter tags
6. **Navigation Menu** — Category icons, colors, and NSFW flags
7. **Detailed Site Information** — Screenshots, user reviews, ratings
8. **Comment Counts** — Per-site comment/review counts
9. **Expanded Site Data** — Historical data, domain aliases, extra links
10. **Changelog History** — Full RSS-based changelog with timestamps
11. **Category Filtering** — Structured category extraction and filtering

Here is exactly what is **exclusive to this API** and does not exist anywhere in the raw JSON files:

### Fields added by `GET /sites/{id}` (HTML scrape)

| Field | Source | Description |
|---|---|---|
| `id` | HTML scrape | Unique site slug |
| `title` | HTML scrape | Display name |
| `url` | HTML scrape | Live URL |
| `icon_url` | HTML scrape | Logo from CDN |
| `rank` | HTML scrape | e.g. `"1 Streaming"` |
| `type` | HTML scrape | Category (`streaming`, `manga`…) |
| `filter_tags` | HTML scrape | e.g. `["Scraper", "Modern interface"]` |
| `is_nsfw` | HTML scrape | Boolean |
| `is_licensed` | HTML scrape | Boolean |
| `is_dead` | HTML scrape | Boolean |
| `dead_reason` | HTML scrape | Shutdown date/reason |
| `screenshots` | HTML scrape | Screenshot URLs + type |
| `user_reviews` | HTML scrape | Full reviews with rating, votes, timestamp |

### Fields parsed & structured FROM `main.json` (raw → clean)

| API Field | `main.json` raw key | What the API does |
|---|---|---|
| `positive_reviews` | `"positive"` | Splits `"A#B#C"` → `["A", "B", "C"]` |
| `negative_reviews` | `"negative"` | Splits `"A#B"` → `["A", "B"]` |
| `info_notes` | `"info"` | Splits into list |
| `alternative_links` | `"altlink"` | Parses `"name<<url#name2<<url2"` → `{"name": "url", ...}` |
| `ex_alternative_links` | `"ex-altlink"` | Same format — previous/expired domains |

### Whole endpoints with zero equivalent in `main.json`

| Endpoint | Data Source | Description |
|---|---|---|
| `GET /menu` | `/data/cache/menu.json` | Category icons, colors, NSFW flags |
| `GET /tags` | `/data/tags.json` | 26 tag definitions/glossary |
| `GET /stats` | `/data/cache/site-stats.json` | Live directory stats |
| `GET /stats/history/{date}` | `/data/cache/statshistory/` | Historical stats snapshots |
| `GET /sites/{id}/comments` | `/comments/threadcount.json` | Per-site comment count |
| `GET /graveyard` | `/graveyard` HTML | All dead sites with reasons |
| `GET /activity` | `/comments/api?activity=true` | Changelogs, reviews, comments feed |
| `GET /search` | `/backend/search` POST | Full text + tag-based search |
| `GET /genres/{genre}` | Cross-endpoint | Tag-based cross-category filtering |
| `GET /categories` | Homepage HTML | Full category dropdown list |
| `GET /categories/{cat}/items` | HTML + lowsec JSON | Full ranked + low-ranked listings |

> [!TIP]
> `main.json` is only a raw text cache used internally by the website's frontend JS. This API is the only way to access the full structured, validated, and enriched data programmatically.


## Python Library Usage

You can also use the scraper engine as a standalone python library in other projects:

```python
from utils.client import EverythingMoeAPI

# Initialize client
api = EverythingMoeAPI(include_nsfw=True)

# Fetch specific site details (full scrape)
details = api.get_site("hentaitv")
print(f"Name: {details.title} | Mirrors: {details.alternative_links}")

# Lightweight expand (no scraping, just JSON)
expand = api.get_site_expand("anikoto")
print(f"Pros: {expand.positive_reviews}")

# Get category navigation menu
menu = api.get_menu()
print(f"Categories: {[m.id for m in menu]}")

# Get tag definitions
tags = api.get_tags()
print(f"Tags: {[t.tag for t in tags]}")

# Get current stats
stats = api.get_stats()
print(f"Total entries: {stats.entries}, Users: {stats.users}")

# Historical stats
hist = api.get_stats_history("20260617")
print(f"Stats on 2026-06-17: {hist.entries} entries")

# Comment count for a site
cc = api.get_site_comment_count("anikoto")
print(f"Comments on anikoto: {cc.comment_count}")
```

---

## Testing

The repository includes a comprehensive test suite (53 unit/integration tests). Run them locally with:

```bash
python -m pytest
```

---

## License

Distributed under the MIT License. See `LICENSE` for details.
