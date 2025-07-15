from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Literal, Annotated

class UserInput(BaseModel):
    age: Annotated[int,Field(...,gt=0, lt=100, description='Age of the User')]
    wegith: Annotated[int, Field(..., gt=0, description='Weight of the user in lbs')]
    height: Annotated[int, Field(..., gt=50, description='Height of the User in centimeters (cm)')]
    dietary_restrictions: Annotated[str, Field()]
    calories: Annotated[int, Field(...,)]




# user_preferences = {
#     "dietary_restrictions": ["vegetarian"],
#     "allergies": ["nuts"],
#     "calorie_target": 2500,
#     "protein_target": 120,
#     "weight_kg": 64 ,
#     "height_cm": 177,
#     "age": 20,
#     "comments":"I dont want fried food today. ALso today i am really craving for some good salad :) . also, i am indian vegeterian meaning that i dont eat eggs too. so no eggs please"
# }