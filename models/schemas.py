from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import date as DateType

class Review(BaseModel):
    """A user review on EverythingMoe."""
    id: int
    name: str
    rating: int  # 1 for positive, 0 for neutral, -1 for negative
    review_text: str
    time: int
    has_pic: bool
    votes: int

class Screenshot(BaseModel):
    """A screenshot associated with a site listing."""
    img: str
    type: str

class SiteDetails(BaseModel):
    """Full details of a specific site/service indexed on EverythingMoe."""
    id: str
    title: str
    url: str
    icon_url: str
    rank: str
    type: str
    filter_tags: List[str] = Field(default_factory=list)
    positive_reviews: List[str] = Field(default_factory=list)
    negative_reviews: List[str] = Field(default_factory=list)
    info_notes: List[str] = Field(default_factory=list)
    alternative_links: Dict[str, str] = Field(default_factory=dict)
    screenshots: List[Screenshot] = Field(default_factory=list)
    user_reviews: List[Review] = Field(default_factory=list)
    is_dead: bool = False
    dead_reason: Optional[str] = None

class SearchResult(BaseModel):
    """A lightweight representation of a site returned by search or category listing."""
    id: str
    title: str
    url: str
    icon_url: str
    rank: str
    type: str
    filter_tags: List[str] = Field(default_factory=list)
    is_nsfw: bool = False
    is_licensed: bool = False
    is_dead: bool = False

class ChangelogEntry(BaseModel):
    """A single changelog entry from the recent-activity feed."""
    timestamp: int
    message: str

class RecentActivity(BaseModel):
    """Aggregated recent activity: changelogs, reviews, and comments."""
    changelog: List[ChangelogEntry] = Field(default_factory=list)
    reviews: List[Dict[str, Any]] = Field(default_factory=list)
    comments: List[Dict[str, Any]] = Field(default_factory=list)


class CategoryMenuItem(BaseModel):
    """A category menu entry from the site navigation."""
    id: str
    short: Optional[str] = None
    shortextra: Optional[str] = None
    color: Optional[str] = None
    nsfw: bool = False


class TagDefinition(BaseModel):
    """A tag definition explaining what an add-tag means."""
    tag: str
    description: str


class SiteStats(BaseModel):
    """Aggregate statistics for the EverythingMoe directory."""
    entries: int
    category: int
    users: int
    comments: int
    reviews: int
    time: int


class StatsHistory(BaseModel):
    """Historical snapshot of site statistics for a given date."""
    date: str
    entries: int
    category: int
    users: int
    comments: int
    reviews: int
    time: int


class SiteExpand(BaseModel):
    """Expanded pros/cons/info/alt-links for a site, fetched from /data/expand/{id}.json.

    Covers all known fields from both main.json and dead.json including
    historical/ex- variants, domain aliases, notes, and extra links.
    """
    # Current pros / cons / info
    positive_reviews: List[str] = Field(default_factory=list)
    negative_reviews: List[str] = Field(default_factory=list)
    info_notes: List[str] = Field(default_factory=list)
    note: Optional[str] = None              # Short editor note (rare, e.g. 'Decent features')

    # Alternative / mirror links
    alternative_links: Dict[str, str] = Field(default_factory=dict)     # altlink
    ex_alternative_links: Dict[str, str] = Field(default_factory=dict)  # ex-altlink (expired/old domains)
    ex_alternative_links2: Dict[str, str] = Field(default_factory=dict) # ex-altlink2 (dead.json only)
    exx_alternative_links: Dict[str, str] = Field(default_factory=dict) # exx-altlink (double-expired)
    reserve_altlink: Optional[str] = None   # reserve-altlink (emergency backup URL, dead.json)

    # Historical / ex- variants (data from a previous version of the site)
    ex_positive_reviews: List[str] = Field(default_factory=list)        # ex-positive
    ex_negative_reviews: List[str] = Field(default_factory=list)        # ex-negative
    ex_info_notes: List[str] = Field(default_factory=list)              # ex-info
    ex_note: Optional[str] = None           # ex-note (old short editor note)
    exx_info_notes: List[str] = Field(default_factory=list)             # exx-info
    exxx_info_notes: List[str] = Field(default_factory=list)            # exxx-info (dead.json)

    # Extra metadata
    alt_name: Optional[str] = None          # altname (alternate display name, e.g. 'Usagi')
    domains: Optional[str] = None           # domains (CDN/domain list used by the site)
    extra_links: List[str] = Field(default_factory=list)  # extra-link / extralink (additional URLs)
    extra: Optional[str] = None             # extra (misc extra data, dead.json)
    potential: Optional[str] = None         # potential (suggested future sites, main.json)


class SiteCommentCount(BaseModel):
    """Comment count for a specific site page."""
    site_id: str
    comment_count: int
    review_count: int


class ChangelogRSSItem(BaseModel):
    """A single changelog entry from the RSS feed."""
    title: str
    link: str
    guid: str
    pub_date: str


class ChangelogRSS(BaseModel):
    """The full changelog RSS feed."""
    items: List[ChangelogRSSItem] = Field(default_factory=list)
