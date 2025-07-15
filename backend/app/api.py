# Using fastapi for getting response and sending resopnses to the user
from fastapi import FASTAPI
from fastapi.responses import JSONResponse
from model.schema import UserInput

app = FASTAPI()

@app.post('/recommendations')
def recommendations(data: UserInput):
    user_preferences = {
        'age': data.age,
        'weight': data.wegith,
        'height': data.height,
        'dietary_restrictions': data.dietary_restrictions,
        'calories' : data.calories,
        'protein': data.protein,
        'comments': data.comments
    }

