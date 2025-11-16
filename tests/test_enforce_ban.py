# tests/test_enforce_ban.py

import time
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def make_review_payload(user: str = "bannedUser") -> dict:
    """Helper to build a valid Review payload for POST /reviews/{movieTitle}."""
    return {
        "movieTitle": "Joker",
        "user": user,
        "date": "2024-11-15",
        "rating": 8.0,
        "usefulVotes": 0,
        "totalVotes": 0,
        "title": "Test title",
        "body": "Test body",
        "reportCount": 0,
    }


@patch("backend.app.dependencies.find_user_by_username")
def test_banned_user_cannot_create_review(mock_find_user):
    """ensure_not_banned should block POST /reviews/{movieTitle} for banned users."""
    future_ts = time.time() + 3600  # ban for 1 hour from now

    mock_find_user.return_value = {
        "userName": "bannedUser",
        "passwordHash": "fake-hash",
        "role": "user",
        "penalties": 0,
        "watchlist": [],
        "banExpiresAt": future_ts,
    }

    response = client.post(
        "/reviews/Joker",
        json=make_review_payload(),
        headers={"X-Username": "bannedUser"},
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"] == "User is currently banned and cannot perform this action"


@patch("backend.app.dependencies.find_user_by_username")
def test_banned_user_cannot_delete_review(mock_find_user):
    """ensure_not_banned should block DELETE /reviews/{movieTitle}/{username} for banned users."""
    future_ts = time.time() + 3600

    mock_find_user.return_value = {
        "userName": "bannedUser",
        "passwordHash": "fake-hash",
        "role": "user",
        "penalties": 0,
        "watchlist": [],
        "banExpiresAt": future_ts,
    }

    response = client.delete(
        "/reviews/Joker/bannedUser",
        headers={"X-Username": "bannedUser"},
    )

    assert response.status_code == 403
    body = response.json()
    assert body["detail"] == "User is currently banned and cannot perform this action"