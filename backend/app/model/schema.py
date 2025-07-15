from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Literal, Annotated

class UserInput(BaseModel):
    age: Annotated[int,Field(...,gt=0, lt=100, description='Age of the User')]
    wegith: Annotated[int, Field(..., gt=0, description='Weight of the user in lbs')]
    height: Annotated[int, Field(..., gt=50, description='Height of the User in centimeters (cm)')]
    dietary_restrictions: Annotated[str, Field(...,description='All the restrictions from the user')]
    calories: Annotated[int, Field(...,gt=0, description="Calories a user is expecting to consume in grams")]
    protein: Annotated[int, Field(...,gt=0, description="Protein a user is expecting to consume in grams")]
    comments: Annotated[str,Field(description="Any additional comments from the user")]

    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight/(self.height**2)