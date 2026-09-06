from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def reset_activity_state():
    activities["Soccer Club"]["participants"] = []
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]


def test_get_activities_returns_activity_data():
    # Arrange
    reset_activity_state()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Soccer Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant_to_activity():
    # Arrange
    reset_activity_state()
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Soccer Club/signup?email=newstudent@mergington.edu")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Soccer Club"
    assert email in activities["Soccer Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    # Arrange
    reset_activity_state()
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_raises_404_for_unknown_activity():
    # Arrange
    reset_activity_state()

    # Act
    response = client.post("/activities/Unknown Club/signup?email=test@example.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_from_activity():
    # Arrange
    reset_activity_state()
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_raises_404_for_missing_participant():
    # Arrange
    reset_activity_state()
    email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/Soccer Club/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"


def test_signup_updates_activity_state_immediately():
    # Arrange
    reset_activity_state()
    email = "instantupdate@mergington.edu"

    # Act
    response = client.post(f"/activities/Soccer Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()["Soccer Club"]["participants"]
