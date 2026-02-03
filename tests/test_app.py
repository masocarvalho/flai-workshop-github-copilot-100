"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Save original state
    original_activities = {
        "Soccer Team": {
            "description": "Join the varsity soccer team and compete against other schools",
            "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swim training and competitions for all skill levels",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 30,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "charlotte@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "amelia@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and conduct experiments",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["benjamin@mergington.edu", "harper@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "Soccer Team" in data
        assert "Swimming Club" in data
        assert "Drama Club" in data
        assert len(data) == 9
    
    def test_activities_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Soccer Team structure
        soccer = data["Soccer Team"]
        assert "description" in soccer
        assert "schedule" in soccer
        assert "max_participants" in soccer
        assert "participants" in soccer
        assert isinstance(soccer["participants"], list)


class TestSignupForActivity:
    """Tests for signing up for activities"""
    
    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Signed up newstudent@mergington.edu for Soccer Team"
        }
        
        # Verify student was added
        activities_response = client.get("/activities")
        soccer_participants = activities_response.json()["Soccer Team"]["participants"]
        assert "newstudent@mergington.edu" in soccer_participants
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_duplicate_signup(self, client):
        """Test that duplicate signups are prevented"""
        email = "lucas@mergington.edu"  # Already in Soccer Team
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for Soccer Team
        response1 = client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Swimming Club
        response2 = client.post(
            "/activities/Swimming Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Soccer Team"]["participants"]
        assert email in data["Swimming Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for unregistering from activities"""
    
    def test_successful_unregister(self, client):
        """Test successful unregistration from an activity"""
        email = "lucas@mergington.edu"  # Already in Soccer Team
        
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Unregistered lucas@mergington.edu from Soccer Team"
        }
        
        # Verify student was removed
        activities_response = client.get("/activities")
        soccer_participants = activities_response.json()["Soccer Team"]["participants"]
        assert email not in soccer_participants
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_not_signed_up(self, client):
        """Test unregister when student is not signed up"""
        email = "notsignedup@mergington.edu"
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": email}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"
    
    def test_signup_and_unregister_flow(self, client):
        """Test complete signup and unregister flow"""
        email = "testflow@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Chess Club"]["participants"]


class TestEdgeCases:
    """Tests for edge cases and special scenarios"""
    
    def test_activity_names_with_spaces(self, client):
        """Test that activity names with spaces are handled correctly"""
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": "programmer@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_email_format_handling(self, client):
        """Test that various email formats are handled"""
        # The API doesn't validate email format, just stores it
        response = client.post(
            "/activities/Art Studio/signup",
            params={"email": "test.user+tag@mergington.edu"}
        )
        assert response.status_code == 200
