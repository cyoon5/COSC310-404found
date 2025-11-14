import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.services.authenticationService import AuthService
from backend.app.main import app
from passlib.hash import bcrypt

client = TestClient(app)


# UNIT TESTS

# Test exception when loading users fails during registration
@patch("backend.app.services.authenticationService.load_users", side_effect=Exception("Failed to read users"))
@patch("backend.app.services.authenticationService.load_admins", return_value=[])
def test_register_user_load_users_exception(mock_admins, mock_load_users):
    service = AuthService()
    with pytest.raises(Exception, match="Failed to read users"):
        service.register_user("newUser", "pass123")

# Test corrupt input to bcrypt during registration
@patch("backend.app.services.authenticationService.bcrypt.hash", side_effect=ValueError("Invalid password input"))
@patch("backend.app.services.authenticationService.load_users", return_value=[])
@patch("backend.app.services.authenticationService.load_admins", return_value=[])
def test_register_user_bcrypt_fault(mock_admins, mock_load_users, mock_hash):
    service = AuthService()
    with pytest.raises(ValueError, match="Invalid password input"):
        service.register_user("userFault", "badpass")


#Equivalence partitioning test for password length during login
@pytest.mark.parametrize("password", ["short", "longpassword123456789012345678901234567890"])
@patch("backend.app.services.authenticationService.load_users")
@patch("backend.app.services.authenticationService.load_admins", return_value=[])
def test_long_password (mock_admins, mock_load_users, password):
    hashed = bcrypt.hash(password[:72])
    mock_load_users.return_value = [{"userName": "user1", "passwordHash": hashed}]
    service = AuthService()
    result = service.login("user1", password)
    assert result["role"] == "user"

# Test successful user registration
@patch("backend.app.services.authenticationService.load_users", return_value=[])
@patch("backend.app.services.authenticationService.load_admins", return_value=[])
@patch("backend.app.services.authenticationService.add_user")
def test_register_user_success(mock_add, mock_admins, mock_users):
    service = AuthService()
    result = service.register_user("newUser", "password123")

    assert result["userName"] == "newUser"
    assert result["role"] == "user"
    assert "passwordHash" in result
    assert bcrypt.verify("password123", result["passwordHash"])
    mock_add.assert_called_once()


# Test if username already exists in users
@patch("backend.app.services.authenticationService.load_users", return_value=[
    {"userName": "existingUser", "passwordHash": "x"}
])
@patch("backend.app.services.authenticationService.load_admins", return_value=[])
def test_register_user_duplicate_user(mock_admins, mock_users):
    service = AuthService()
    with pytest.raises(ValueError, match="Username already exists"):
        service.register_user("existingUser", "password")


# Test if username already exists in admins
@patch("backend.app.services.authenticationService.load_users", return_value=[])
@patch("backend.app.services.authenticationService.load_admins", return_value=[
    {"adminName": "existingAdmin", "passwordHash": "x"}
])
def test_register_user_duplicate_admin(mock_admins, mock_users):
    service = AuthService()
    with pytest.raises(ValueError, match="Username already exists"):
        service.register_user("existingAdmin", "password")


# Test if login works for user
@patch("backend.app.services.authenticationService.load_users")
@patch("backend.app.services.authenticationService.load_admins", return_value=[])
def test_login_user_success(mock_admins, mock_users):
    hashed = bcrypt.hash("mypassword")
    mock_users.return_value = [{"userName": "testUser", "passwordHash": hashed}]

    service = AuthService()
    result = service.login("testUser", "mypassword")

    assert result["username"] == "testUser"
    assert result["role"] == "user"


# Test for wrong user password
@patch("backend.app.services.authenticationService.load_users")
@patch("backend.app.services.authenticationService.load_admins", return_value=[])
def test_login_wrong_user_password(mock_admins, mock_users):
    hashed = bcrypt.hash("correctpw")
    mock_users.return_value = [{"userName": "john", "passwordHash": hashed}]

    service = AuthService()
    with pytest.raises(ValueError, match="Incorrect password"):
        service.login("john", "wrongpw")


# Test admin login success
@patch("backend.app.services.authenticationService.load_users", return_value=[])
@patch("backend.app.services.authenticationService.load_admins")
def test_login_admin_success(mock_admins, mock_users):
    hashed = bcrypt.hash("adminpw")
    mock_admins.return_value = [{"adminName": "admin1", "passwordHash": hashed}]

    service = AuthService()
    result = service.login("admin1", "adminpw")

    assert result["username"] == "admin1"
    assert result["role"] == "admin"


# Test for wrong admin password
@patch("backend.app.services.authenticationService.load_users", return_value=[])
@patch("backend.app.services.authenticationService.load_admins")
def test_login_admin_wrong_password(mock_admins, mock_users):
    hashed = bcrypt.hash("correctpw")
    mock_admins.return_value = [{"adminName": "adminX", "passwordHash": hashed}]
    service = AuthService()
    with pytest.raises(ValueError, match="Incorrect password"):
        service.login("adminX", "wrongpw")


# Test if the username not found in either users or admins
@patch("backend.app.services.authenticationService.load_users", return_value=[])
@patch("backend.app.services.authenticationService.load_admins", return_value=[])
def test_login_not_found(mock_admins, mock_users):
    service = AuthService()
    with pytest.raises(ValueError, match="Username not found"):
        service.login("ghost", "anything")


# INTEGRATION TESTS

# testing register endpoint
@patch("backend.app.services.authenticationService.add_user")
@patch("backend.app.services.authenticationService.load_users", return_value=[])
@patch("backend.app.services.authenticationService.load_admins", return_value=[])
def test_integration_register(mock_admins, mock_load, mock_add):
    response = client.post("/auth/register", json={
        "username": "intUser",
        "password": "pass123"
    })

    assert response.status_code == 200
    mock_add.assert_called_once()
    data = response.json()
    assert data["user"]["userName"] == "intUser"

# testing register and login endpoints together
@patch("backend.app.services.authenticationService.add_user")
@patch("backend.app.services.authenticationService.load_users", return_value=[])
@patch("backend.app.services.authenticationService.load_admins", return_value=[])
def test_integration_register_and_login(mock_load_admins, mock_load_users, mock_add_user):
    # Register
    response = client.post("/auth/register", json={
        "username": "intUser",
        "password": "pass123"
    })

    assert response.status_code == 200
    mock_add_user.assert_called_once()

    # Mock that this user now exists for login
    mock_load_users.return_value = [{
        "userName": "intUser",
        "passwordHash": bcrypt.hash("pass123"),
        "role": "user",
        "penalties": 0,
        "watchlist": []
    }]

    # Logging in
    response_login = client.post("/auth/login", json={
        "username": "intUser",
        "password": "pass123"
    })
    assert response_login.status_code == 200
    assert response_login.json()["role"] == "user"



# login wrong password, test endpoint
def test_integration_login_wrong():
    response = client.post("/auth/login", json={"username": "nouser", "password": "wrong"})
    assert response.status_code == 401


# admin login (using mocked repo)
@patch("backend.app.services.authenticationService.load_users", return_value=[])
@patch("backend.app.services.authenticationService.load_admins")
def test_integration_admin_login(mock_admins, mock_users):
    hashed = bcrypt.hash("secret")
    mock_admins.return_value = [{"adminName": "master", "passwordHash": hashed}]

    response = client.post("/auth/login", json={
        "username": "master",
        "password": "secret"
    })

    assert response.status_code == 200
    assert response.json()["role"] == "admin"
