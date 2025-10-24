import pytest
from pydantic import ValidationError
from backend.app.model.schema import UserInput


class TestUserInputModel:
    """Test suite for UserInput Pydantic model validation"""

    def test_valid_user_input(self):
        """Test that valid data passes validation"""
        valid_data = {
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
        user_input = UserInput(**valid_data)
        assert user_input.age == 25
        assert user_input.gender == "male"
        assert user_input.weight == 180
        assert user_input.calories == 2500
        assert "peanuts" in user_input.allergens

    def test_bmi_calculation(self):
        """Test that BMI computed field calculates correctly"""
        user_input = UserInput(
            age=30,
            gender="female",
            weight=150,
            height=165,
            activity_level="active",
            goal="lose_weight",
            diet="vegan",
            dietary_restrictions="none",
            calories=2000,
            protein=120,
            comments="",
            allergens=[],
            dislikes=[]
        )
        expected_bmi = 150 / (165 ** 2)
        assert abs(user_input.bmi - expected_bmi) < 0.0001

    def test_age_validation_zero(self):
        """Test that age validation rejects zero"""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(
                age=0,
                gender="male",
                weight=180,
                height=175,
                activity_level="moderate",
                goal="maintain",
                diet="balanced",
                dietary_restrictions="none",
                calories=2200,
                protein=140,
                comments="",
                allergens=[],
                dislikes=[]
            )
        assert "age" in str(exc_info.value)

    def test_age_validation_negative(self):
        """Test that age validation rejects negative values"""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(
                age=-5,
                gender="male",
                weight=180,
                height=175,
                activity_level="moderate",
                goal="maintain",
                diet="balanced",
                dietary_restrictions="none",
                calories=2200,
                protein=140,
                comments="",
                allergens=[],
                dislikes=[]
            )
        assert "age" in str(exc_info.value)

    def test_age_validation_too_high(self):
        """Test that age validation rejects values >= 100"""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(
                age=100,
                gender="male",
                weight=180,
                height=175,
                activity_level="moderate",
                goal="maintain",
                diet="balanced",
                dietary_restrictions="none",
                calories=2200,
                protein=140,
                comments="",
                allergens=[],
                dislikes=[]
            )
        assert "age" in str(exc_info.value)

    def test_weight_validation_zero(self):
        """Test that weight validation rejects zero"""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(
                age=25,
                gender="male",
                weight=0,
                height=175,
                activity_level="moderate",
                goal="maintain",
                diet="balanced",
                dietary_restrictions="none",
                calories=2200,
                protein=140,
                comments="",
                allergens=[],
                dislikes=[]
            )
        assert "weight" in str(exc_info.value)

    def test_weight_validation_negative(self):
        """Test that weight validation rejects negative values"""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(
                age=25,
                gender="male",
                weight=-150,
                height=175,
                activity_level="moderate",
                goal="maintain",
                diet="balanced",
                dietary_restrictions="none",
                calories=2200,
                protein=140,
                comments="",
                allergens=[],
                dislikes=[]
            )
        assert "weight" in str(exc_info.value)

    def test_height_validation_too_low(self):
        """Test that height validation rejects values <= 50"""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(
                age=25,
                gender="male",
                weight=180,
                height=50,
                activity_level="moderate",
                goal="maintain",
                diet="balanced",
                dietary_restrictions="none",
                calories=2200,
                protein=140,
                comments="",
                allergens=[],
                dislikes=[]
            )
        assert "height" in str(exc_info.value)

    def test_calories_validation_zero(self):
        """Test that calories validation rejects zero"""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(
                age=25,
                gender="male",
                weight=180,
                height=175,
                activity_level="moderate",
                goal="maintain",
                diet="balanced",
                dietary_restrictions="none",
                calories=0,
                protein=140,
                comments="",
                allergens=[],
                dislikes=[]
            )
        assert "calories" in str(exc_info.value)

    def test_protein_validation_zero(self):
        """Test that protein validation rejects zero"""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(
                age=25,
                gender="male",
                weight=180,
                height=175,
                activity_level="moderate",
                goal="maintain",
                diet="balanced",
                dietary_restrictions="none",
                calories=2200,
                protein=0,
                comments="",
                allergens=[],
                dislikes=[]
            )
        assert "protein" in str(exc_info.value)

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            UserInput(
                age=25,
                gender="male"
            )
        errors = exc_info.value.errors()
        required_fields = {"weight", "height", "activity_level", "goal",
                          "diet", "dietary_restrictions", "calories", "protein"}
        error_fields = {error['loc'][0] for error in errors}
        assert required_fields.issubset(error_fields)

    def test_wrong_type_validation(self):
        """Test that wrong data types raise ValidationError"""
        with pytest.raises(ValidationError):
            UserInput(
                age="twenty five",
                gender="male",
                weight=180,
                height=175,
                activity_level="moderate",
                goal="maintain",
                diet="balanced",
                dietary_restrictions="none",
                calories=2200,
                protein=140,
                comments="",
                allergens=[],
                dislikes=[]
            )

    def test_empty_allergens_list(self):
        """Test that empty allergens list is valid"""
        user_input = UserInput(
            age=25,
            gender="male",
            weight=180,
            height=175,
            activity_level="moderate",
            goal="maintain",
            diet="balanced",
            dietary_restrictions="none",
            calories=2200,
            protein=140,
            comments="",
            allergens=[],
            dislikes=[]
        )
        assert user_input.allergens == []

    def test_empty_dislikes_list(self):
        """Test that empty dislikes list is valid"""
        user_input = UserInput(
            age=25,
            gender="male",
            weight=180,
            height=175,
            activity_level="moderate",
            goal="maintain",
            diet="balanced",
            dietary_restrictions="none",
            calories=2200,
            protein=140,
            comments="",
            allergens=[],
            dislikes=[]
        )
        assert user_input.dislikes == []

    def test_empty_comments_string(self):
        """Test that empty comments string is valid"""
        user_input = UserInput(
            age=25,
            gender="male",
            weight=180,
            height=175,
            activity_level="moderate",
            goal="maintain",
            diet="balanced",
            dietary_restrictions="none",
            calories=2200,
            protein=140,
            comments="",
            allergens=[],
            dislikes=[]
        )
        assert user_input.comments == ""

    def test_multiple_allergens(self):
        """Test that multiple allergens are stored correctly"""
        allergens_list = ["peanuts", "tree nuts", "dairy", "eggs", "fish"]
        user_input = UserInput(
            age=25,
            gender="male",
            weight=180,
            height=175,
            activity_level="moderate",
            goal="maintain",
            diet="balanced",
            dietary_restrictions="none",
            calories=2200,
            protein=140,
            comments="",
            allergens=allergens_list,
            dislikes=[]
        )
        assert user_input.allergens == allergens_list

    def test_edge_case_valid_age(self):
        """Test edge case for valid age boundaries"""
        user_input = UserInput(
            age=99,
            gender="male",
            weight=180,
            height=175,
            activity_level="moderate",
            goal="maintain",
            diet="balanced",
            dietary_restrictions="none",
            calories=2200,
            protein=140,
            comments="",
            allergens=[],
            dislikes=[]
        )
        assert user_input.age == 99

    def test_edge_case_valid_height(self):
        """Test edge case for valid height boundaries"""
        user_input = UserInput(
            age=25,
            gender="male",
            weight=180,
            height=51,
            activity_level="moderate",
            goal="maintain",
            diet="balanced",
            dietary_restrictions="none",
            calories=2200,
            protein=140,
            comments="",
            allergens=[],
            dislikes=[]
        )
        assert user_input.height == 51
