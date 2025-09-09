from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Literal, Annotated

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
    

""" Additional api parameters added (on date : 09/09/2025) ~ Vraj :) :   Essential Parameters (definitely add these):
  - gender (male/female)
  - activity_level (active/sedentary/moderate)
  - goal (build_muscle/lose_weight/maintain)
  - diet (Keto/Paleo/Vegan/etc.)
  - allergens (array like [Eggs, Fish, Shellfish])
  - dislikes (array of disliked foods)"""