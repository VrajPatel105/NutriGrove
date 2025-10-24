import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment before each test"""
    yield


@pytest.fixture
def sample_valid_user_input():
    """Reusable valid user input fixture"""
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
