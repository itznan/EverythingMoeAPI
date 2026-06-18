from __future__ import annotations

import json
import logging
import re
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup, Tag

from models.schemas import (
    ChangelogEntry,
    ChangelogRSS,
    ChangelogRSSItem,
    CategoryMenuItem,
    RecentActivity,
    Review,
    Screenshot,
    SearchResult,
    SiteDetails,
    SiteExpand,
    SiteStats,
    StatsHistory,
    TagDefinition,
)

logger = logging.getLogger("everythingmoe")


def parse_categories(html: str) -> Dict[str, str]:
    """Extract the category dropdown options from the homepage HTML."""
    soup = BeautifulSoup(html, "html.parser")
    select = soup.find("select", id="section-input")
    if not select:
        return {}
    categories: Dict[str, str] = {}
    for option in select.find_all("option"):
        val = option.get("value")
        if val and val != "any":
            categories[val] = option.text.strip()
    return categories


def _parse_item_div(div: Tag, category: str) -> Optional[SearchResult]:
    """Parse a single ``section-item`` div into a :class:`SearchResult`."""
    a_tag = div.find("a")
    if not a_tag:
        return None

    slug = a_tag.get("href", "").replace("/s/", "")
    url = a_tag.get("data-link", "") or a_tag.get("href", "")
    title = a_tag.text.strip()

    img_tag = a_tag.find("img")
    icon_url = img_tag.get("src", "") if img_tag else ""

    filters_str = div.get("data-filter", "")
    filter_tags = [x.strip() for x in filters_str.split(",") if x.strip()] if filters_str else []

    add_tags = [span.text.strip().lower() for span in div.find_all("span", class_="addtag")]

    classes = div.get("class", [])
    is_licensed = "section-licensed" in classes
    is_nsfw = "nsfwsection" in classes or "nsfw" in add_tags
    is_dead = "section-dead" in classes

    rank_val = div.get("data-rank", "")
    rank = f"{rank_val} {category.capitalize()}" if rank_val else f"High-Rank {category.capitalize()}"

    return SearchResult(
        id=slug,
        title=title,
        url=url,
        icon_url=icon_url,
        rank=rank,
        type=category,
        filter_tags=filter_tags,
        is_nsfw=is_nsfw,
        is_licensed=is_licensed,
        is_dead=is_dead,
    )


def parse_section_items(html: str, category: str) -> Tuple[List[SearchResult], bool]:
    """Extract high-ranked items from a homepage section."""
    soup = BeautifulSoup(html, "html.parser")
    sec_div = soup.find(id=f"sec-{category}")
    if not sec_div:
        return [], False

    items: List[SearchResult] = []
    for div in sec_div.find_all(class_="section-item"):
        if "section-expandbtn" in div.get("class", []):
            continue
        try:
            result = _parse_item_div(div, category)
            if result:
                items.append(result)
        except Exception as exc:
            logger.warning("Error parsing high-ranked item in %s: %s", category, exc)
    return items, True


def parse_lowsec_items(data: list, category: str, start_rank: int) -> List[SearchResult]:
    """Convert lowsec JSON array into :class:`SearchResult` objects."""
    items: List[SearchResult] = []
    for idx, entry in enumerate(data):
        filter_str = entry.get("filter", "")
        filter_tags = [f.strip() for f in filter_str.split(",") if f.strip()] if filter_str else []

        tags_str = entry.get("tags", "")
        add_tags = [t.strip().lower() for t in tags_str.split(" ") if t.strip()] if tags_str else []

        items.append(SearchResult(
            id=entry.get("id", ""),
            title=entry.get("title", ""),
            url=entry.get("link", ""),
            icon_url=entry.get("icon", ""),
            rank=f"{start_rank + idx} {category.capitalize()}",
            type=category,
            filter_tags=filter_tags,
            is_nsfw="nsfw" in add_tags,
            is_licensed="licensed" in add_tags,
            is_dead="dead" in add_tags,
        ))
    return items


def parse_graveyard_items(html: str) -> List[SearchResult]:
    """Extract dead sites from the ``/graveyard`` HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    items: List[SearchResult] = []
    for div in soup.find_all(class_="section-item"):
        if "section-expandbtn" in div.get("class", []):
            continue
        try:
            result = _parse_item_div(div, "dead")
            if result:
                rank_val = div.get("data-rank", "")
                result.rank = f"{rank_val} Dead" if rank_val else "Dead"
                result.is_dead = True
                items.append(result)
        except Exception as exc:
            logger.warning("Error parsing graveyard item: %s", exc)
    return items


def parse_search_results(data: list) -> List[SearchResult]:
    """Convert backend search JSON response into :class:`SearchResult` objects."""
    results: List[SearchResult] = []
    for item in data:
        filter_str = item.get("filter", "")
        filter_tags = [x.strip() for x in filter_str.split(",") if x.strip()] if filter_str else []

        tags_str = item.get("tags", "")
        add_tags = [x.strip().lower() for x in tags_str.split(" ") if x.strip()] if tags_str else []

        results.append(SearchResult(
            id=item.get("id") or item.get("tempid", ""),
            title=item.get("title", ""),
            url=item.get("link", ""),
            icon_url=item.get("icon", ""),
            rank=item.get("rank", ""),
            type=item.get("type", ""),
            filter_tags=filter_tags,
            is_nsfw="nsfw" in add_tags or item.get("type") in ("hentai", "hentairead"),
            is_licensed="licensed" in add_tags,
            is_dead="DEAD" in item or item.get("type") == "dead",
        ))
    return results


def parse_altlinks(altlink_str: Optional[str], base_url: str = "") -> Dict[str, str]:
    """Parse the ``altlink`` delimited string into a name→URL mapping."""
    if not altlink_str:
        return {}
    altlinks: Dict[str, str] = {}
    for part in altlink_str.split("#"):
        if "<<" in part:
            name, url = part.split("<<", 1)
            if url.startswith("/"):
                url = base_url + url
            altlinks[name] = url
    return altlinks


def parse_site_data(html: str, base_url: str = "") -> Optional[SiteDetails]:
    """Extract the ``var siteData = {...};`` block from a detail page and parse it."""
    soup = BeautifulSoup(html, "html.parser")
    raw: Optional[dict] = None
    for script in soup.find_all("script"):
        if script.string and "var siteData =" in script.string:
            match = re.search(r"var\s+siteData\s*=\s*(\{.*?\});", script.string, re.DOTALL)
            if match:
                try:
                    raw = json.loads(match.group(1))
                    break
                except json.JSONDecodeError:
                    pass
    if raw is None:
        return None

    filter_str = raw.get("filter", "")
    filter_tags = [x.strip() for x in filter_str.split(",") if x.strip()] if filter_str else []

    expand = raw.get("expand") or {}
    pos = [x.strip() for x in expand.get("positive", "").split("#") if x.strip()]
    neg = [x.strip() for x in expand.get("negative", "").split("#") if x.strip()]
    info = [x.strip() for x in expand.get("info", "").split("#") if x.strip()]

    altlink_str = expand.get("altlink") or expand.get("ex-altlink")
    alt_links = parse_altlinks(altlink_str, base_url)

    screenshots = [
        Screenshot(img=x.get("img", ""), type=x.get("type", ""))
        for x in raw.get("ss", [])
    ]

    user_reviews: List[Review] = []
    for rev in raw.get("reviews", []):
        user_reviews.append(Review(
            id=rev.get("id", 0),
            name=rev.get("name", ""),
            rating=int(rev.get("type", 0)),
            review_text=rev.get("review", ""),
            time=rev.get("time", 0),
            has_pic=bool(rev.get("pic")),
            votes=rev.get("vote", 0),
        ))

    return SiteDetails(
        id=raw.get("id", ""),
        title=raw.get("title", ""),
        url=raw.get("link", ""),
        icon_url=raw.get("icon", ""),
        rank=raw.get("rank", ""),
        type=raw.get("type", ""),
        filter_tags=filter_tags,
        positive_reviews=pos,
        negative_reviews=neg,
        info_notes=info,
        alternative_links=alt_links,
        screenshots=screenshots,
        user_reviews=user_reviews,
        is_dead="DEAD" in raw or raw.get("type") == "dead",
        dead_reason=raw.get("DEAD"),
    )


def parse_activity(data: dict) -> RecentActivity:
    """Convert the ``/comments/api?activity=true`` JSON into :class:`RecentActivity`."""
    entries: List[ChangelogEntry] = []
    for item in data.get("changelog", []):
        if "#" in str(item):
            ts_str, msg = str(item).split("#", 1)
            try:
                ts = int(ts_str)
            except ValueError:
                ts = 0
            entries.append(ChangelogEntry(timestamp=ts, message=msg))
    return RecentActivity(
        changelog=entries,
        reviews=data.get("reviews", []),
        comments=data.get("comments", []),
    )


def parse_menu(data: list) -> List[CategoryMenuItem]:
    """Convert ``/data/cache/menu.json`` list into :class:`CategoryMenuItem` objects."""
    items: List[CategoryMenuItem] = []
    for entry in data:
        cat_id = entry.get("id", "")
        if not cat_id:
            continue
        items.append(CategoryMenuItem(
            id=cat_id,
            short=entry.get("short"),
            shortextra=entry.get("shortextra"),
            color=entry.get("color"),
            nsfw=bool(entry.get("nsfw", False)),
        ))
    return items


def parse_tags(data: dict) -> List[TagDefinition]:
    """Convert ``/data/tags.json`` dict into :class:`TagDefinition` list."""
    return [
        TagDefinition(tag=tag, description=description)
        for tag, description in data.items()
    ]


def parse_stats(data: dict) -> SiteStats:
    """Convert ``/data/cache/site-stats.json`` dict into :class:`SiteStats`."""
    return SiteStats(
        entries=data.get("entries", 0),
        category=data.get("category", 0),
        users=data.get("users", 0),
        comments=data.get("comments", 0),
        reviews=data.get("reviews", 0),
        time=data.get("time", 0),
    )


def parse_stats_history(data: dict, date: str) -> StatsHistory:
    """Convert a ``/data/cache/statshistory/{date}.json`` dict into :class:`StatsHistory`."""
    return StatsHistory(
        date=date,
        entries=data.get("entries", 0),
        category=data.get("category", 0),
        users=data.get("users", 0),
        comments=data.get("comments", 0),
        reviews=data.get("reviews", 0),
        time=data.get("time", 0),
    )


def _split_list(raw: str) -> List[str]:
    """Split a '#'-delimited string into a clean list, ignoring empty entries."""
    return [x.strip() for x in raw.split("#") if x.strip()] if raw else []


def _split_extra_links(raw: str) -> List[str]:
    """Split extra-link / extralink values (comma or '#' separated URLs)."""
    if not raw:
        return []
    parts = raw.split("#") if "#" in raw else raw.split(",")
    return [p.strip() for p in parts if p.strip()]


def parse_expand(data: dict, base_url: str = "") -> SiteExpand:
    """Convert a ``/data/expand/{id}.json`` response into :class:`SiteExpand`.

    Handles all known field variants discovered in both ``main.json`` and
    ``dead.json``, including historical ``ex-``/``exx-``/``exxx-`` prefixes,
    domain aliases, notes, and extra links.
    """
    return SiteExpand(
        # Current pros / cons / info
        positive_reviews=_split_list(data.get("positive", "")),
        negative_reviews=_split_list(data.get("negative", "")),
        info_notes=_split_list(data.get("info", "")),
        note=data.get("note") or None,

        # Mirror / alt links
        alternative_links=parse_altlinks(data.get("altlink"), base_url),
        ex_alternative_links=parse_altlinks(data.get("ex-altlink"), base_url),
        ex_alternative_links2=parse_altlinks(data.get("ex-altlink2"), base_url),
        exx_alternative_links=parse_altlinks(data.get("exx-altlink"), base_url),
        reserve_altlink=data.get("reserve-altlink") or None,

        # Historical ex- variants
        ex_positive_reviews=_split_list(data.get("ex-positive", "")),
        ex_negative_reviews=_split_list(data.get("ex-negative", "")),
        ex_info_notes=_split_list(data.get("ex-info", "")),
        ex_note=data.get("ex-note") or None,
        exx_info_notes=_split_list(data.get("exx-info", "")),
        exxx_info_notes=_split_list(data.get("exxx-info", "")),

        # Extra metadata
        alt_name=data.get("altname") or None,
        domains=data.get("domains") or None,
        extra_links=_split_extra_links(data.get("extra-link") or data.get("extralink") or ""),
        extra=data.get("extra") or None,
        potential=data.get("potential") or None,
    )


def parse_changelog_rss(xml_content: str) -> ChangelogRSS:
    """Parse the changelog RSS feed XML into :class:`ChangelogRSS`."""
    soup = BeautifulSoup(xml_content, "xml")
    items: List[ChangelogRSSItem] = []
    
    for item in soup.find_all("item"):
        title_tag = item.find("title")
        link_tag = item.find("link")
        guid_tag = item.find("guid")
        pub_date_tag = item.find("pubDate")
        
        if title_tag and link_tag:
            items.append(ChangelogRSSItem(
                title=title_tag.text.strip(),
                link=link_tag.text.strip(),
                guid=guid_tag.text.strip() if guid_tag else "",
                pub_date=pub_date_tag.text.strip() if pub_date_tag else "",
            ))
    
    return ChangelogRSS(items=items)
