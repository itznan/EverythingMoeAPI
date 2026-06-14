# EverythingMoe API & Web Service

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Tests Status](https://img.shields.io/badge/Tests-38%20Passed-success?style=for-the-badge&logo=pytest)](https://pytest.org)

An unofficial, robust **Python scraper client wrapper** and **FastAPI Web Service** that exposes clean JSON API endpoints for [everythingmoe.com](https://everythingmoe.com/). 

Easily query categories, search items, filter tags/genres, track graveyard dead sites, and monitor recent changelogs or comments.

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
- **100% Mocked Test Coverage**: 38 clean unit/integration/API tests that run offline in milliseconds.

---

## Project Architecture

The workspace follows a highly structured, scalable FastAPI layout:

- [.github/workflows/test.yml](file:///E:/NAN/Github/everythingmoe-api/.github/workflows/test.yml) - GitHub Actions CI workflow configuration.
- [api/main.py](file:///E:/NAN/Github/everythingmoe-api/api/main.py) - FastAPI Application, CORS configuration, and router entrypoint.
- [api/dependencies.py](file:///E:/NAN/Github/everythingmoe-api/api/dependencies.py) - Client dependency injection container.
- [models/schemas.py](file:///E:/NAN/Github/everythingmoe-api/models/schemas.py) - Pydantic serialization & validation models.
- [routers/](file:///E:/NAN/Github/everythingmoe-api/routers) - Folder housing individual API endpoint routers.
- [utils/client.py](file:///E:/NAN/Github/everythingmoe-api/utils/client.py) - Core scraping client orchestration.
- [utils/parsers.py](file:///E:/NAN/Github/everythingmoe-api/utils/parsers.py) - BeautifulSoup scraping parser methods.
- [utils/constants.py](file:///E:/NAN/Github/everythingmoe-api/utils/constants.py) - App constants, headers, and mapping rules.
- [utils/exceptions.py](file:///E:/NAN/Github/everythingmoe-api/utils/exceptions.py) - Custom scrap/parse exception structures.
- [tests/](file:///E:/NAN/Github/everythingmoe-api/tests) - Tests directory featuring client, parser, and router tests.
- [start.bat](file:///E:/NAN/Github/everythingmoe-api/start.bat) - One-click Windows launch script.

---

## Getting Started

### 1. Installation

Clone this repository and install the package with dev dependencies (required for testing):

```bash
git clone https://github.com/yourusername/everythingmoe-api.git
cd everythingmoe-api
pip install -e .[dev]
```

### 2. Running the Server

#### Windows (One-Click)
Simply double-click the **[start.bat](file:///E:/NAN/Github/everythingmoe-api/start.bat)** file.

#### Command Line
```bash
uvicorn api.main:app --reload
```

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
- `GET /categories/{category}/items` : Fetch all listings in a category (e.g. `streaming`, `manga`, `novel`, `game`).

### Search & Genres
- `GET /search?q={query}&category={category}` : Search items. Filter tags by prefixing query with `tag:` (e.g. `/search?q=tag:Torrent`).
- `GET /genres/{genre}` : Filter items by tag name or redirect directly to category if name matches.

### Details & Metadata
- `GET /sites/{id_or_slug}` : Get mirror links, editorial pros/cons, community reviews, and screenshot links for a site (e.g. `/sites/anikoto`).

### Graveyard & Logs
- `GET /graveyard` : List all dead/archived sites.
- `GET /activity` : Retrieve recent changelogs, review submissions, and comments.

---

## Python Library Usage

You can also use the scraper engine as a standalone python library in other projects:

```python
from utils.client import EverythingMoeAPI

# Initialize client
api = EverythingMoeAPI(include_nsfw=True)

# Fetch specific site details
details = api.get_site("hentaitv")
print(f"Name: {details.title} | Mirrors: {details.alternative_links}")
```

---

## Testing

The repository includes a comprehensive test suite (38 unit/integration tests). Run them locally with:

```bash
python -m pytest
```

---

## License

Distributed under the MIT License. See `LICENSE` for details.
