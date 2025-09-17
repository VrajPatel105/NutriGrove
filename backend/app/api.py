# Using fastapi for getting response and sending resopnses to the user
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .model.schema import UserInput
from .ai_food_recommendation import FoodRecommender

recommender = FoodRecommender()
app = FastAPI()

@app.get('/')
def hello():
    return {'message':'Hello, This is API system for NutriGrove'}

@app.post('/recommendations')
def recommendations(data: UserInput):
    user_preferences = {
        'age': data.age,
        'gender': data.gender,
        'weight': data.weight,
        'height': data.height,
        'activity level': data.activity_level,
        'goal' : data.goal,
        'diet' : data.diet,
        'dietary_restrictions': data.dietary_restrictions,
        'calories' : data.calories,
        'protein': data.protein,
        'comments': data.comments,
        'allergens': data.allergens,
        'dislikes': data.dislikes
    }

    schedule = recommender.get_daily_meal_schedule(user_preferences)

    return JSONResponse(status_code=200, content=schedule)

# Adding a new api endpoint for getting the entire menu data. Used the function from class FoodRecommender. : EDIT - will need to figure it out later on.
@app.get('/menu')
def todays_menu():
    return recommender.get_all_menu_data()

#   Essential Parameters (definitely add these):
# age
# weight
# height
# dietary_restrictions
# calories
# protein
# comments 
# THE ALL ABOVE ALREADY EXISTS IN THE API, BUT THE ONE'S BELOW NEEDS TO BE ADDED TO THE API. (09/09/25)
#   - gender (male/female)
#   - activity_level (active/sedentary/moderate)
#   - goal (build_muscle/lose_weight/maintain)
#   - diet (Keto/Paleo/Vegan/etc.)
#   - allergens (array like [Eggs, Fish, Shellfish])
#   - dislikes (array of disliked foods)