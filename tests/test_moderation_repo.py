import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from backend.app.repositories import moderationRepo
from backend.app.models.models import Report


# ---------------------------------------------------------------------------
# Helpers to point moderationRepo at a temporary data dir
# ---------------------------------------------------------------------------

def setup_temp_data_dir(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    imdb_dir = data_dir / "imdb"
    reports_file = data_dir / "reports.json"
    bans_file = data_dir / "bans.json"

    monkeypatch.setattr(moderationRepo, "DATA_DIR", data_dir, raising=False)
    monkeypatch.setattr(moderationRepo, "IMDB_DIR", imdb_dir, raising=False)
    monkeypatch.setattr(moderationRepo, "REPORTS_FILE", reports_file, raising=False)
    monkeypatch.setattr(moderationRepo, "BANS_FILE", bans_file, raising=False)

    return data_dir, imdb_dir, reports_file, bans_file


# ---------------------------------------------------------------------------
# _read_json_list basic behaviour
# ---------------------------------------------------------------------------

def test_read_json_list_missing_and_empty(tmp_path):
    missing = tmp_path / "missing.json"
    assert moderationRepo._read_json_list(missing) == []

    empty = tmp_path / "empty.json"
    empty.write_text("   ", encoding="utf-8")
    assert moderationRepo._read_json_list(empty) == []


def test_read_json_list_invalid_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        moderationRepo._read_json_list(bad)


# ---------------------------------------------------------------------------
# build_snapshot_and_increment_reports
# ---------------------------------------------------------------------------

def _write_sample_csv(imdb_dir: Path, movie: str, user: str, reports: str = "1") -> Path:
    movie_dir = imdb_dir / movie
    movie_dir.mkdir(parents=True, exist_ok=True)
    csv_path = movie_dir / "movieReviews.csv"

    fieldnames = [
        "User",
        "User's Rating out of 10",
        "Usefulness Vote",
        "Total Votes",
        "Review Title",
        "Review",
        "Reports",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "User": user,
                "User's Rating out of 10": "8.5",
                "Usefulness Vote": "5",
                "Total Votes": "10",
                "Review Title": "Good movie",
                "Review": "Nice review",
                "Reports": reports,
            }
        )
    return csv_path


def test_build_snapshot_and_increment_reports_happy_path(tmp_path, monkeypatch):
    _, imdb_dir, _, _ = setup_temp_data_dir(tmp_path, monkeypatch)
    csv_path = _write_sample_csv(imdb_dir, "Joker", "TVpotatoCat", reports="1")

    snapshot = moderationRepo.build_snapshot_and_increment_reports("Joker", "TVpotatoCat")

    # CSV should have Reports incremented
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["Reports"] == "2"

    # Snapshot fields parsed correctly
    assert snapshot.movieTitle == "Joker"
    assert snapshot.user == "TVpotatoCat"
    assert snapshot.rating == pytest.approx(8.5)
    assert snapshot.usefulVotes == 5
    assert snapshot.totalVotes == 10
    assert snapshot.title == "Good movie"
    assert snapshot.body == "Nice review"
    assert snapshot.reportCount == 2


def test_build_snapshot_and_increment_reports_missing_csv_raises(tmp_path, monkeypatch):
    setup_temp_data_dir(tmp_path, monkeypatch)
    with pytest.raises(FileNotFoundError):
        moderationRepo.build_snapshot_and_increment_reports("NoSuchMovie", "User")


def test_build_snapshot_and_increment_reports_missing_user_raises(tmp_path, monkeypatch):
    _, imdb_dir, _, _ = setup_temp_data_dir(tmp_path, monkeypatch)
    # CSV with different user
    _write_sample_csv(imdb_dir, "Joker", "SomeoneElse", reports="0")

    with pytest.raises(ValueError):
        moderationRepo.build_snapshot_and_increment_reports("Joker", "TVpotatoCat")


# ---------------------------------------------------------------------------
# Reports: create / load / replace / list / list_for_review
# ---------------------------------------------------------------------------

def test_create_report_for_review_and_list(tmp_path, monkeypatch):
    _, imdb_dir, _, _ = setup_temp_data_dir(tmp_path, monkeypatch)
    _write_sample_csv(imdb_dir, "Joker", "TVpotatoCat", reports="0")

    report = moderationRepo.create_report_for_review(
        movie_title="Joker",
        review_user="TVpotatoCat",
        reported_by="Alice",
        reason_type="spam",
        reason="Looks spammy",
    )

    # Returned report basic sanity
    assert isinstance(report.reportId, int)
    assert report.review.user == "TVpotatoCat"
    assert report.reasonType == "spam"
    assert report.status == "pending"

    # Persisted into reports.json
    all_reports = moderationRepo.load_reports()
    assert len(all_reports) == 1
    assert all_reports[0].reportId == report.reportId

    # list_reports with and without status
    assert moderationRepo.list_reports() == all_reports
    pending = moderationRepo.list_reports(status="pending")
    assert pending == all_reports


def test_replace_report_success_and_error(tmp_path, monkeypatch):
    _, imdb_dir, _, _ = setup_temp_data_dir(tmp_path, monkeypatch)
    _write_sample_csv(imdb_dir, "Joker", "TVpotatoCat", reports="0")

    # Create one report
    original = moderationRepo.create_report_for_review(
        movie_title="Joker",
        review_user="TVpotatoCat",
        reported_by="Alice",
        reason_type="spam",
        reason="Looks spammy",
    )

    # Successful replace
    updated = original.model_copy()
    updated.status = "confirmed"
    moderationRepo.replace_report(updated)
    after = moderationRepo.load_reports()[0]
    assert after.status == "confirmed"

    # Error path: id not found
    missing = original.model_copy()
    missing.reportId = 999
    with pytest.raises(ValueError, match="Report with id 999 not found"):
        moderationRepo.replace_report(missing)


def test_list_pending_and_list_reports_for_review(tmp_path, monkeypatch):
    _, imdb_dir, _, _ = setup_temp_data_dir(tmp_path, monkeypatch)
    _write_sample_csv(imdb_dir, "Joker", "TVpotatoCat", reports="0")

    # Two reports for the SAME underlying review/user
    r1 = moderationRepo.create_report_for_review(
        "Joker", "TVpotatoCat", "Alice", "spam", "one"
    )
    r2 = moderationRepo.create_report_for_review(
        "Joker", "TVpotatoCat", "Bob", "abuse", "two"
    )

    # Mark second as confirmed to exercise the pending filter
    r2.status = "confirmed"
    moderationRepo.replace_report(r2)

    pending = moderationRepo.list_pending_reports()
    assert {r.reportId for r in pending} == {r1.reportId}

    for_review = moderationRepo.list_reports_for_review("Joker", "TVpotatoCat")
    assert len(for_review) == 2
    assert {r.reportId for r in for_review} == {r1.reportId, r2.reportId}

    none_for_other_movie = moderationRepo.list_reports_for_review("OtherMovie", "X")
    assert none_for_other_movie == []


# ---------------------------------------------------------------------------
# Bans: add_ban + list_bans
# ---------------------------------------------------------------------------

def test_add_ban_and_list_bans(tmp_path, monkeypatch):
    setup_temp_data_dir(tmp_path, monkeypatch)

    base_time = datetime(2024, 1, 1, 12, 0, 0)
    seconds = 3 * 24 * 3600

    ban1 = moderationRepo.add_ban(
        user_name="TVpotatoCat",
        reported_by="Alice",
        report_id=1,
        movie_title="Joker",
        review_user="TVpotatoCat",
        reason_type="spam",
        reason="bad review",
        ban_option="3d",
        ban_duration_seconds=seconds,
        banned_at=base_time,
    )

    assert ban1.banId == 1
    assert ban1.userName == "TVpotatoCat"
    assert ban1.banOption == "3d"
    assert ban1.banDurationSeconds == seconds
    assert ban1.bannedAt == base_time
    assert ban1.bannedUntil == base_time + timedelta(seconds=seconds)

    # Second ban for a different user to exercise _next_ban_id and filtering
    ban2 = moderationRepo.add_ban(
        user_name="OtherUser",
        reported_by="Charlie",
        report_id=2,
        movie_title="Joker",
        review_user="OtherUser",
        reason_type="abuse",
        reason="mean",
        ban_option="7d",
        ban_duration_seconds=7 * 24 * 3600,
        banned_at=base_time,
    )
    assert ban2.banId == 2

    all_bans = moderationRepo.list_bans()
    assert len(all_bans) == 2

    cat_bans = moderationRepo.list_bans(user_name="TVpotatoCat")
    assert [b.userName for b in cat_bans] == ["TVpotatoCat"]

    none = moderationRepo.list_bans(user_name="Nobody")
    assert none == []