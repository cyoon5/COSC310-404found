from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Annotated
from datetime import date, datetime




# ─────────────────────────────────────────────────────────────
# 1. Movie metadata (metadata.json)
# ─────────────────────────────────────────────────────────────

class Movie(BaseModel):
    """
    Represents one movie's metadata as stored in data/imdb/<MovieTitle>/metadata.json
    """
    title: str  # folder name / movie title
    movieIMDbRating: float
    movieGenres: List[str]
    directors: List[str]
    mainStars: List[str]

    totalRatingCount: Optional[int] = None
    totalUserReviews: Optional[str] = None
    totalCriticReviews: Optional[str] = None
    metaScore: Optional[str] = None

    # Stored as ISO date string in JSON, parsed to date by Pydantic
    datePublished: Optional[date] = None

    creators: Optional[List[str]] = None
    description: Optional[str] = None
    duration: Optional[int] = None  # minutes


# ─────────────────────────────────────────────────────────────
# 2. Reviews (CSV rows) + snapshots for moderation
# ─────────────────────────────────────────────────────────────

class Review(BaseModel):
    """
    Full review row from movieReviews.csv.

    CSV columns:
      - "Movie Title"
      - "Date of Review"
      - "User"
      - "Usefulness Vote"
      - "Total Votes"
      - "User's Rating out of 10"
      - "Review Title"
      - "Review"
      - "Reports"
    """
    movieTitle: str
    user: str
    date: Annotated[date, Field(default_factory=date.today)] 
    rating: Optional[float] = None
    usefulVotes: Optional[int] = None
    totalVotes: Optional[int] = None
    title: str
    body: str
    reportCount: int = 0

class ReviewUpdate(BaseModel):
    #Only these fields as user should not update fields like date, user, movieTitle
    rating: Optional[float] = None
    title: Optional[str] = None
    body: Optional[str] = None

class ReviewCreate(BaseModel): 
    #Should not be optional when creating a review
    rating: float
    title: str
    body: str


class ReviewSnapshot(BaseModel):
    """
    Embedded copy of a review at the moment it was reported.
    This is what gets stored inside each Report in reports.json.
    """
    movieTitle: str
    user: str

    rating: float
    usefulVotes: int
    totalVotes: int

    title: str
    body: str

    # After incrementing the CSV counter for this report:
    reportCount: int


# ─────────────────────────────────────────────────────────────
# 3. Moderation: reports + decisions
# ─────────────────────────────────────────────────────────────

ReportStatus = Literal["pending", "confirmed", "rejected"]


class ReportCreate(BaseModel):
    """
    Body for POST /moderation/reports/{movie_title}/{review_user}
    """
    reasonType: str
    reason: Optional[str] = None


class Report(BaseModel):
    """
    One moderation report stored in data/reports.json.
    Represents one user reporting one review at one time.
    """
    reportId: int  # 1, 2, 3, ...

    review: ReviewSnapshot  # embedded snapshot of the review at report time

    reportedBy: str  # username from X-Username
    status: ReportStatus = "pending"
    dateReported: datetime

    reasonType: str
    reason: Optional[str] = None

    handledByAdmin: Optional[str] = None
    handledAt: Optional[datetime] = None

    # How long a ban was applied because of THIS report; null if no ban
    banDurationSeconds: Optional[int] = None


class ReportDecisionRequest(BaseModel):
    """
    Body for POST /moderation/reports/{report_id}/decision

    {
      "action": "confirm" | "reject",
      "banOption": "3d" | "7d" | "30d" | null
    }
    """
    action: Literal["confirm", "reject"]
    banOption: Optional[Literal["3d", "7d", "30d"]] = None


# ─────────────────────────────────────────────────────────────
# 4. Bans (bans.json)
# ─────────────────────────────────────────────────────────────

class Ban(BaseModel):
    """
    One ban event stored in data/bans.json.
    This is a historical log; users.json only holds *current* banExpiresAt.
    """
    banId: int

    # Who is banned (may or may not exist in users.json)
    userName: str

    # Which report / review triggered this ban
    reportedBy: str
    reportId: int
    movieTitle: str
    reviewUser: str

    # Why
    reasonType: str
    reason: Optional[str] = None

    # What ban option was chosen
    banOption: Literal["3d", "7d", "30d"]
    banDurationSeconds: int

    # When the ban runs
    bannedAt: datetime
    bannedUntil: datetime


# ─────────────────────────────────────────────────────────────
# 5. Auth: users & admins (users.json / admins.json)
# ─────────────────────────────────────────────────────────────

class User(BaseModel):
    """
    Registered user stored in users.json.
    Password is already hashed when persisted.
    """
    userName: str
    passwordHash: str
    role: Literal["user"] = "user"

    # Count of confirmed offences (for "three strikes" etc.)
    penalties: int = 0

    # Simple watchlist of movie titles
    watchlist: List[str] = []
    bio: Optional[str] = None
    # Unix timestamp for when ban ends; None if not currently banned
    banExpiresAt: Optional[float] = None


class Admin(BaseModel):
    """
    Admin user stored in admins.json.
    """
    adminName: str
    passwordHash: str
    role: Literal["admin"] = "admin"