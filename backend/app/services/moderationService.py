from __future__ import annotations

from typing import List, Optional, Tuple, Literal
from datetime import datetime

from ..models.models import (
    Report,
    ReportCreate,
    ReportDecisionRequest,
    Ban,
)
from ..repositories import moderationRepo
from ..repositories.usersRepo import load_users, save_users


# Map banOption → seconds
BAN_OPTION_TO_SECONDS = {
    "3d": 3 * 24 * 3600,
    "7d": 7 * 24 * 3600,
    "30d": 30 * 24 * 3600,
}


class ModerationService:
    """
    Orchestrates moderation behaviour:
      - reporting reviews
      - listing reports
      - deciding reports (confirm/reject + penalties + bans)
      - listing bans
    """

    # ─────────────────────────────────────────────
    # 1. Reporting a review
    # ─────────────────────────────────────────────

    def report_review(
        self,
        movie_title: str,
        review_user: str,
        current_username: str,
        payload: ReportCreate,
    ) -> Report:
        """
        Implements the user story:

        - As a signed-in user, I report a review with reasonType + reason.
        - Increments CSV Reports, builds snapshot, stores a new Report in reports.json.
        """
        report = moderationRepo.create_report_for_review(
            movie_title=movie_title,
            review_user=review_user,
            reported_by=current_username,
            reason_type=payload.reasonType,
            reason=payload.reason,
        )
        return report

    # ─────────────────────────────────────────────
    # 2. Listing reports
    # ─────────────────────────────────────────────

    def list_pending_reports(self) -> List[Report]:
        """
        Admin story: view all open moderation work.
        """
        return moderationRepo.list_pending_reports()

    def list_reports(
        self,
        status: Optional[Literal["pending", "confirmed", "rejected"]] = None,
    ) -> List[Report]:
        """
        Admin story: list all reports, optionally filtered by status.
        """
        return moderationRepo.list_reports(status=status)

    def list_reports_for_review(
        self,
        movie_title: str,
        review_user: str,
    ) -> List[Report]:
        """
        Admin story: see all reports ever filed against one specific review.
        """
        return moderationRepo.list_reports_for_review(movie_title, review_user)

    # ─────────────────────────────────────────────
    # 3. Deciding a report (confirm / reject + ban)
    # ─────────────────────────────────────────────

    def decide_report(
        self,
        report_id: int,
        decision: ReportDecisionRequest,
        admin_username: str,
    ) -> Tuple[Report, Optional[Ban]]:
        """
        Implements POST /moderation/reports/{report_id}/decision

        Behaviour:
          - reject → status=rejected, handledByAdmin/handledAt set, no ban.
          - confirm → status=confirmed, penalties incremented for registered user,
                      optional ban created & logged in bans.json + banExpiresAt updated.
        """
        report = moderationRepo.get_report_by_id(report_id)
        if report is None:
            raise ValueError("Report not found")

        if report.status in ("confirmed", "rejected"):
            raise ValueError("Report already decided")

        now = datetime.utcnow()

        # Common fields for both paths
        report.handledByAdmin = admin_username
        report.handledAt = now

        if decision.action == "reject":
            # ── Reject branch ──
            report.status = "rejected"
            report.banDurationSeconds = None

            moderationRepo.replace_report(report)
            return report, None

        # ── Confirm branch ──
        report.status = "confirmed"

        # 3.1 Increment penalties for registered users
        self._increment_penalties_for_review_author(report)

        # 3.2 Ban handling
        ban_obj: Optional[Ban] = None

        if decision.banOption is None:
            # Confirm but no ban
            report.banDurationSeconds = None
            moderationRepo.replace_report(report)
            return report, None

        # Confirm with ban
        ban_option = decision.banOption
        if ban_option not in BAN_OPTION_TO_SECONDS:
            raise ValueError(f"Invalid ban option: {ban_option}")

        ban_duration_seconds = BAN_OPTION_TO_SECONDS[ban_option]
        report.banDurationSeconds = ban_duration_seconds

        # Create ban record in bans.json
        review_snapshot = report.review
        ban_obj = moderationRepo.add_ban(
            user_name=review_snapshot.user,
            reported_by=report.reportedBy,
            report_id=report.reportId,
            movie_title=review_snapshot.movieTitle,
            review_user=review_snapshot.user,
            reason_type=report.reasonType,
            reason=report.reason,
            ban_option=ban_option,
            ban_duration_seconds=ban_duration_seconds,
            banned_at=now,
        )

        # 3.3 Update banExpiresAt for registered users (if they exist)
        self._update_ban_expires_for_user(
            username=review_snapshot.user,
            banned_until=ban_obj.bannedUntil,
        )

        # 3.4 Persist updated report
        moderationRepo.replace_report(report)

        return report, ban_obj

    # ─────────────────────────────────────────────
    # 3a. Helpers: penalties + banExpiresAt
    # ─────────────────────────────────────────────

    def _increment_penalties_for_review_author(self, report: Report) -> None:
        """
        Look up review.user in users.json; if present, increment penalties by 1.

        CSV-only reviewers (no users.json entry) are ignored here.
        """
        review_author = report.review.user
        users = load_users()
        changed = False

        for user in users:
            if user.get("userName") == review_author:
                # Ensure penalties field exists and is int-like
                penalties = user.get("penalties", 0)
                try:
                    penalties = int(penalties)
                except (ValueError, TypeError):
                    penalties = 0
                user["penalties"] = penalties + 1
                changed = True
                break

        if changed:
            save_users(users)
        # If not found → CSV-only reviewer; nothing to update.

    def _update_ban_expires_for_user(self, username: str, banned_until: datetime) -> None:
        """
        For registered users, set banExpiresAt to the Unix timestamp of banned_until.

        If user doesn't exist in users.json → do nothing (CSV-only reviewer).
        If user already has a future banExpiresAt → we simply overwrite with this latest ban.
        """
        users = load_users()
        changed = False
        ts = int(banned_until.timestamp())

        for user in users:
            if user.get("userName") == username:
                user["banExpiresAt"] = ts
                changed = True
                break

        if changed:
            save_users(users)

    # ─────────────────────────────────────────────
    # 4. Bans listing
    # ─────────────────────────────────────────────

    def list_bans(self, user_name: Optional[str] = None) -> List[Ban]:
        """
        Admin story:

          - GET /moderation/bans → list all bans
          - GET /moderation/bans?userName=foo → all bans for 'foo'
        """
        return moderationRepo.list_bans(user_name=user_name)