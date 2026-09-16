import uuid

import pytest
from sqlalchemy.pool import StaticPool

from data5580_hw.app import create_app
from data5580_hw.models.user_model import User, validate_email

INVALID_EMAIL_PAYLOAD = {
    "name": "Hikaru",
    "email": "rjfioefjrioeexamplecom",
}


def unique_email(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def client():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "connect_args": {"check_same_thread": False},
                "poolclass": StaticPool,
            },
        }
    )
    with app.test_client() as test_client:
        yield test_client


def create_user(client, name="Hikaru", email=None):
    response = client.post(
        "/users",
        json={"name": name, "email": email or unique_email(name.lower())},
    )
    assert response.status_code == 200
    return response.json


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json == {"message": "Hello World!"}


def test_create_app_without_test_config():
    app = create_app()
    assert app.testing is False
    with app.test_client() as test_client:
        response = test_client.get("/")
        assert response.status_code == 200


def test_fetch_all_users(client):
    """Acceptance Criteria 5: GET /users returns a list of users."""
    empty = client.get("/users")
    assert empty.status_code == 200
    assert empty.json == []

    create_user(client, name="User1", email="User1@example.com")
    create_user(client, name="User2", email="User2@example.com")

    response = client.get("/users")
    assert response.status_code == 200
    users = response.json
    assert isinstance(users, list)
    assert len(users) == 2
    assert {user["name"] for user in users} == {"User1", "User2"}


def test_create_user_success(client):
    """Acceptance Criteria 1: POST /users stores a user and returns a unique id."""
    payload = {"name": "Hikaru", "email": "hikaru@example.com"}
    response = client.post("/users", json=payload)

    assert response.status_code == 200
    assert response.json["name"] == "Hikaru"
    assert response.json["email"] == "hikaru@example.com"
    assert response.json["message"] == "User created successfully."
    assert response.json["id"]
    assert len(response.json["id"]) == 32


def test_create_user_ids_are_unique(client):
    """Acceptance Criteria 1: IDs are unique (nuance)."""
    first = create_user(client, name="Hikaru", email="hikaru@example.com")
    second = create_user(client, name="Zack", email="zack@example.com")
    assert first["id"] != second["id"]


def test_create_user_duplicate_email(client):
    """Acceptance Criteria 1 and 6: duplicate email returns 400."""
    payload = {"name": "Hikaru", "email": "hikaru@example.com"}
    client.post("/users", json=payload)
    response = client.post("/users", json=payload)

    assert response.status_code == 400
    assert response.json["error"] == "the email is already in use"


def test_create_user_invalid_email(client):
    """Acceptance Criteria 9: invalid email format returns 400."""
    response = client.post("/users", json=INVALID_EMAIL_PAYLOAD)
    assert response.status_code == 400
    assert response.json["error"] == "Invalid email format"


def test_create_user_invalid_email_type(client):
    """Acceptance Criteria 9: empty or non-string email is invalid."""
    empty = client.post("/users", json={"name": "Hikaru", "email": ""})
    assert empty.status_code == 400
    assert empty.json["error"] == "Invalid email format"

    number = client.post("/users", json={"name": "Hikaru", "email": 12345678})
    assert number.status_code == 400
    assert number.json["error"] == "Invalid email format"


def test_create_user_missing_keys(client):
    """Acceptance Criteria 8/9: missing required fields return 400."""
    missing_email = client.post("/users", json={"name": "Hikaru"})
    assert missing_email.status_code == 400
    assert missing_email.json["error"] == "email is required"

    missing_name = client.post("/users", json={"email": "hikaru@example.com"})
    assert missing_name.status_code == 400
    assert missing_name.json["error"] == "name is required"

    missing_body = client.post("/users", json={})
    assert missing_body.status_code == 400
    assert "is required" in missing_body.json["error"]


def test_create_user_invalid_json(client):
    response = client.post(
        "/users",
        data="not-json",
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "is required" in response.json["error"]


def test_get_user_by_id(client):
    """Acceptance Criteria 2: GET /users/{id} returns stored details."""
    created = create_user(client, name="DetailUser")
    response = client.get(f"/users/{created['id']}")

    assert response.status_code == 200
    assert response.json["id"] == created["id"]
    assert response.json["name"] == "DetailUser"
    assert response.json["email"] == created["email"]


def test_get_user_not_found(client):
    """Acceptance Criteria 2: unknown id returns 404."""
    response = client.get("/users/42fewghbfte")
    assert response.status_code == 404
    assert response.json["error"] == "User not found"


def test_patch_user_by_id(client):
    """Acceptance Criteria 3: PATCH updates provided fields."""
    created = create_user(client, name="hikaru_old", email="hikaru_old@example.com")
    user_id = created["id"]

    both = client.patch(
        f"/users/{user_id}",
        json={"name": "Hikaru_new", "email": "Hikaru_new@example.com"},
    )
    assert both.status_code == 200
    assert both.json["id"] == user_id
    assert both.json["name"] == "Hikaru_new"
    assert both.json["email"] == "Hikaru_new@example.com"
    assert both.json["message"] == "User updated successfully."

    name_only = client.patch(f"/users/{user_id}", json={"name": "Takumi_new"})
    assert name_only.status_code == 200
    assert name_only.json["id"] == user_id
    assert name_only.json["name"] == "Takumi_new"
    assert name_only.json["email"] == "Hikaru_new@example.com"
    assert name_only.json["message"] == "User updated successfully."

    email_only = client.patch(
        f"/users/{user_id}",
        json={"email": "takumi_new@example.com"},
    )
    assert email_only.status_code == 200
    assert email_only.json["id"] == user_id
    assert email_only.json["name"] == "Takumi_new"
    assert email_only.json["email"] == "takumi_new@example.com"
    assert email_only.json["message"] == "User updated successfully."


def test_patch_user_errors(client):
    """Acceptance Criteria 8 and 9 for PATCH."""
    created = create_user(client, name="hikaru_old", email="hikaru_old@example.com")
    user_id = created["id"]

    missing = client.patch(f"/users/{user_id}", json={})
    assert missing.status_code == 400
    assert missing.json["error"] == (
        "No valid fields to update. You need name or email to update"
    )

    invalid_email = client.patch(f"/users/{user_id}", json=INVALID_EMAIL_PAYLOAD)
    assert invalid_email.status_code == 400
    assert invalid_email.json["error"] == "Invalid email format"

    missing_user = client.patch(
        "/users/42fewghbfte",
        json={"name": "john_fake", "email": "john_fake@example.com"},
    )
    assert missing_user.status_code == 404
    assert missing_user.json["error"] == "User not found"


def test_delete_user_by_id(client):
    """Acceptance Criteria 4: DELETE removes an existing user."""
    created = create_user(client, name="User_for_delete")
    user_id = created["id"]

    deleted = client.delete(f"/users/{user_id}")
    assert deleted.status_code == 200
    assert deleted.json["message"] == "User deleted successfully."

    missing = client.get(f"/users/{user_id}")
    assert missing.status_code == 404


def test_delete_user_not_found(client):
    """Acceptance Criteria 4: DELETE unknown id returns 404."""
    response = client.delete("/users/fakefakefake")
    assert response.status_code == 404
    assert response.json["error"] == "User not found"


def test_put_user_by_id(client):
    """Acceptance Criteria 7: PUT replaces name and email."""
    created = create_user(client, name="Ben_old", email="ben_old@example.com")
    response = client.put(
        f"/users/{created['id']}",
        json={"name": "Ben_new", "email": "Ben_new@example.com"},
    )

    assert response.status_code == 200
    assert response.json["id"] == created["id"]
    assert response.json["name"] == "Ben_new"
    assert response.json["email"] == "Ben_new@example.com"
    assert response.json["message"] == "User details updated successfully."


def test_put_user_errors(client):
    """Acceptance Criteria 8 and 9 for PUT."""
    created = create_user(client, name="Ben_old", email="ben_old@example.com")
    user_id = created["id"]

    missing_email = client.put(f"/users/{user_id}", json={"name": "Alice_new"})
    assert missing_email.status_code == 400
    assert missing_email.json["error"] == "You need email to update."

    missing_name = client.put(
        f"/users/{user_id}",
        json={"email": "Alice_new@example.com"},
    )
    assert missing_name.status_code == 400
    assert missing_name.json["error"] == "You need name to update."

    empty = client.put(f"/users/{user_id}", json={})
    assert empty.status_code == 400
    assert empty.json["error"] == "No valid fields to update. You need name and email."

    invalid_email = client.put(f"/users/{user_id}", json=INVALID_EMAIL_PAYLOAD)
    assert invalid_email.status_code == 400
    assert invalid_email.json["error"] == "Invalid email format"

    missing_user = client.put(
        "/users/481grwfwe34",
        json={"name": "john_fake5", "email": "john_fake5@example.com"},
    )
    assert missing_user.status_code == 404
    assert missing_user.json["error"] == "User not found"


def test_update_duplicate_email(client):
    """Acceptance Criteria 6: email stays unique on PATCH and PUT."""
    create_user(client, name="UserOne", email="existing@example.com")
    second = create_user(client, name="UserTwo", email="twouser@example.com")

    patch_response = client.patch(
        f"/users/{second['id']}",
        json={"email": "existing@example.com"},
    )
    assert patch_response.status_code == 400
    assert patch_response.json["error"] == "the email is already in use"

    put_response = client.put(
        f"/users/{second['id']}",
        json={"name": "new_existing", "email": "existing@example.com"},
    )
    assert put_response.status_code == 400
    assert put_response.json["error"] == "the email is already in use"


def test_validate_email_and_user_mapping():
    assert validate_email("valid@example.com") is True
    assert validate_email("bad-email") is False
    assert validate_email(None) is False
    assert User.from_user_sql(None) is None
