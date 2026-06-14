from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests

from models.schemas import RecentActivity, SearchResult, SiteDetails
from utils.constants import BASE_URL, CATEGORY_TO_LOWSEC, DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from utils.exceptions import (
    EverythingMoeError,
    EverythingMoeNetworkError,
    EverythingMoeNotFoundError,
    EverythingMoeParseError,
)
from utils.parsers import (
    parse_activity,
    parse_categories,
    parse_graveyard_items,
    parse_lowsec_items,
    parse_search_results,
    parse_section_items,
    parse_site_data,
)

logger = logging.getLogger("everythingmoe")


class EverythingMoeAPI:
    """Unofficial scraper client for `EverythingMoe <https://everythingmoe.com>`_."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        include_nsfw: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": DEFAULT_USER_AGENT,
            "Referer": self.base_url,
        })
        if include_nsfw:
            self.session.headers["Cookie"] = "nsfw=true"

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Send an HTTP request and handle common error cases."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
            if resp.status_code == 404:
                raise EverythingMoeNotFoundError(f"Endpoint not found: {url}")
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                raise EverythingMoeNotFoundError(f"Endpoint not found: {url}") from exc
            raise EverythingMoeNetworkError(f"HTTP error: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise EverythingMoeNetworkError(f"Network request failed: {exc}") from exc

    def get_categories(self) -> Dict[str, str]:
        """Fetch all available categories from the homepage dropdown."""
        try:
            resp = self._request("GET", "/")
            cats = parse_categories(resp.text)
            if not cats:
                raise EverythingMoeParseError("Could not find category dropdown on homepage.")
            return cats
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to parse categories: {exc}") from exc

    def get_category_items(self, category: str) -> List[SearchResult]:
        """Fetch **all** items under a category (high-ranked + low-ranked)."""
        if category == "dead":
            return self.get_graveyard()
        try:
            resp = self._request("GET", "/")
            items, found = parse_section_items(resp.text, category)
            if not found:
                raise EverythingMoeNotFoundError(
                    f"Category section 'sec-{category}' not found on homepage."
                )

            # Append low-ranked items from the JSON endpoint
            lowsec_name = CATEGORY_TO_LOWSEC.get(category)
            if lowsec_name:
                try:
                    low_resp = self._request("GET", f"/data/lowsec/{lowsec_name}.json")
                    low_items = parse_lowsec_items(low_resp.json(), category, len(items) + 1)
                    items.extend(low_items)
                except EverythingMoeNotFoundError:
                    pass  # some categories don't have a lowsec file
                except Exception as exc:
                    logger.warning("Error loading low-ranked items for %s: %s", category, exc)

            return items
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to fetch category items: {exc}") from exc

    def get_graveyard(self) -> List[SearchResult]:
        """Fetch all dead/archived sites from the ``/graveyard`` page."""
        try:
            resp = self._request("GET", "/graveyard")
            return parse_graveyard_items(resp.text)
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to parse graveyard: {exc}") from exc

    def search(self, query: str, category: str = "any") -> List[SearchResult]:
        """Search for sites via the server-side backend."""
        try:
            if query.startswith("tag:"):
                payload = {"tag": query.split(":", 1)[1]}
            else:
                payload = {"q": query, "section": category}

            resp = self._request("POST", "/backend/search", data=payload)
            return parse_search_results(resp.json())
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Search failed: {exc}") from exc

    def get_site(self, id_or_slug: str) -> SiteDetails:
        """Fetch full details for a specific site."""
        try:
            resp = self._request("GET", f"/s/{id_or_slug}")
            details = parse_site_data(resp.text, self.base_url)
            if details is None:
                raise EverythingMoeParseError(
                    f"Could not parse siteData in /s/{id_or_slug}"
                )
            return details
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(
                f"Failed to get details for '{id_or_slug}': {exc}"
            ) from exc

    def get_latest(self) -> RecentActivity:
        """Fetch the most recent changelogs, reviews, and comments."""
        try:
            resp = self._request("GET", "/comments/api?activity=true")
            return parse_activity(resp.json())
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to fetch activity: {exc}") from exc

    def get_by_genre(self, genre: str) -> List[SearchResult]:
        """Filter items by genre/tag or retrieve a full category."""
        genre_lower = genre.lower().strip()
        categories = self.get_categories()
        for cat_id, cat_label in categories.items():
            if genre_lower in (cat_id.lower(), cat_label.lower()):
                return self.get_category_items(cat_id)
        return self.search(f"tag:{genre}")

    def get_episodes(self, anime_id: str) -> List[Any]:
        """Placeholder — EverythingMoe does not index individual episodes."""
        logger.warning(
            "EverythingMoe is a directory of external sites. "
            "It does not index individual anime episodes. Returning empty list."
        )
        return []
