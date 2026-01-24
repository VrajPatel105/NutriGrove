from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Literal, Annotated, Optional, List, Dict
from datetime import datetime, date

class UserInput(BaseModel):
    age: Annotated[int,Field(...,gt=0, lt=100, description='Age of the User')]
    gender: Annotated[str, Field(..., description='Gender of the user')]
    weight: Annotated[int, Field(..., gt=0, description='Weight of the user in lbs')]
    height: Annotated[int, Field(..., gt=50, description='Height of the User in centimeters (cm)')]
    activity_level: Annotated[str, Field(...,description='Activity level of the user. For ex: active/sedentary/moderate')]
    goal: Annotated[str, Field(...,description='Goal of the user. Example: build_muscle/lose_weight/maintain')]
    diet: Annotated[str, Field(...,description='Diet preferred by the user. Example: keto, Paleo, vegan, etc')]
    dietary_restrictions: Annotated[str, Field(...,description='All the restrictions from the user')]
    calories: Annotated[int, Field(...,gt=0, description="Calories a user is expecting to consume in grams")]
    protein: Annotated[int, Field(...,gt=0, description="Protein a user is expecting to consume in grams")]
    comments: Annotated[str,Field(description="Any additional comments from the user")]
    allergens: Annotated[list,Field(description='Allergens selected by the user')]
    dislikes: Annotated[list, Field(description='Disliked food by the user. For ex: garlic, mushrooms etc')]


    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight/(self.height**2)


# ============================================
# NEW MODELS FOR WHATSAPP NUTRITION COACH
# ============================================

class UserProfile(BaseModel):
    """User profile for WhatsApp nutrition coach"""
    phone_number: str
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[int] = None  # lbs
    height: Optional[int] = None  # cm
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    diet: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    calories_target: Optional[int] = None
    protein_target: Optional[int] = None
    carbs_target: Optional[int] = None
    fat_target: Optional[int] = None
    allergens: Optional[List[str]] = []
    dislikes: Optional[List[str]] = []


class FoodLogEntry(BaseModel):
    """Single food log entry"""
    phone_number: str
    date: date
    meal_type: str  # breakfast/lunch/dinner/snack
    food_name: str
    portion: str
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    sugar_g: Optional[float] = None
    was_planned: bool = False
    is_external: bool = False
    notes: Optional[str] = None


class DailySummary(BaseModel):
    """Daily nutrition summary"""
    phone_number: str
    date: date
    planned_calories: Optional[int] = None
    actual_calories: Optional[int] = None
    planned_protein: Optional[int] = None
    actual_protein: Optional[float] = None
    actual_carbs: Optional[float] = None
    actual_fat: Optional[float] = None
    actual_fiber: Optional[float] = None
    adherence_score: Optional[float] = None
    meals_logged: int = 0
    notes: Optional[str] = None
    synced_to_sheets: bool = False


class WhatsAppMessage(BaseModel):
    """Incoming WhatsApp message"""
    From: str  # Phone number with "whatsapp:" prefix
    Body: str  # Message text
    MessageSid: Optional[str] = None


class ConversationContext(BaseModel):
    """Conversation state and context"""
    phone_number: str
    current_phase: Optional[str] = None
    context_data: Optional[Dict] = {}
    last_interaction: Optional[datetime] = None


class MenuSearchParams(BaseModel):
    """Parameters for menu search"""
    meal_type: Optional[str] = None
    min_protein: Optional[int] = None
    max_calories: Optional[int] = None
    exclude_allergens: Optional[List[str]] = []
    station: Optional[str] = None
    limit: int = 10


class FoodItem(BaseModel):
    """Food item from menu (minimal data)"""
    name: str
    station: Optional[str] = None
    meal_type: Optional[str] = None
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    allergens: Optional[List[str]] = []


class DailyProgress(BaseModel):
    """Daily nutrition progress"""
    actual: Dict[str, float]
    target: Dict[str, int]
    remaining: Dict[str, float]
    meals_logged: int
    adherence: Optional[float] = None
    

""" Additional api parameters added (on date : 09/09/2025) ~ Vraj :) :   Essential Parameters (definitely add these):
  - gender (male/female)
  - activity_level (active/sedentary/moderate)
  - goal (build_muscle/lose_weight/maintain)
  - diet (Keto/Paleo/Vegan/etc.)
  - allergens (array like [Eggs, Fish, Shellfish])
  - dislikes (array of disliked foods)"""