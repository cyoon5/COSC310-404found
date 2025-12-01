# tests/test_watchlist.py

from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


# ---------- GET watchlist ----------

@patch("backend.app.dependencies.find_user_by_username")
@patch("backend.app.repositories.usersRepo.get_watchlist")
def test_get_my_watchlist(mock_get_watchlist, mock_find_user):
    mock_find_user.return_value = {
        "userName": "alice",
        "passwordHash": "x",
        "role": "user",
        "penalties": 0,
        "watchlist": ["Joker"],
        "banExpiresAt": None,
    }
    mock_get_watchlist.return_value = ["Joker"]

    resp = client.get("/watchlist", headers={"X-Username": "alice"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["watchlist"] == ["Joker"]
    mock_get_watchlist.assert_called_once_with("alice")


# ---------- POST watchlist (valid movie) ----------

@patch("backend.app.dependencies.find_user_by_username")
@patch("backend.app.repositories.usersRepo.add_to_watchlist")
@patch("backend.app.services.watchlistService.os.path.exists", return_value=True)
def test_add_to_my_watchlist_valid_movie(mock_exists, mock_add, mock_find_user):
    mock_find_user.return_value = {
        "userName": "alice",
        "passwordHash": "x",
        "role": "user",
        "penalties": 0,
        "watchlist": [],
        "banExpiresAt": None,
    }
    mock_add.return_value = ["Joker"]

    resp = client.post("/watchlist/Joker", headers={"X-Username": "alice"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "Movie added to watchlist"
    assert body["watchlist"] == ["Joker"]
    mock_exists.assert_called()  # ensure existence was checked
    mock_add.assert_called_once_with("alice", "Joker")


# ---------- POST watchlist (invalid / non-existent movie) ----------

@patch("backend.app.dependencies.find_user_by_username")
@patch("backend.app.services.watchlistService.os.path.exists", return_value=False)
def test_add_to_my_watchlist_invalid_movie(mock_exists, mock_find_user):
    mock_find_user.return_value = {
        "userName": "alice",
        "passwordHash": "x",
        "role": "user",
        "penalties": 0,
        "watchlist": [],
        "banExpiresAt": None,
    }

    resp = client.post("/watchlist/FakeMovie", headers={"X-Username": "alice"})

    assert resp.status_code == 400
    body = resp.json()
    assert body["detail"] == "Movie not found in IMDb dataset"
    mock_exists.assert_called()


# ---------- DELETE watchlist (valid movie) ----------

@patch("backend.app.dependencies.find_user_by_username")
@patch("backend.app.repositories.usersRepo.remove_from_watchlist")
@patch("backend.app.services.watchlistService.os.path.exists", return_value=True)
def test_remove_from_my_watchlist_valid_movie(mock_exists, mock_remove, mock_find_user):
    mock_find_user.return_value = {
        "userName": "alice",
        "passwordHash": "x",
        "role": "user",
        "penalties": 0,
        "watchlist": ["Joker"],
        "banExpiresAt": None,
    }
    mock_remove.return_value = []

    resp = client.delete("/watchlist/Joker", headers={"X-Username": "alice"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "Movie removed from watchlist"
    assert body["watchlist"] == []
    mock_exists.assert_called()
    mock_remove.assert_called_once_with("alice", "Joker")


# ---------- DELETE watchlist (invalid / non-existent movie) ----------

@patch("backend.app.dependencies.find_user_by_username")
@patch("backend.app.services.watchlistService.os.path.exists", return_value=False)
def test_remove_from_my_watchlist_invalid_movie(mock_exists, mock_find_user):
    mock_find_user.return_value = {
        "userName": "alice",
        "passwordHash": "x",
        "role": "user",
        "penalties": 0,
        "watchlist": ["Joker"],
        "banExpiresAt": None,
    }

    resp = client.delete("/watchlist/FakeMovie", headers={"X-Username": "alice"})

    assert resp.status_code == 400
    body = resp.json()
    assert body["detail"] == "Movie not found in IMDb dataset"
    mock_exists.assert_called()