import pytest
from unittest.mock import patch
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.services.moderationService import (
    ModerationService,
    BAN_OPTION_TO_SECONDS,
)
from backend.app.models.models import (
    ReviewSnapshot,
    Report,
    ReportCreate,
    ReportDecisionRequest,
    Ban,
)
from backend.app.main import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_snapshot(movie: str = "Joker", user: str = "TVpotatoCat") -> ReviewSnapshot:
    return ReviewSnapshot(
        movieTitle=movie,
        user=user,
        rating=8.0,
        usefulVotes=5,
        totalVotes=10,
        title="Good movie",
        body="Body text",
        reportCount=1,
    )


def make_pending_report(
    report_id: int = 1,
    movie: str = "Joker",
    user: str = "TVpotatoCat",
) -> Report:
    snapshot = make_snapshot(movie=movie, user=user)
    return Report(
        reportId=report_id,
        review=snapshot,
        reportedBy="Alice",
        status="pending",
        dateReported=datetime.utcnow(),
        reasonType="spam",
        reason="Looks like spam",
        handledByAdmin=None,
        handledAt=None,
        banDurationSeconds=None,
    )


def make_ban_from_report(report: Report, ban_option: str = "3d") -> Ban:
    now = datetime.utcnow()
    dur = BAN_OPTION_TO_SECONDS[ban_option]
    return Ban(
        banId=1,
        userName=report.review.user,
        reportedBy=report.reportedBy,
        reportId=report.reportId,
        movieTitle=report.review.movieTitle,
        reviewUser=report.review.user,
        reasonType=report.reasonType,
        reason=report.reason,
        banOption=ban_option,
        banDurationSeconds=dur,
        bannedAt=now,
        bannedUntil=now + timedelta(seconds=dur),
    )


# ---------------------------------------------------------------------------
# UNIT TESTS – ModerationService
# ---------------------------------------------------------------------------

@patch("backend.app.services.moderationService.moderationRepo.create_report_for_review")
def test_report_review_calls_repo_and_returns_report(mock_create):
    service = ModerationService()
    fake_report = make_pending_report()
    mock_create.return_value = fake_report

    payload = ReportCreate(reasonType="spam", reason="Test reason")

    result = service.report_review(
        movie_title="Joker",
        review_user="TVpotatoCat",
        current_username="Alice",
        payload=payload,
    )

    mock_create.assert_called_once_with(
        movie_title="Joker",
        review_user="TVpotatoCat",
        reported_by="Alice",
        reason_type="spam",
        reason="Test reason",
    )
    assert result is fake_report
    assert result.status == "pending"


@patch("backend.app.services.moderationService.moderationRepo.replace_report")
@patch("backend.app.services.moderationService.moderationRepo.get_report_by_id")
def test_decide_report_reject_updates_status_and_no_ban(mock_get, mock_replace):
    service = ModerationService()
    report = make_pending_report()
    mock_get.return_value = report

    decision = ReportDecisionRequest(action="reject", banOption=None)

    updated, ban = service.decide_report(
        report_id=1,
        decision=decision,
        admin_username="admin1",
    )

    assert updated.status == "rejected"
    assert updated.handledByAdmin == "admin1"
    assert updated.handledAt is not None
    assert updated.banDurationSeconds is None
    mock_replace.assert_called_once()
    assert ban is None


@patch.object(ModerationService, "_update_ban_expires_for_user")
@patch.object(ModerationService, "_increment_penalties_for_review_author")
@patch("backend.app.services.moderationService.moderationRepo.replace_report")
@patch("backend.app.services.moderationService.moderationRepo.get_report_by_id")
def test_decide_report_confirm_without_ban(
    mock_get,
    mock_replace,
    mock_inc_penalties,
    mock_update_ban,
):
    service = ModerationService()
    report = make_pending_report()
    mock_get.return_value = report

    decision = ReportDecisionRequest(action="confirm", banOption=None)

    updated, ban = service.decide_report(
        report_id=1,
        decision=decision,
        admin_username="admin1",
    )

    assert updated.status == "confirmed"
    assert updated.banDurationSeconds is None
    mock_inc_penalties.assert_called_once()
    mock_update_ban.assert_not_called()
    mock_replace.assert_called_once()
    assert ban is None


@patch.object(ModerationService, "_update_ban_expires_for_user")
@patch.object(ModerationService, "_increment_penalties_for_review_author")
@patch("backend.app.services.moderationService.moderationRepo.add_ban")
@patch("backend.app.services.moderationService.moderationRepo.replace_report")
@patch("backend.app.services.moderationService.moderationRepo.get_report_by_id")
def test_decide_report_confirm_with_ban(
    mock_get,
    mock_replace,
    mock_add_ban,
    mock_inc_penalties,
    mock_update_ban,
):
    service = ModerationService()
    report = make_pending_report()
    mock_get.return_value = report

    fake_ban = make_ban_from_report(report, ban_option="3d")
    mock_add_ban.return_value = fake_ban

    decision = ReportDecisionRequest(action="confirm", banOption="3d")

    updated, ban = service.decide_report(
        report_id=1,
        decision=decision,
        admin_username="admin1",
    )

    assert updated.status == "confirmed"
    assert updated.banDurationSeconds == BAN_OPTION_TO_SECONDS["3d"]
    mock_inc_penalties.assert_called_once()
    mock_add_ban.assert_called_once()
    mock_update_ban.assert_called_once_with(
        username=report.review.user,
        banned_until=fake_ban.bannedUntil,
    )
    mock_replace.assert_called_once()
    assert ban == fake_ban


@patch("backend.app.services.moderationService.moderationRepo.get_report_by_id", return_value=None)
def test_decide_report_raises_if_report_not_found(mock_get):
    service = ModerationService()
    decision = ReportDecisionRequest(action="confirm", banOption=None)

    with pytest.raises(ValueError, match="Report not found"):
        service.decide_report(
            report_id=99,
            decision=decision,
            admin_username="admin1",
        )


@patch("backend.app.services.moderationService.moderationRepo.get_report_by_id")
def test_decide_report_raises_if_already_decided(mock_get):
    report = make_pending_report()
    report.status = "confirmed"  # already decided
    mock_get.return_value = report

    service = ModerationService()
    decision = ReportDecisionRequest(action="confirm", banOption=None)

    with pytest.raises(ValueError, match="Report already decided"):
        service.decide_report(
            report_id=1,
            decision=decision,
            admin_username="admin1",
        )


def test_decide_report_invalid_ban_option_raises():
    # Pydantic should reject invalid banOption values
    with pytest.raises(ValidationError):
        ReportDecisionRequest(action="confirm", banOption="99d")


@patch("backend.app.services.moderationService.moderationRepo.list_pending_reports")
def test_list_pending_reports_delegates_to_repo(mock_list):
    service = ModerationService()
    fake_report = make_pending_report()
    mock_list.return_value = [fake_report]

    result = service.list_pending_reports()

    mock_list.assert_called_once()
    assert result == [fake_report]


@patch("backend.app.services.moderationService.moderationRepo.list_bans")
def test_list_bans_delegates_to_repo(mock_list):
    service = ModerationService()
    fake_ban = make_ban_from_report(make_pending_report())
    mock_list.return_value = [fake_ban]

    result = service.list_bans(user_name="TVpotatoCat")

    mock_list.assert_called_once_with(user_name="TVpotatoCat")
    assert result == [fake_ban]


# ---------------------------------------------------------------------------
# INTEGRATION TESTS – FastAPI endpoints (service mocked)
# ---------------------------------------------------------------------------

client = TestClient(app)


@patch("backend.app.dependencies.find_user_by_username", return_value={"userName": "alice"})
@patch("backend.app.controllers.moderationController.moderation_service.report_review")
def test_integration_report_review_endpoint(mock_report_review, mock_find_user):
    fake_report = make_pending_report()
    mock_report_review.return_value = fake_report

    response = client.post(
        "/moderation/reports/Joker/TVpotatoCat",
        json={"reasonType": "spam", "reason": "test"},
        headers={"X-Username": "alice"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Report created successfully"
    assert data["report"]["review"]["movieTitle"] == "Joker"
    assert data["report"]["review"]["user"] == "TVpotatoCat"
    mock_report_review.assert_called_once()


@patch("backend.app.controllers.moderationController.moderation_service.decide_report")
def test_integration_decide_report_endpoint_confirm_with_ban(mock_decide):
    report = make_pending_report()
    report.status = "confirmed"  # simulate service confirming it
    ban = make_ban_from_report(report, ban_option="3d")
    mock_decide.return_value = (report, ban)

    response = client.post(
        "/moderation/reports/1/decision",
        json={"action": "confirm", "banOption": "3d"},
        headers={"X-Username": "admin1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Report decided successfully"
    assert body["report"]["status"] == "confirmed"
    assert body["ban"]["banOption"] == "3d"
    mock_decide.assert_called_once()


@patch("backend.app.controllers.moderationController.moderation_service.decide_report")
def test_integration_decide_report_not_found_returns_400(mock_decide):
    mock_decide.side_effect = ValueError("Report not found")

    response = client.post(
        "/moderation/reports/99/decision",
        json={"action": "confirm", "banOption": None},
        headers={"X-Username": "admin1"},
    )

    assert response.status_code == 400
    assert "Report not found" in response.json()["detail"]
    mock_decide.assert_called_once()


@patch("backend.app.controllers.moderationController.moderation_service.list_bans")
def test_integration_get_bans_endpoint(mock_list_bans):
    report = make_pending_report()
    fake_ban = make_ban_from_report(report, ban_option="7d")
    mock_list_bans.return_value = [fake_ban]

    response = client.get(
        "/moderation/bans",
        params={"userName": "TVpotatoCat"},
        headers={"X-Username": "admin1"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["userName"] == "TVpotatoCat"
    assert data[0]["banOption"] == "7d"
    mock_list_bans.assert_called_once_with(user_name="TVpotatoCat")