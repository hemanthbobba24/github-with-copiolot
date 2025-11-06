from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.app import app

client = TestClient(app)

def test_read_root():
    """Test that root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 308)  # Both are valid redirect codes
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Test structure of activities
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    
    # Test activity structure
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    test_email = "test_student@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={test_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {test_email} for Chess Club"
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert test_email in activities["Chess Club"]["participants"]
    
    # Test duplicate signup
    response = client.post(f"/activities/Chess Club/signup?email={test_email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/Nonexistent Club/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First sign up a test participant
    test_email = "test_unregister@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={test_email}")
    
    # Then unregister them
    response = client.delete(f"/activities/Chess Club/unregister?email={test_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {test_email} from Chess Club"
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert test_email not in activities["Chess Club"]["participants"]
    
    # Test unregistering when not signed up
    response = client.delete(f"/activities/Chess Club/unregister?email={test_email}")
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"]

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/Nonexistent Club/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]