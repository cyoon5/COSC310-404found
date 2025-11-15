from __future__ import annotations

from pathlib import Path
import csv
import json
from datetime import datetime, timedelta
from typing import List, Optional, Literal, Dict, Any

from ..models.models import ReviewSnapshot, Report, Ban

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────

# backend/app/repositories/moderationRepo.py
# parents[3] → project root
ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
IMDB_DIR = DATA_DIR / "imdb"

REPORTS_FILE = DATA_DIR / "reports.json"
BANS_FILE = DATA_DIR / "bans.json"


# ─────────────────────────────────────────────────────────────
# Helper JSON load/save
# ─────────────────────────────────────────────────────────────

def _read_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        return json.loads(raw)
    except json.JSONDecodeError:
        # If corrupted, bubble up – service/controller can decide how to handle
        raise


def _write_json_list(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


# ─────────────────────────────────────────────────────────────
# CSV: build snapshot + increment Reports column
# ─────────────────────────────────────────────────────────────

def build_snapshot_and_increment_reports(
    movie_title: str,
    review_user: str,
) -> ReviewSnapshot:
    """
    Load movieReviews.csv for a movie, find the row for review_user,
    increment its Reports counter, write CSV back, and return a ReviewSnapshot
    reflecting the new reportCount.

    Raises:
        FileNotFoundError if CSV doesn't exist.
        ValueError if the review_user can't be found.
    """
    csv_path = IMDB_DIR / movie_title / "movieReviews.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"No reviews found for movie '{movie_title}'")

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    target_index: Optional[int] = None
    for i, row in enumerate(rows):
        if row.get("User") == review_user:
            target_index = i
            break

    if target_index is None:
        raise ValueError(
            f"Review not found for movie '{movie_title}' and user '{review_user}'"
        )

    row = rows[target_index]

    # Current reports value (blank/missing/invalid → 0)
    raw_reports = row.get("Reports", "")
    try:
        current_reports = int(raw_reports)
    except (ValueError, TypeError):
        current_reports = 0

    new_reports = current_reports + 1
    row["Reports"] = str(new_reports)
    rows[target_index] = row

    # Write updated CSV back
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Build snapshot according to spec
    def _int(value: Any) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def _float(value: Any) -> float:
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    snapshot = ReviewSnapshot(
        movieTitle=movie_title,
        user=row.get("User", ""),
        rating=_float(row.get("User's Rating out of 10")),
        usefulVotes=_int(row.get("Usefulness Vote")),
        totalVotes=_int(row.get("Total Votes")),
        title=row.get("Review Title", "") or "",
        body=row.get("Review", "") or "",
        reportCount=new_reports,
    )
    return snapshot


# ─────────────────────────────────────────────────────────────
# Reports: load/save/list/create/update
# ─────────────────────────────────────────────────────────────

def load_reports() -> List[Report]:
    raw = _read_json_list(REPORTS_FILE)
    return [Report.model_validate(r) for r in raw]


def save_reports(reports: List[Report]) -> None:
    data = [r.model_dump(mode="json") for r in reports]
    _write_json_list(REPORTS_FILE, data)


def _next_report_id(reports: List[Report]) -> int:
    if not reports:
        return 1
    return max(r.reportId for r in reports) + 1


def create_report_for_review(
    movie_title: str,
    review_user: str,
    reported_by: str,
    reason_type: str,
    reason: Optional[str],
) -> Report:
    """
    Implements the core "report a review" logic:

    - increments the CSV Reports counter
    - builds a ReviewSnapshot
    - stores a new Report object into reports.json
    """
    # 1) CSV bump + snapshot
    snapshot = build_snapshot_and_increment_reports(movie_title, review_user)

    # 2) Load existing reports
    reports = load_reports()
    new_id = _next_report_id(reports)

    # 3) Create new Report
    now = datetime.utcnow()
    report = Report(
        reportId=new_id,
        review=snapshot,
        reportedBy=reported_by,
        status="pending",
        dateReported=now,
        reasonType=reason_type,
        reason=reason,
        handledByAdmin=None,
        handledAt=None,
        banDurationSeconds=None,
    )

    # 4) Persist
    reports.append(report)
    save_reports(reports)

    return report


def get_report_by_id(report_id: int) -> Optional[Report]:
    for r in load_reports():
        if r.reportId == report_id:
            return r
    return None


def replace_report(updated: Report) -> None:
    """
    Replace a report with the same reportId in reports.json.
    """
    reports = load_reports()
    for idx, r in enumerate(reports):
        if r.reportId == updated.reportId:
            reports[idx] = updated
            save_reports(reports)
            return
    # If not found, treat as logic error – service should have checked first.
    raise ValueError(f"Report with id {updated.reportId} not found")


def list_reports(status: Optional[Literal["pending", "confirmed", "rejected"]] = None) -> List[Report]:
    reports = load_reports()
    if status is None:
        return reports
    return [r for r in reports if r.status == status]


def list_pending_reports() -> List[Report]:
    return list_reports(status="pending")


def list_reports_for_review(movie_title: str, review_user: str) -> List[Report]:
    """
    All reports for a specific review (movie_title + review_user),
    across all statuses.
    """
    reports = load_reports()
    return [
        r
        for r in reports
        if r.review.movieTitle == movie_title and r.review.user == review_user
    ]


# ─────────────────────────────────────────────────────────────
# Bans: load/save/list/create
# ─────────────────────────────────────────────────────────────

def load_bans() -> List[Ban]:
    raw = _read_json_list(BANS_FILE)
    return [Ban.model_validate(b) for b in raw]


def save_bans(bans: List[Ban]) -> None:
    data = [b.model_dump(mode="json") for b in bans]
    _write_json_list(BANS_FILE, data)


def _next_ban_id(bans: List[Ban]) -> int:
    if not bans:
        return 1
    return max(b.banId for b in bans) + 1


def add_ban(
    *,
    user_name: str,
    reported_by: str,
    report_id: int,
    movie_title: str,
    review_user: str,
    reason_type: str,
    reason: Optional[str],
    ban_option: Literal["3d", "7d", "30d"],
    ban_duration_seconds: int,
    banned_at: Optional[datetime] = None,
) -> Ban:
    """
    Create and persist one Ban record in bans.json.

    Service layer should:
      - decide whether/when to call this (only on confirmed with banOption)
      - compute ban_duration_seconds (3/7/30 days)
      - update users.json.banExpiresAt separately
    """
    bans = load_bans()
    new_id = _next_ban_id(bans)
    banned_at = banned_at or datetime.utcnow()
    banned_until = banned_at + timedelta(seconds=ban_duration_seconds)

    ban = Ban(
        banId=new_id,
        userName=user_name,
        reportedBy=reported_by,
        reportId=report_id,
        movieTitle=movie_title,
        reviewUser=review_user,
        reasonType=reason_type,
        reason=reason,
        banOption=ban_option,
        banDurationSeconds=ban_duration_seconds,
        bannedAt=banned_at,
        bannedUntil=banned_until,
    )

    bans.append(ban)
    save_bans(bans)
    return ban


def list_bans(user_name: Optional[str] = None) -> List[Ban]:
    """
    - No user_name → all bans.
    - user_name → only bans for that username.
    """
    bans = load_bans()
    if user_name is None:
        return bans
    return [b for b in bans if b.userName == user_name]