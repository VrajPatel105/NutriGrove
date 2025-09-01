import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

class FoodRecommender:
    def __init__(self):
        """Initialize the AI Food Recommender with Google Gemini"""
        # Load .env from backend/app directory
        env_path = Path(__file__).parent / ".env"
        load_dotenv(env_path)
        
        # Initialize Google Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("Missing GEMINI_API_KEY in .env file")
        
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials in .env file")
        
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Initialize caching
        self._menu_cache = None
        self._cache_timestamp = 0
        self._cache_duration = 3600  # 1 hour cache
        
        print("AI Recommender initialized successfully!")
    
    def get_all_menu_data(self):
        """Get ALL available food data from database with caching"""
        current_time = time.time()
        
        # Check if cache is valid (force refresh for now)
        if (True or self._menu_cache is None or 
            current_time - self._cache_timestamp > self._cache_duration):
            
            try:
                print("Fetching fresh menu data from database...")
                result = self.supabase.table('cleaned_data').select('*').execute()
                self._menu_cache = result.data
                self._cache_timestamp = current_time
                print(f"Menu data cached successfully. {len(self._menu_cache)} items loaded.")
            except Exception as e:
                print(f"Error fetching menu data: {e}")
                return self._menu_cache or []
        else:
            print("Using cached menu data...")
        
        return self._menu_cache or []
    
    def format_menu_data(self, menu_items):
        """Format menu data for AI processing"""
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
        return formatted_menu
    
    def get_daily_meal_schedule(self, user_preferences):
        """Generate a complete daily meal schedule using single API call"""
        
        # Get ALL menu data (cached)
        menu_items = self.get_all_menu_data()
        if not menu_items:
            return {"error": "No menu data available"}
        
        # Format data for AI
        formatted_menu = self.format_menu_data(menu_items)
        
        # Comprehensive prompt for single API call
        prompt = f"""
You are an expert nutritionist creating a complete daily meal plan for a university student. 

USER PREFERENCES AND GOALS:
{json.dumps(user_preferences, indent=2)}

COMPLETE DINING HALL MENU (ALL AVAILABLE OPTIONS):
{json.dumps(formatted_menu, indent=2)}

CRITICAL PORTION AND NUTRITION CALCULATION RULES:
1. ALWAYS calculate nutrition values based on ACTUAL portions needed
2. If menu shows "1 egg = 70 calories, 6g protein" but you recommend "3 eggs", then list "210 calories, 18g protein"
3. Scale ALL nutritional values (calories, protein, carbs, fat, fiber, sodium) proportionally to serving size
4. If user requests specific protein/calorie targets, you MUST meet or exceed them with 10% buffer - this is NON-NEGOTIABLE
5. Give a short reason on why you selected this in the reason selected field
CRITICAL: Show your multiplication clearly. If menu shows '1 egg = 6g protein' and you recommend '3 eggs', you MUST show '3 × 6g = 18g protein' in your calculations.
INSTRUCTIONS:
1. **PRIORITIZE USER COMMENTS ABOVE ALL OTHER REQUIREMENTS** - if user says they want specific foods, portions, or goals, follow their requests exactly
2. Analyze ALL menu options and select the BEST combinations for breakfast, lunch, and dinner
3. **MANDATORY**: Meet or exceed the user's calorie and protein targets - do not go under
4. Ensure the meal plan meets ALL dietary restrictions and avoids ALL allergens
5. Calculate nutritional values based on actual recommended portions, not menu base portions
6. Provide variety across meals and different dining stations
7. Use user's age, height, weight for BMI-informed recommendations
8. Explain portion calculations and target achievement in your reasoning

RESPOND ONLY with valid JSON in this EXACT format:

{{
  "breakfast": [
    {{
      "name": "Exact Food Name",
      "station": "Exact Station Name",
      "recommended_portion": "X servings (e.g., '2 eggs', '1.5 cups oatmeal')",
      "serving_size": "Portion calculation (e.g., 'Menu: 1 egg, Recommended: 2 eggs')",
      "calories": calculated_total_calories_for_recommended_portion,
      "protein_g": calculated_total_protein_for_recommended_portion,
      "carbs_g": calculated_total_carbs_for_recommended_portion,
      "fat_g": calculated_total_fat_for_recommended_portion,
      "fiber_g": calculated_total_fiber_for_recommended_portion,
      "sodium_mg": calculated_total_sodium_for_recommended_portion,
      "allergens": ["list", "of", "allergens"],
      "reason_selected": "Explain: 1) Why chosen, 2) Portion calculation (e.g., 'Menu lists 1 egg=70cal/6g protein, recommending 2 eggs=140cal/12g protein'), 3) How it helps achieve user's targets"
    }}
  ],
  "lunch": [
    {{
      "name": "Exact Food Name",
      "station": "Exact Station Name",
      "recommended_portion": "X servings",
      "serving_size": "Portion calculation",
      "calories": calculated_total_for_portion,
      "protein_g": calculated_total_for_portion,
      "carbs_g": calculated_total_for_portion,
      "fat_g": calculated_total_for_portion,
      "fiber_g": calculated_total_for_portion,
      "sodium_mg": calculated_total_for_portion,
      "allergens": ["list", "of", "allergens"],
      "reason_selected": "Detailed explanation with portion math"
    }}
  ],
  "dinner": [
    {{
      "name": "Exact Food Name",
      "station": "Exact Station Name",
      "recommended_portion": "X servings",
      "serving_size": "Portion calculation",
      "calories": calculated_total_for_portion,
      "protein_g": calculated_total_for_portion,
      "carbs_g": calculated_total_for_portion,
      "fat_g": calculated_total_for_portion,
      "fiber_g": calculated_total_for_portion,
      "sodium_mg": calculated_total_for_portion,
      "allergens": ["list", "of", "allergens"],
      "reason_selected": "Detailed explanation with portion math"
    }}
  ],
  "daily_totals": {{
    "total_calories": sum_of_all_calculated_calories,
    "total_protein_g": sum_of_all_calculated_protein,
    "total_carbs_g": sum_of_all_calculated_carbs,
    "total_fat_g": sum_of_all_calculated_fat,
    "total_fiber_g": sum_of_all_calculated_fiber,
    "total_sodium_mg": sum_of_all_calculated_sodium,
    "calorie_target": user_calorie_target,
    "protein_target": user_protein_target,
    "calorie_difference": actual_total_minus_target,
    "protein_difference": actual_total_minus_target
  }},
  "meal_plan_analysis": {{
    "calorie_goal_status": "Achieved: [actual_calories] vs target [target_calories] (+/- X difference)",
    "protein_goal_status": "Achieved: [actual_protein]g vs target [target_protein]g (+/- X difference)",
    "target_achievement": "SUCCESS - All targets met/exceeded" or "FAILED - Explain what targets were missed and why",
    "dietary_compliance": "All restrictions followed" or "Issues: description",
    "nutritional_balance": "Assessment of overall nutritional balance",
    "variety_score": "Good/Excellent variety across stations and food types",
    "health_rating": "Excellent/Good/Fair - brief explanation",
    "portion_transparency": "All nutrition values calculated for recommended portions, not menu base portions",
    "user_comment_compliance": "Followed user's specific requests: [list what was followed]" or "No specific requests in comments",
    "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
  }}
}}

ABSOLUTE REQUIREMENTS - DO NOT COMPROMISE ON THESE:
1. **NEVER go under the user's calorie or protein targets** - if targets can't be met with available food, recommend larger portions
2. **Calculate ALL nutrition values for the actual recommended portions** - not the menu base portions
3. **Show portion math clearly** - if recommending 2 eggs and menu shows 1 egg nutrition, multiply by 2
4. **User comments override all other requirements** - if user requests specific foods/amounts, prioritize their requests
5. **Total daily calories must be within +50 of target** (never more than 50 under)
6. **Total daily protein must meet or exceed target by at least 5g**
7. **Explain your portion calculations** in the reason_selected field
8. **NO TEXT outside the JSON structure**
9. **Use EXACT values from the menu data provided**
10. **Select 2-4 items per meal for balanced nutrition**

QUALITY CHECK BEFORE RESPONDING:
- Verify total calories ≥ target calories
- Verify total protein ≥ target protein  
- Verify all nutrition values reflect recommended portions, not menu base portions
- Verify user's specific comments/requests are addressed

JSON FORMATTING REQUIREMENTS:
- Use only standard ASCII characters in text fields
- Avoid special quotes (use only "straight quotes")
- No line breaks within string values
- Keep all decimal numbers as simple floats (e.g., 42.5, not 42.50)
- Escape any internal quotes with backslash
- Test that your JSON is valid before responding
"""
        
        try:
            print("Generating meal plan with single API call...")
            response = self.model.generate_content(prompt)
            ai_response = response.text.strip()
            
            # Clean up response
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            
            # Extract JSON
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                meal_schedule = json.loads(json_str)
                
                # Save to file
                self.save_response_to_file(meal_schedule, user_preferences)
                print("Meal plan generated successfully!")
                
                return meal_schedule
            else:
                return {"error": "Failed to parse AI response", "raw_response": ai_response}
                
        except json.JSONDecodeError as e:
            return {"error": "Failed to parse AI response as JSON", "json_error": str(e), "raw_response": ai_response}
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
                "timestamp": json.dumps({"generated_at": time.time()})
            }
            
            # Save to file
            file_path = 'backend/app/data/ai_response/daily_meal_schedule.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)
            
            print(f"AI response saved to: {file_path}")
            
        except Exception as e:
            print(f"Error saving response to file: {e}")
