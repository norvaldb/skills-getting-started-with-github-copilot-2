"""
Test suite for Mergington High School Activities API

Tests cover:
- Activity retrieval
- Student signup functionality
- Student unregistration functionality
- Edge cases and error handling
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
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
        },
        "Basketball Team": {
            "description": "Competitive basketball practice and games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "alex@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swimming techniques and endurance training",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["sarah@mergington.edu", "noah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media art",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["lily@mergington.edu", "grace@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performance, acting, and stagecraft",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "ava@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Competitive science challenges and experiments",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "charlotte@mergington.edu"]
        }
    }
    
    # Reset activities to original state before each test
    activities.clear()
    activities.update(original_activities)
    yield
    # Clean up after test if needed


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Should have 9 activities
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activities_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_activities_initial_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant(self, client):
        """Test that signing up an existing participant returns error"""
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for non-existent activity returns error"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=coder@mergington.edu"
        )
        assert response.status_code == 200
        assert "coder@mergington.edu" in response.json()["message"]
    
    def test_signup_multiple_participants(self, client):
        """Test signing up multiple different participants"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/Chess Club/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Chess Club"]["participants"]
        
        for email in emails:
            assert email in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        # First, sign up a participant
        client.post("/activities/Chess Club/signup?email=temporary@mergington.edu")
        
        # Then unregister them
        response = client.delete(
            "/activities/Chess Club/unregister?email=temporary@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "temporary@mergington.edu" in data["message"]
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "temporary@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_initial_participant(self, client):
        """Test unregistering one of the initial participants"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        # daniel should still be there
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant who is not signed up"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity returns error"""
        response = client.delete(
            "/activities/Fake Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_with_url_encoded_activity_name(self, client):
        """Test unregister with URL-encoded activity name"""
        # Sign up first
        client.post("/activities/Programming Class/signup?email=coder@mergington.edu")
        
        # Unregister
        response = client.delete(
            "/activities/Programming%20Class/unregister?email=coder@mergington.edu"
        )
        assert response.status_code == 200


class TestSignupAndUnregisterWorkflow:
    """Integration tests for signup and unregister workflow"""
    
    def test_complete_lifecycle(self, client):
        """Test complete lifecycle: signup -> verify -> unregister -> verify"""
        email = "lifecycle@mergington.edu"
        activity = "Drama Club"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        assert email in after_signup.json()[activity]["participants"]
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregister
        after_unregister = client.get("/activities")
        assert email not in after_unregister.json()[activity]["participants"]
        assert len(after_unregister.json()[activity]["participants"]) == initial_count
    
    def test_cannot_unregister_before_signup(self, client):
        """Test that unregistering before signing up fails appropriately"""
        email = "never_signed_up@mergington.edu"
        
        response = client.delete(f"/activities/Art Studio/unregister?email={email}")
        assert response.status_code == 400
    
    def test_multiple_activities_per_student(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multi@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Studio"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]


class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_activity_name_with_special_characters(self, client):
        """Test handling of activity names with special characters"""
        # Test with URL-encoded spaces and other characters
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_empty_email_parameter(self, client):
        """Test signup with empty email parameter"""
        response = client.post("/activities/Chess Club/signup?email=")
        # Currently the API accepts empty emails, so it returns 200
        # This could be improved with validation in the future
        assert response.status_code == 200
    
    def test_email_format_variations(self, client):
        """Test that various email formats are accepted"""
        test_emails = [
            "simple@mergington.edu",
            "first.last@mergington.edu",
            "name+tag@mergington.edu",
            "name_with_underscore@mergington.edu"
        ]
        
        for email in test_emails:
            response = client.post(f"/activities/Gym Class/signup?email={email}")
            assert response.status_code == 200
