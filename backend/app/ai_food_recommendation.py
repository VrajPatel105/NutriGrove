import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

class FoodRecommender:
    def __init__(self):
        """Initialize the AI Food Recommender with Google Gemini
        Google Gemini is being used because I have a student  acccount that offeres api for free (till certain limit ofc :) )
        """
        load_dotenv()
        
        # Initialize Google Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("Missing GEMINI_API_KEY in .env file")
        
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        # adding this to rectify specific errors
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials in .env file")
        
        self.supabase = create_client(supabase_url, supabase_key)
        print("AI Recommender initialized successfully!")
    
    def get_all_menu_data(self):
        """Get ALL available food data from database"""
        try:
            # getting all thee cleaned data from supabase db
            result = self.supabase.table('cleaned_data').select('*').execute()
            return result.data
        except Exception as e:
            print(f"Error fetching menu data: {e}")
            return []
    
    # main function that will recommend
    def get_daily_meal_schedule(self, user_preferences):
        """Generate a complete daily meal schedule"""
        
        # Get ALL menu data
        menu_items = self.get_all_menu_data()
        if not menu_items:
            return {"error": "No menu data available"}
        
        # Format data for AI
        formatted_menu = []
        for item in menu_items:
            food_data = item['data']
            nutrition = food_data['nutrition']
            
            formatted_item = {
                'name': food_data['food_name'],
                'station': food_data['station_name'],
                'meal_type': food_data['meal_type'],
                'calories': nutrition.get('calories', 0),
                'protein_g': nutrition.get('protein_g', 0),
                'carbs_g': nutrition.get('carbs_g', 0),
                'fat_g': nutrition.get('total_fat_g', 0),
                'fiber_g': nutrition.get('dietary_fiber_g', 0),
                'sodium_mg': nutrition.get('sodium_mg', 0),
                'serving_size': nutrition.get('serving_size', 'N/A'),
                'allergens': nutrition.get('allergens', []),
                'ingredients': nutrition.get('ingredients', 'N/A')
            }
            formatted_menu.append(formatted_item)
        
        # Prompt for model
        prompt = f"""
You are an expert nutritionist creating a complete daily meal plan for a university student. 

USER PREFERENCES AND GOALS:
{json.dumps(user_preferences, indent=2)}

COMPLETE DINING HALL MENU (ALL AVAILABLE OPTIONS):
{json.dumps(formatted_menu, indent=2)}

INSTRUCTIONS:
1. Analyze ALL menu options and select the BEST combinations for breakfast, lunch, and dinner
2. Ensure the meal plan meets ALL dietary restrictions and avoids ALL allergens
3. Target the specified calorie and protein goals as closely as possible
4. Provide variety across meals and different dining stations
5. Include complete nutritional information for each selected item
6. Explain WHY each food was chosen
7. Also, make sure you use the user's personal information such as age, height and weight for bmi reference to recommend better.

RESPOND ONLY with valid JSON in this EXACT format:

{{
  "breakfast": [
    {{
      "name": "Exact Food Name",
      "station": "Exact Station Name",
      "serving_size": "Exact serving size from menu",
      "calories": exact_number,
      "protein_g": exact_number,
      "carbs_g": exact_number,
      "fat_g": exact_number,
      "fiber_g": exact_number_or_0,
      "sodium_mg": exact_number_or_0,
      "allergens": ["list", "of", "allergens"],
      "reason_selected": "Detailed explanation why this food was chosen - nutritional benefits, how it fits goals, etc."
    }}
  ],
  "lunch": [
    {{
      "name": "Exact Food Name",
      "station": "Exact Station Name", 
      "serving_size": "Exact serving size from menu",
      "calories": exact_number,
      "protein_g": exact_number,
      "carbs_g": exact_number,
      "fat_g": exact_number,
      "fiber_g": exact_number_or_0,
      "sodium_mg": exact_number_or_0,
      "allergens": ["list", "of", "allergens"],
      "reason_selected": "Detailed explanation why this food was chosen"
    }}
  ],
  "dinner": [
    {{
      "name": "Exact Food Name",
      "station": "Exact Station Name",
      "serving_size": "Exact serving size from menu", 
      "calories": exact_number,
      "protein_g": exact_number,
      "carbs_g": exact_number,
      "fat_g": exact_number,
      "fiber_g": exact_number_or_0,
      "sodium_mg": exact_number_or_0,
      "allergens": ["list", "of", "allergens"],
      "reason_selected": "Detailed explanation why this food was chosen"
    }}
  ],
  "daily_totals": {{
    "total_calories": sum_of_all_calories,
    "total_protein_g": sum_of_all_protein,
    "total_carbs_g": sum_of_all_carbs,
    "total_fat_g": sum_of_all_fat,
    "total_fiber_g": sum_of_all_fiber,
    "total_sodium_mg": sum_of_all_sodium
  }},
  "meal_plan_analysis": {{
    "calorie_goal_status": "Met/Over/Under target by X calories",
    "protein_goal_status": "Met/Over/Under target by X grams", 
    "dietary_compliance": "All restrictions followed" or "Issues: description",
    "nutritional_balance": "Assessment of overall nutritional balance",
    "variety_score": "Good/Excellent variety across stations and food types",
    "health_rating": "Excellent/Good/Fair - brief explanation",
    "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
    "additional_comments": " "
  }}
}}

CRITICAL REQUIREMENTS:
- Use EXACT values from the menu data provided
- Select 2-4 items per meal for balanced nutrition
- Ensure total daily calories are within 100 calories of target
- Ensure protein meets or exceeds target
- Provide detailed reasoning for each food choice
- Calculate accurate totals
- NO TEXT outside the JSON structure
- ALso please confirm in the suggestions that if you followed the user's comments or not and how.
- Also make sure to prioritize the user's preferences. If user adds a comment of some certain type of request, then you dont need to follow all this critical reqs if the user's comment is contradicting it .
"""
        
        try:
            response = self.model.generate_content(prompt)
            ai_response = response.text.strip()
            
            # Clean up response
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            try:
                meal_schedule = json.loads(ai_response)
                
                # Save to file
                self.save_response_to_file(meal_schedule, user_preferences)
                
                return meal_schedule
            except json.JSONDecodeError:
                return {"error": "Failed to parse AI response", "raw_response": ai_response}
            
        except Exception as e:
            return {"error": f"AI service error: {str(e)}"}
    
    def save_response_to_file(self, meal_schedule, user_preferences):
        """Save AI response to backend/app/data/ai_response folder"""
        try:
            # Create directory if it doesn't exist
            os.makedirs('backend/app/data/ai_response', exist_ok=True)
            
            # Create response with metadata
            response_data = {
                "user_preferences": user_preferences,
                "meal_schedule": meal_schedule,
                "timestamp": json.dumps({"generated_at": "now"})  # You can add actual timestamp
            }
            
            # Save to file
            file_path = 'backend/app/data/ai_response/daily_meal_schedule.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)
            
            print(f"AI response saved to: {file_path}")
            
        except Exception as e:
            print(f"Error saving response to file: {e}")