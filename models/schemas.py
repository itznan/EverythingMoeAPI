from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

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
