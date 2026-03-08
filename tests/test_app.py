from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Ensure each test gets a fresh copy of the in-memory activity state."""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirects_to_static_index():
    client = TestClient(app)

    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_list():
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()


def test_signup_adds_participant():
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"

    # Arrange
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_already_registered_returns_400():
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity_name)}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400


def test_signup_nonexistent_activity_returns_404():
    client = TestClient(app)

    # Act
    response = client.post(
        "/activities/Nonexistent/signup", params={"email": "nobody@mergington.edu"}
    )

    # Assert
    assert response.status_code == 404


def test_unregister_removes_participant():
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"

    # Arrange
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Removed {email} from {activity_name}"


def test_unregister_missing_participant_returns_404():
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity_name)}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
