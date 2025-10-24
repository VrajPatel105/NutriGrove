import pytest
import json
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
from backend.app.ai_food_recommendation import FoodRecommender


@pytest.fixture
def mock_env_variables(monkeypatch):
    """Mock environment variables"""
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key_12345")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test_supabase_key_12345")


@pytest.fixture
def mock_menu_data():
    """Mock menu data from database"""
    return [
        {
            "id": 1,
            "data": {
                "food_name": "Scrambled Eggs",
                "station_name": "Main Grill",
                "meal_type": "Breakfast",
                "nutrition": {
                    "calories": 70,
                    "protein_g": 6,
                    "carbs_g": 1,
                    "fat_g": 5,
                    "fiber_g": 0,
                    "sodium_mg": 60,
                    "ingredients": "Eggs, butter, salt"
                }
            }
        },
        {
            "id": 2,
            "data": {
                "food_name": "Grilled Chicken",
                "station_name": "Main Grill",
                "meal_type": "Lunch",
                "nutrition": {
                    "calories": 165,
                    "protein_g": 31,
                    "carbs_g": 0,
                    "fat_g": 3.6,
                    "fiber_g": 0,
                    "sodium_mg": 74,
                    "ingredients": "Chicken breast, olive oil, seasonings. Disclaimer: May contain allergens"
                }
            }
        }
    ]


@pytest.fixture
def user_preferences():
    """Sample user preferences"""
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
        "allergens": [],
        "dislikes": []
    }


@pytest.fixture
def mock_ai_response():
    """Mock AI response for meal schedule"""
    return {
        "breakfast": [
            {
                "name": "Scrambled Eggs",
                "station": "Main Grill",
                "recommended_portion": "3 eggs",
                "calories": 210,
                "protein_g": 18
            }
        ],
        "lunch": [],
        "dinner": [],
        "daily_totals": {
            "total_calories": 2500,
            "total_protein_g": 150
        },
        "meal_plan_analysis": {
            "target_achievement": "SUCCESS"
        }
    }


class TestFoodRecommenderInitialization:
    """Test suite for FoodRecommender initialization"""

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_initialization_success(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables):
        """Test successful initialization with valid credentials"""
        recommender = FoodRecommender()
        assert recommender is not None
        mock_genai_config.assert_called_once()
        mock_supabase.assert_called_once()

    @patch("backend.app.ai_food_recommendation.load_dotenv")
    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    def test_initialization_missing_gemini_key(self, mock_genai_config, mock_supabase, mock_load_dotenv, monkeypatch):
        """Test that missing GEMINI_API_KEY raises ValueError"""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_ANON_KEY", "test_key")
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        with pytest.raises(ValueError, match="Missing GEMINI_API_KEY"):
            FoodRecommender()

    @patch("backend.app.ai_food_recommendation.load_dotenv")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_initialization_missing_supabase_url(self, mock_model, mock_genai_config, mock_load_dotenv, monkeypatch):
        """Test that missing SUPABASE_URL raises ValueError"""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        monkeypatch.setenv("SUPABASE_ANON_KEY", "test_key")
        monkeypatch.delenv("SUPABASE_URL", raising=False)

        with pytest.raises(ValueError, match="Missing Supabase credentials"):
            FoodRecommender()

    @patch("backend.app.ai_food_recommendation.load_dotenv")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_initialization_missing_supabase_key(self, mock_model, mock_genai_config, mock_load_dotenv, monkeypatch):
        """Test that missing SUPABASE_ANON_KEY raises ValueError"""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)

        with pytest.raises(ValueError, match="Missing Supabase credentials"):
            FoodRecommender()


class TestGetAllMenuData:
    """Test suite for get_all_menu_data method"""

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_get_menu_data_success(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables, mock_menu_data):
        """Test successful menu data retrieval"""
        mock_supabase_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = mock_menu_data
        mock_supabase_instance.table.return_value.select.return_value.execute.return_value = mock_result
        mock_supabase.return_value = mock_supabase_instance

        recommender = FoodRecommender()
        menu_data = recommender.get_all_menu_data()

        assert len(menu_data) == 2
        assert menu_data[0]["data"]["food_name"] == "Scrambled Eggs"

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_get_menu_data_empty(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables):
        """Test menu data retrieval when database is empty"""
        mock_supabase_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase_instance.table.return_value.select.return_value.execute.return_value = mock_result
        mock_supabase.return_value = mock_supabase_instance

        recommender = FoodRecommender()
        menu_data = recommender.get_all_menu_data()

        assert menu_data == []

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_get_menu_data_error_handling(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables):
        """Test error handling when database query fails"""
        mock_supabase_instance = MagicMock()
        mock_supabase_instance.table.return_value.select.return_value.execute.side_effect = Exception("Database error")
        mock_supabase.return_value = mock_supabase_instance

        recommender = FoodRecommender()
        menu_data = recommender.get_all_menu_data()

        assert menu_data == []

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    @patch("backend.app.ai_food_recommendation.time.time")
    def test_get_menu_data_caching(self, mock_time, mock_model, mock_genai_config, mock_supabase, mock_env_variables, mock_menu_data):
        """Test that menu data is cached correctly"""
        mock_time.side_effect = [100, 100]
        mock_supabase_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = mock_menu_data
        mock_supabase_instance.table.return_value.select.return_value.execute.return_value = mock_result
        mock_supabase.return_value = mock_supabase_instance

        recommender = FoodRecommender()
        recommender._cache_duration = 3600
        recommender._menu_cache = None
        recommender._cache_timestamp = 0

        first_call = recommender.get_all_menu_data()

        assert recommender._menu_cache is not None
        assert len(first_call) == 2


class TestFormatMenuData:
    """Test suite for format_menu_data method"""

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_format_menu_data_structure(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables, mock_menu_data):
        """Test that menu data is formatted correctly"""
        recommender = FoodRecommender()
        formatted = recommender.format_menu_data(mock_menu_data)

        assert len(formatted) == 2
        assert "name" in formatted[0]
        assert "station" in formatted[0]
        assert "meal_type" in formatted[0]
        assert "nutrition" in formatted[0]

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_format_menu_data_disclaimer_removal(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables, mock_menu_data):
        """Test that disclaimer text is removed from ingredients"""
        recommender = FoodRecommender()
        formatted = recommender.format_menu_data(mock_menu_data)

        chicken_item = formatted[1]
        ingredients = chicken_item["nutrition"]["ingredients"]

        assert "Disclaimer:" not in ingredients
        assert "Chicken breast, olive oil, seasonings." in ingredients

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_format_menu_data_empty_list(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables):
        """Test formatting empty menu data"""
        recommender = FoodRecommender()
        formatted = recommender.format_menu_data([])
        assert formatted == []


class TestGetDailyMealSchedule:
    """Test suite for get_daily_meal_schedule method"""

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_meal_schedule_no_menu_data(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables, user_preferences):
        """Test that error is returned when no menu data is available"""
        mock_supabase_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = []
        mock_supabase_instance.table.return_value.select.return_value.execute.return_value = mock_result
        mock_supabase.return_value = mock_supabase_instance

        recommender = FoodRecommender()
        result = recommender.get_daily_meal_schedule(user_preferences)

        assert "error" in result
        assert result["error"] == "No menu data available"

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_meal_schedule_success(self, mock_model_class, mock_genai_config, mock_supabase, mock_env_variables, mock_menu_data, user_preferences, mock_ai_response):
        """Test successful meal schedule generation"""
        mock_supabase_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = mock_menu_data
        mock_supabase_instance.table.return_value.select.return_value.execute.return_value = mock_result
        mock_supabase.return_value = mock_supabase_instance

        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_ai_response)
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        with patch("builtins.open", mock_open()):
            with patch("backend.app.ai_food_recommendation.os.makedirs"):
                recommender = FoodRecommender()
                result = recommender.get_daily_meal_schedule(user_preferences)

        assert "breakfast" in result
        assert "daily_totals" in result
        assert "meal_plan_analysis" in result

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_meal_schedule_json_parse_error(self, mock_model_class, mock_genai_config, mock_supabase, mock_env_variables, mock_menu_data, user_preferences):
        """Test handling of invalid JSON response from AI"""
        mock_supabase_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = mock_menu_data
        mock_supabase_instance.table.return_value.select.return_value.execute.return_value = mock_result
        mock_supabase.return_value = mock_supabase_instance

        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Invalid JSON response"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        recommender = FoodRecommender()
        result = recommender.get_daily_meal_schedule(user_preferences)

        assert "error" in result
        assert "Failed to parse AI response" in result["error"]

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_meal_schedule_ai_exception(self, mock_model_class, mock_genai_config, mock_supabase, mock_env_variables, mock_menu_data, user_preferences):
        """Test handling of AI service exception"""
        mock_supabase_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = mock_menu_data
        mock_supabase_instance.table.return_value.select.return_value.execute.return_value = mock_result
        mock_supabase.return_value = mock_supabase_instance

        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = Exception("AI API Error")
        mock_model_class.return_value = mock_model_instance

        recommender = FoodRecommender()
        result = recommender.get_daily_meal_schedule(user_preferences)

        assert "error" in result
        assert "AI service error" in result["error"]

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_meal_schedule_with_json_markdown(self, mock_model_class, mock_genai_config, mock_supabase, mock_env_variables, mock_menu_data, user_preferences, mock_ai_response):
        """Test handling of JSON response wrapped in markdown code blocks"""
        mock_supabase_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.data = mock_menu_data
        mock_supabase_instance.table.return_value.select.return_value.execute.return_value = mock_result
        mock_supabase.return_value = mock_supabase_instance

        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = f"```json\n{json.dumps(mock_ai_response)}\n```"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        with patch("builtins.open", mock_open()):
            with patch("backend.app.ai_food_recommendation.os.makedirs"):
                recommender = FoodRecommender()
                result = recommender.get_daily_meal_schedule(user_preferences)

        assert "breakfast" in result
        assert "error" not in result


class TestSaveResponseToFile:
    """Test suite for save_response_to_file method"""

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_save_response_creates_directory(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables, mock_ai_response, user_preferences):
        """Test that save_response_to_file creates directory"""
        with patch("backend.app.ai_food_recommendation.os.makedirs") as mock_makedirs:
            with patch("builtins.open", mock_open()):
                recommender = FoodRecommender()
                recommender.save_response_to_file(mock_ai_response, user_preferences)
                mock_makedirs.assert_called_once_with('backend/app/data/ai_response', exist_ok=True)

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_save_response_writes_file(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables, mock_ai_response, user_preferences):
        """Test that save_response_to_file writes to correct file"""
        mock_file = mock_open()
        with patch("backend.app.ai_food_recommendation.os.makedirs"):
            with patch("builtins.open", mock_file):
                recommender = FoodRecommender()
                recommender.save_response_to_file(mock_ai_response, user_preferences)

                calls = [call for call in mock_file.call_args_list if len(call[0]) > 0]
                target_call = [call for call in calls if 'daily_meal_schedule.json' in str(call)]
                assert len(target_call) > 0

    @patch("backend.app.ai_food_recommendation.create_client")
    @patch("backend.app.ai_food_recommendation.genai.configure")
    @patch("backend.app.ai_food_recommendation.genai.GenerativeModel")
    def test_save_response_error_handling(self, mock_model, mock_genai_config, mock_supabase, mock_env_variables, mock_ai_response, user_preferences):
        """Test error handling in save_response_to_file"""
        with patch("backend.app.ai_food_recommendation.os.makedirs", side_effect=Exception("Write error")):
            recommender = FoodRecommender()
            recommender.save_response_to_file(mock_ai_response, user_preferences)
