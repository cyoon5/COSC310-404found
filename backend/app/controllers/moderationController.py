from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from ..models.models import (
    Report,
    Ban,
    ReportCreate,
    ReportDecisionRequest,
)
from ..services.moderationService import ModerationService
from app.dependencies import get_current_user, admin_required

router = APIRouter(prefix="/moderation", tags=["Moderation"])

moderation_service = ModerationService()

# ─────────────────────────────────────────────
# 3. Deciding a report (confirm / reject + ban)
#  (put this BEFORE the generic /reports/{movie_title}/{review_user})
# ─────────────────────────────────────────────

@router.post("/reports/{report_id}/decision")
def decide_report(
    report_id: int,
    payload: ReportDecisionRequest,
    admin: dict = Depends(admin_required),
):
    """
    POST /moderation/reports/{report_id}/decision

    Body:
    {
      "action": "confirm" | "reject",
      "banOption": "3d" | "7d" | "30d" | null
    }

    Admin-only: confirm or reject a report, optionally applying a ban.
    """
    try:
        report, ban = moderation_service.decide_report(
            report_id=report_id,
            decision=payload,
            admin_username=admin["username"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = {
        "message": "Report decided successfully",
        "report": report,
    }
    if ban is not None:
        response["ban"] = ban
    return response


# ─────────────────────────────────────────────
# 1. Reporting a review (user or admin)
# ─────────────────────────────────────────────

@router.post("/reports/{movie_title}/{review_user}")
def report_review(
    movie_title: str,
    review_user: str,
    payload: ReportCreate,
    current_user: dict = Depends(get_current_user),
):
    """
    POST /moderation/reports/{movie_title}/{review_user}

    Any logged-in user or admin can report a review.
    """
    try:
        report = moderation_service.report_review(
            movie_title=movie_title,
            review_user=review_user,
            current_username=current_user["username"],
            payload=payload,
        )
        return {
            "message": "Report created successfully",
            "report": report,
        }
    except FileNotFoundError as e:
        # No CSV for that movie
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        # Review not found, or other logical problem
        raise HTTPException(status_code=400, detail=str(e))


# ─────────────────────────────────────────────
# 2. Listing reports (admin only)
# ─────────────────────────────────────────────

@router.get("/reports/pending", response_model=List[Report])
def get_pending_reports(
    admin: dict = Depends(admin_required),
):
    """
    GET /moderation/reports/pending

    Admin-only: list all pending reports.
    """
    return moderation_service.list_pending_reports()


@router.get("/reports", response_model=List[Report])
def get_reports(
    status: Optional[str] = Query(
        None,
        description='Optional status filter: "pending", "confirmed", or "rejected"',
    ),
    admin: dict = Depends(admin_required),
):
    """
    GET /moderation/reports
    GET /moderation/reports?status=pending

    Admin-only: list all reports, optionally filtered by status.
    """
    if status is not None and status not in {"pending", "confirmed", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status value")

    return moderation_service.list_reports(status=status)  # type: ignore[arg-type]


@router.get(
    "/reports/review/{movie_title}/{review_user}",
    response_model=List[Report],
)
def get_reports_for_review(
    movie_title: str,
    review_user: str,
    admin: dict = Depends(admin_required),
):
    """
    GET /moderation/reports/review/{movie_title}/{review_user}

    Admin-only: all reports (any status) for a specific review.
    """
    return moderation_service.list_reports_for_review(movie_title, review_user)


# ─────────────────────────────────────────────
# 4. Bans listing (admin only)
# ─────────────────────────────────────────────

@router.get("/bans", response_model=List[Ban])
def get_bans(
    userName: Optional[str] = Query(
        None,
        alias="userName",
        description="If provided, only bans for this userName are returned",
    ),
    admin: dict = Depends(admin_required),
):
    """
    GET /moderation/bans
    GET /moderation/bans?userName=foo

    Admin-only: list all bans, or only bans for a specific userName.
    """
    return moderation_service.list_bans(user_name=userName)