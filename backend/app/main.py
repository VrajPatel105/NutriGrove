from datetime import datetime
from backend.app.ai_food_recommendation import FoodRecommender
import json

# need to implement new logic, since i have moved the scraping code to a new repo 


recommender = FoodRecommender()
    
# testing this with user preferences manually
user_preferences = {
    "dietary_restrictions": ["vegetarian"],
    "allergies": ["nuts"],
    "calorie_target": 2500,
    "protein_target": 120,
    "weight_kg": 64 ,
    "height_cm": 177,
    "age": 20,
    "comments":"I dont want fried food today. ALso today i am really craving for some good salad :) . also, i am indian vegeterian meaning that i dont eat eggs too. so no eggs please"
}
schedule = recommender.get_daily_meal_schedule(user_preferences)

if "error" in schedule:
    print(f"Error: {schedule['error']}")
else:
    print("Stored daily meal schedule succesfully!!")