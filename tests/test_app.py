from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_success():
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_success():
    activity_name = "Chess Club"
    email = "removeme@mergington.edu"

    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
