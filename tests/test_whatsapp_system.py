"""
Comprehensive Tests for WhatsApp Nutrition Coach System
"""

import pytest
import asyncio
from datetime import datetime, date, timedelta
from backend.app.services.menu_service import MenuService
from backend.app.services.food_logger import FoodLogger
from backend.app.services.nutrition_estimator import NutritionEstimator
from backend.app.services.conversational_agent import ConversationalAgent
from backend.app.services.analytics_service import AnalyticsService
from backend.app.utils.date_parser import DateParser
from backend.app.utils.food_parser import FoodParser
from backend.app.utils.portion_calculator import PortionCalculator


class TestDateParser:
    """Test date parsing utility"""

    def test_parse_today(self):
        """Test parsing 'today'"""
        result = DateParser.parse_date("today")
        assert result.date() == datetime.now().date()

    def test_parse_tomorrow(self):
        """Test parsing 'tomorrow'"""
        result = DateParser.parse_date("tomorrow")
        tomorrow = datetime.now().date() + timedelta(days=1)
        assert result.date() == tomorrow

    def test_get_meal_time_context(self):
        """Test meal time context detection"""
        context = DateParser.get_meal_time_context()
        assert context in ['breakfast', 'lunch', 'dinner', 'snack']

    def test_is_weekend(self):
        """Test weekend detection"""
        result = DateParser.is_weekend()
        assert isinstance(result, bool)


class TestFoodParser:
    """Test food parsing utility"""

    def test_extract_foods_simple(self):
        """Test extracting foods from simple text"""
        result = FoodParser.extract_foods("ate 3 eggs and toast")
        assert len(result) == 2
        assert result[0]['food'] == 'eggs'
        assert result[0]['portion'] == '3 eggs'
        assert result[0]['quantity'] == 3.0

    def test_extract_foods_complex(self):
        """Test extracting multiple foods"""
        result = FoodParser.extract_foods("had 2 eggs, toast, and some orange juice")
        assert len(result) >= 2  # At least eggs and toast

    def test_detect_meal_type(self):
        """Test meal type detection"""
        result = FoodParser.detect_meal_type("ate breakfast", hour=8)
        assert result == 'breakfast'

        result = FoodParser.detect_meal_type("had lunch", hour=12)
        assert result == 'lunch'

    def test_is_logging_message(self):
        """Test logging vs question detection"""
        assert FoodParser.is_logging_message("ate 3 eggs") == True
        assert FoodParser.is_logging_message("what should I eat?") == False


class TestPortionCalculator:
    """Test portion calculator utility"""

    def test_extract_quantity(self):
        """Test quantity extraction"""
        assert PortionCalculator.extract_quantity("3 eggs") == 3.0
        assert PortionCalculator.extract_quantity("half cup") == 0.5
        assert PortionCalculator.extract_quantity("a banana") == 1.0

    def test_scale_nutrition(self):
        """Test nutrition scaling"""
        base = {'calories': 70, 'protein_g': 6, 'fat_g': 5}
        result = PortionCalculator.scale_nutrition(base, "1 egg", "3 eggs")

        assert result['calories'] == 210
        assert result['protein_g'] == 18
        assert result['fat_g'] == 15

    def test_calculate_portion_math(self):
        """Test portion calculation explanation"""
        result = PortionCalculator.calculate_portion_math("1 egg", "3 eggs", 70, 6)
        assert "210 cal" in result
        assert "18g protein" in result.lower() or "18.0g protein" in result.lower()


@pytest.mark.asyncio
class TestMenuService:
    """Test menu service"""

    async def test_search_menu_minimal(self):
        """Test minimal menu search"""
        service = MenuService()
        result = await service.search_menu_minimal(
            meal_type="lunch",
            min_protein=30,
            limit=5
        )

        # Should return list of foods
        assert isinstance(result, list)
        # Should be filtered
        assert len(result) <= 5

        if result:
            # Check structure
            assert 'name' in result[0]
            assert 'calories' in result[0]
            assert 'protein_g' in result[0]

    async def test_get_food_details(self):
        """Test getting detailed food info"""
        service = MenuService()
        result = await service.get_food_details("chicken")

        # Should return dict or None
        assert result is None or isinstance(result, dict)

        if result:
            assert 'name' in result
            assert 'calories' in result


@pytest.mark.asyncio
class TestFoodLogger:
    """Test food logging service"""

    async def test_log_food_item(self):
        """Test logging a food item"""
        logger = FoodLogger()

        result = await logger.log_food_item(
            phone_number="+1234567890",
            food_name="eggs",
            portion="3 eggs",
            meal_type="breakfast",
            calories=210,
            protein_g=18,
            was_planned=True
        )

        # Should return logged entry
        assert isinstance(result, dict)
        assert result['food_name'] == 'eggs'
        assert result['calories'] == 210

    async def test_get_daily_progress(self):
        """Test getting daily progress"""
        logger = FoodLogger()

        result = await logger.get_daily_progress(
            phone_number="+1234567890",
            target_date=date.today().isoformat()
        )

        # Should return progress dict
        assert isinstance(result, dict)
        assert 'actual' in result
        assert 'target' in result
        assert 'remaining' in result


@pytest.mark.asyncio
class TestNutritionEstimator:
    """Test nutrition estimation service"""

    async def test_estimate_common_food(self):
        """Test estimating common food"""
        estimator = NutritionEstimator()

        # Test built-in knowledge
        result = estimator.estimate_from_common_knowledge("chips")

        if result:
            assert 'calories' in result
            assert 'protein_g' in result
            assert result['calories'] > 0


@pytest.mark.asyncio
class TestAnalyticsService:
    """Test analytics service"""

    async def test_generate_weekly_analysis(self):
        """Test weekly analysis generation"""
        analytics = AnalyticsService()

        # Use a phone number that has data
        result = await analytics.generate_weekly_analysis(
            phone_number="+1234567890"
        )

        # Should return analysis or error
        assert isinstance(result, dict)
        # Either has summary or error
        assert 'summary' in result or 'error' in result

    async def test_get_daily_streak(self):
        """Test daily streak calculation"""
        analytics = AnalyticsService()

        result = await analytics.get_daily_streak(
            phone_number="+1234567890"
        )

        # Should return number
        assert isinstance(result, int)
        assert result >= 0


class TestPydanticModels:
    """Test Pydantic model validation"""

    def test_user_profile_model(self):
        """Test UserProfile model"""
        from backend.app.model.schema import UserProfile

        profile = UserProfile(
            phone_number="+1234567890",
            age=25,
            weight=170,
            calories_target=2800
        )

        assert profile.phone_number == "+1234567890"
        assert profile.age == 25

    def test_food_log_entry_model(self):
        """Test FoodLogEntry model"""
        from backend.app.model.schema import FoodLogEntry

        log = FoodLogEntry(
            phone_number="+1234567890",
            date=date.today(),
            meal_type="breakfast",
            food_name="eggs",
            portion="3 eggs",
            calories=210
        )

        assert log.food_name == "eggs"
        assert log.calories == 210


# Integration Tests
@pytest.mark.asyncio
class TestIntegration:
    """Integration tests for full workflows"""

    async def test_food_logging_workflow(self):
        """Test complete food logging workflow"""
        logger = FoodLogger()

        # 1. Log a food
        log_result = await logger.log_food_item(
            phone_number="+1999999999",  # Test number
            food_name="test_food",
            portion="1 serving",
            meal_type="lunch",
            calories=500,
            protein_g=30,
            was_planned=False
        )

        assert log_result is not None

        # 2. Get progress
        progress = await logger.get_daily_progress(
            phone_number="+1999999999",
            target_date=date.today().isoformat()
        )

        assert progress['actual']['calories'] >= 500

    async def test_menu_to_log_workflow(self):
        """Test searching menu and logging food"""
        menu_service = MenuService()
        logger = FoodLogger()

        # 1. Search menu
        foods = await menu_service.search_menu_minimal(
            meal_type="lunch",
            limit=1
        )

        if foods:
            food = foods[0]

            # 2. Log the found food
            log_result = await logger.log_food_item(
                phone_number="+1999999999",
                food_name=food['name'],
                portion="1 serving",
                meal_type="lunch",
                calories=food['calories'],
                protein_g=food['protein_g']
            )

            assert log_result is not None


# Performance Tests
@pytest.mark.asyncio
class TestPerformance:
    """Test performance and token optimization"""

    async def test_menu_search_token_efficiency(self):
        """Test that menu search returns minimal data"""
        service = MenuService()

        result = await service.search_menu_minimal(
            meal_type="lunch",
            limit=10
        )

        # Should return max 10 items
        assert len(result) <= 10

        if result:
            # Each item should only have essential fields
            item = result[0]
            essential_fields = ['name', 'calories', 'protein_g', 'carbs_g', 'fat_g']

            for field in essential_fields:
                assert field in item

            # Should NOT have micronutrients (that would be in full details)
            assert 'vitamin_a_re' not in item
            assert 'calcium_mg' not in item


def test_environment_variables():
    """Test that required environment variables are set"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'ANTHROPIC_API_KEY'
    ]

    for var in required_vars:
        assert os.getenv(var) is not None, f"{var} not set in environment"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
