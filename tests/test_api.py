import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from backend.app.api import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def valid_user_data():
    """Valid user input data for testing"""
    return {
        "age": 25,
        "gender": "male",
        "weight": 180,
        "height": 175,
        "activity_level": "moderate",
        "goal": "build_muscle",
        "diet": "keto",
        "dietary_restrictions": "none",
        "calories": 2500,
        "protein": 150,
        "comments": "I prefer high protein meals",
        "allergens": ["peanuts", "shellfish"],
        "dislikes": ["mushrooms", "olives"]
    }


@pytest.fixture
def mock_meal_schedule():
    """Mock meal schedule response"""
    return {
        "breakfast": [
            {
                "name": "Scrambled Eggs",
                "station": "Main Grill",
                "recommended_portion": "3 eggs",
                "serving_size": "Menu: 1 egg, Recommended: 3 eggs",
                "calories": 210,
                "protein_g": 18,
                "carbs_g": 2,
                "fat_g": 15,
                "fiber_g": 0,
                "sodium_mg": 180,
                "allergens": ["eggs"],
                "ingredients": "Eggs, butter, salt",
                "per_menu_serving_nutrition": {
                    "serving_size": "1 egg",
                    "calories": 70,
                    "protein_g": 6
                },
                "full_nutrition": {
                    "calories": 210,
                    "protein_g": 18
                },
                "portion_math": "3 servings x 70 cal = 210 cal",
                "reason_selected": "High protein breakfast option"
            }
        ],
        "lunch": [],
        "dinner": [],
        "daily_totals": {
            "total_calories": 2500,
            "total_protein_g": 150,
            "calorie_target": 2500,
            "protein_target": 150
        },
        "meal_plan_analysis": {
            "calorie_goal_status": "Met",
            "protein_goal_status": "Met",
            "target_achievement": "SUCCESS"
        }
    }


class TestRootEndpoint:
    """Test suite for root endpoint"""

    def test_root_endpoint_success(self, client):
        """Test that root endpoint returns 200 and correct message"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, This is API system for NutriGrove"}

    def test_root_endpoint_response_format(self, client):
        """Test that root endpoint returns JSON with expected fields"""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)


class TestRecommendationsEndpoint:
    """Test suite for /recommendations endpoint"""

    def test_recommendations_success(self, client, valid_user_data, mock_meal_schedule):
        """Test successful request with valid data returns 200"""
        with patch("backend.app.api.recommender.get_daily_meal_schedule") as mock_schedule:
            mock_schedule.return_value = mock_meal_schedule
            response = client.post("/recommendations", json=valid_user_data)
            assert response.status_code == 200

    def test_recommendations_response_structure(self, client, valid_user_data, mock_meal_schedule):
        """Test that response contains expected fields"""
        with patch("backend.app.api.recommender.get_daily_meal_schedule") as mock_schedule:
            mock_schedule.return_value = mock_meal_schedule
            response = client.post("/recommendations", json=valid_user_data)
            data = response.json()

            assert "breakfast" in data
            assert "lunch" in data
            assert "dinner" in data
            assert "daily_totals" in data
            assert "meal_plan_analysis" in data

    def test_recommendations_invalid_age_negative(self, client, valid_user_data):
        """Test that negative age returns 422 validation error"""
        invalid_data = valid_user_data.copy()
        invalid_data["age"] = -5
        response = client.post("/recommendations", json=invalid_data)
        assert response.status_code == 422

    def test_recommendations_invalid_age_zero(self, client, valid_user_data):
        """Test that age zero returns 422 validation error"""
        invalid_data = valid_user_data.copy()
        invalid_data["age"] = 0
        response = client.post("/recommendations", json=invalid_data)
        assert response.status_code == 422

    def test_recommendations_invalid_age_too_high(self, client, valid_user_data):
        """Test that age >= 100 returns 422 validation error"""
        invalid_data = valid_user_data.copy()
        invalid_data["age"] = 100
        response = client.post("/recommendations", json=invalid_data)
        assert response.status_code == 422

    def test_recommendations_invalid_weight_zero(self, client, valid_user_data):
        """Test that weight zero returns 422 validation error"""
        invalid_data = valid_user_data.copy()
        invalid_data["weight"] = 0
        response = client.post("/recommendations", json=invalid_data)
        assert response.status_code == 422

    def test_recommendations_invalid_height_too_low(self, client, valid_user_data):
        """Test that height <= 50 returns 422 validation error"""
        invalid_data = valid_user_data.copy()
        invalid_data["height"] = 50
        response = client.post("/recommendations", json=invalid_data)
        assert response.status_code == 422

    def test_recommendations_invalid_calories_zero(self, client, valid_user_data):
        """Test that calories zero returns 422 validation error"""
        invalid_data = valid_user_data.copy()
        invalid_data["calories"] = 0
        response = client.post("/recommendations", json=invalid_data)
        assert response.status_code == 422

    def test_recommendations_invalid_protein_zero(self, client, valid_user_data):
        """Test that protein zero returns 422 validation error"""
        invalid_data = valid_user_data.copy()
        invalid_data["protein"] = 0
        response = client.post("/recommendations", json=invalid_data)
        assert response.status_code == 422

    def test_recommendations_missing_required_field(self, client):
        """Test that missing required fields return 422 validation error"""
        incomplete_data = {
            "age": 25,
            "gender": "male",
            "weight": 180
        }
        response = client.post("/recommendations", json=incomplete_data)
        assert response.status_code == 422

    def test_recommendations_wrong_data_type(self, client, valid_user_data):
        """Test that wrong data type returns 422 validation error"""
        invalid_data = valid_user_data.copy()
        invalid_data["age"] = "twenty five"
        response = client.post("/recommendations", json=invalid_data)
        assert response.status_code == 422

    def test_recommendations_empty_allergens(self, client, valid_user_data, mock_meal_schedule):
        """Test that empty allergens list is accepted"""
        with patch("backend.app.api.recommender.get_daily_meal_schedule") as mock_schedule:
            mock_schedule.return_value = mock_meal_schedule
            test_data = valid_user_data.copy()
            test_data["allergens"] = []
            response = client.post("/recommendations", json=test_data)
            assert response.status_code == 200

    def test_recommendations_empty_dislikes(self, client, valid_user_data, mock_meal_schedule):
        """Test that empty dislikes list is accepted"""
        with patch("backend.app.api.recommender.get_daily_meal_schedule") as mock_schedule:
            mock_schedule.return_value = mock_meal_schedule
            test_data = valid_user_data.copy()
            test_data["dislikes"] = []
            response = client.post("/recommendations", json=test_data)
            assert response.status_code == 200

    def test_recommendations_empty_comments(self, client, valid_user_data, mock_meal_schedule):
        """Test that empty comments string is accepted"""
        with patch("backend.app.api.recommender.get_daily_meal_schedule") as mock_schedule:
            mock_schedule.return_value = mock_meal_schedule
            test_data = valid_user_data.copy()
            test_data["comments"] = ""
            response = client.post("/recommendations", json=test_data)
            assert response.status_code == 200

    def test_recommendations_edge_case_high_calories(self, client, valid_user_data, mock_meal_schedule):
        """Test that high calorie values are accepted"""
        with patch("backend.app.api.recommender.get_daily_meal_schedule") as mock_schedule:
            mock_schedule.return_value = mock_meal_schedule
            test_data = valid_user_data.copy()
            test_data["calories"] = 5000
            response = client.post("/recommendations", json=test_data)
            assert response.status_code == 200

    def test_recommendations_edge_case_high_protein(self, client, valid_user_data, mock_meal_schedule):
        """Test that high protein values are accepted"""
        with patch("backend.app.api.recommender.get_daily_meal_schedule") as mock_schedule:
            mock_schedule.return_value = mock_meal_schedule
            test_data = valid_user_data.copy()
            test_data["protein"] = 300
            response = client.post("/recommendations", json=test_data)
            assert response.status_code == 200

    def test_recommendations_calls_recommender(self, client, valid_user_data, mock_meal_schedule):
        """Test that endpoint calls FoodRecommender.get_daily_meal_schedule"""
        with patch("backend.app.api.recommender.get_daily_meal_schedule") as mock_schedule:
            mock_schedule.return_value = mock_meal_schedule
            client.post("/recommendations", json=valid_user_data)
            assert mock_schedule.called
            call_args = mock_schedule.call_args[0][0]
            assert call_args["age"] == 25
            assert call_args["calories"] == 2500


class TestMenuEndpoint:
    """Test suite for /menu endpoint"""

    def test_menu_endpoint_success(self, client):
        """Test that menu endpoint returns 200"""
        with patch("backend.app.api.recommender.get_all_menu_data") as mock_menu:
            mock_menu.return_value = [
                {
                    "id": 1,
                    "data": {
                        "food_name": "Scrambled Eggs",
                        "station_name": "Main Grill",
                        "meal_type": "Breakfast",
                        "nutrition": {
                            "calories": 70,
                            "protein_g": 6
                        }
                    }
                }
            ]
            response = client.get("/menu")
            assert response.status_code == 200

    def test_menu_endpoint_returns_list(self, client):
        """Test that menu endpoint returns a list"""
        with patch("backend.app.api.recommender.get_all_menu_data") as mock_menu:
            mock_menu.return_value = [{"id": 1}, {"id": 2}]
            response = client.get("/menu")
            data = response.json()
            assert isinstance(data, list)

    def test_menu_endpoint_empty_list(self, client):
        """Test that menu endpoint handles empty menu data"""
        with patch("backend.app.api.recommender.get_all_menu_data") as mock_menu:
            mock_menu.return_value = []
            response = client.get("/menu")
            assert response.status_code == 200
            assert response.json() == []

    def test_menu_endpoint_calls_recommender(self, client):
        """Test that endpoint calls FoodRecommender.get_all_menu_data"""
        with patch("backend.app.api.recommender.get_all_menu_data") as mock_menu:
            mock_menu.return_value = []
            client.get("/menu")
            assert mock_menu.called


class TestErrorHandling:
    """Test suite for error handling scenarios"""

    def test_recommendations_with_null_values(self, client, valid_user_data):
        """Test that null values in optional fields return error"""
        invalid_data = valid_user_data.copy()
        invalid_data["comments"] = None
        response = client.post("/recommendations", json=invalid_data)
        assert response.status_code == 422

    def test_recommendations_with_extra_fields(self, client, valid_user_data, mock_meal_schedule):
        """Test that extra fields are ignored"""
        with patch("backend.app.api.recommender.get_daily_meal_schedule") as mock_schedule:
            mock_schedule.return_value = mock_meal_schedule
            test_data = valid_user_data.copy()
            test_data["extra_field"] = "should be ignored"
            response = client.post("/recommendations", json=test_data)
            assert response.status_code == 200

    def test_invalid_http_method_on_recommendations(self, client):
        """Test that GET on /recommendations returns 405"""
        response = client.get("/recommendations")
        assert response.status_code == 405

    def test_invalid_http_method_on_root(self, client):
        """Test that POST on root returns 405"""
        response = client.post("/")
        assert response.status_code == 405

    def test_invalid_http_method_on_menu(self, client):
        """Test that POST on /menu returns 405"""
        response = client.post("/menu")
        assert response.status_code == 405
