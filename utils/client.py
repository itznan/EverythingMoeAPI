from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests

from models.schemas import RecentActivity, SearchResult, SiteDetails, CategoryMenuItem, TagDefinition, SiteStats, StatsHistory, SiteExpand, SiteCommentCount, ChangelogRSS
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
    parse_changelog_rss,
    parse_expand,
    parse_graveyard_items,
    parse_lowsec_items,
    parse_menu,
    parse_search_results,
    parse_section_items,
    parse_site_data,
    parse_stats,
    parse_stats_history,
    parse_tags,
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

    def get_menu(self) -> List[CategoryMenuItem]:
        """Fetch the category navigation menu with icons, colors, and NSFW flags."""
        try:
            resp = self._request("GET", "/data/cache/menu.json")
            return parse_menu(resp.json())
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to fetch menu: {exc}") from exc

    def get_tags(self) -> List[TagDefinition]:
        """Fetch tag definitions explaining what each filter/add-tag means."""
        try:
            resp = self._request("GET", "/data/tags.json")
            return parse_tags(resp.json())
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to fetch tags: {exc}") from exc

    def get_stats(self) -> SiteStats:
        """Fetch the latest aggregate statistics for the EverythingMoe directory."""
        try:
            resp = self._request("GET", "/data/cache/site-stats.json")
            return parse_stats(resp.json())
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to fetch stats: {exc}") from exc

    def get_stats_history(self, date: str) -> StatsHistory:
        """Fetch historical statistics for a specific date (format: YYYYMMDD)."""
        try:
            resp = self._request("GET", f"/data/cache/statshistory/{date}.json")
            return parse_stats_history(resp.json(), date)
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to fetch stats history for {date}: {exc}") from exc

    def get_site_expand(self, id_or_slug: str) -> SiteExpand:
        """Fetch expanded pros/cons/info/alt-links for a site directly from /data/expand/.

        This is a fast, lightweight alternative to scraping the full site detail page.
        Works for both active and dead (graveyard) sites.
        """
        try:
            resp = self._request("GET", f"/data/expand/{id_or_slug}.json")
            return parse_expand(resp.json(), self.base_url)
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to fetch expand data for '{id_or_slug}': {exc}") from exc

    def get_site_comment_count(self, id_or_slug: str) -> SiteCommentCount:
        """Fetch the comment count and review count for a specific site page."""
        try:
            thread_key = f"/s/{id_or_slug}"
            tc_resp = self._request("GET", "/comments/threadcount.json")
            trc_resp = self._request("GET", "/comments/threadreviewcount.json")
            tc_data = tc_resp.json()
            trc_data = trc_resp.json()
            comment_count = tc_data.get(thread_key, 0) or 0
            # trc_data maps review paths like /review/ID -> count
            # We look at total reviews, not per-site
            return SiteCommentCount(
                site_id=id_or_slug,
                comment_count=comment_count,
                review_count=0,  # thread review counts are by review ID, not by site
            )
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to fetch comment count for '{id_or_slug}': {exc}") from exc

    def get_changelog(self) -> ChangelogRSS:
        """Fetch the full changelog from the RSS feed."""
        try:
            url = "https://static.everythingmoe.com/feeds/changelog.xml"
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return parse_changelog_rss(resp.text)
        except EverythingMoeError:
            raise
        except Exception as exc:
            raise EverythingMoeParseError(f"Failed to fetch changelog: {exc}") from exc
