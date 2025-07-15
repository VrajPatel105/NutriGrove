# Using fastapi for getting response and sending resopnses to the user
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from backend.app.model.schema import UserInput
from backend.app.ai_food_recommendation import FoodRecommender

recommender = FoodRecommender()
app = FastAPI()

@app.get('/')
def hello():
    return {'message':'Hello, This is API system for NutriGrove'}

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

    schedule = recommender.get_daily_meal_schedule(user_preferences)

    return JSONResponse(status_code=200, content=schedule)