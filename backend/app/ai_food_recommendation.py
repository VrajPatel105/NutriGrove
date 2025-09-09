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
        """Format menu data for AI processing with full nutrition info and sanitized ingredients"""
        formatted_menu = []
        for item in menu_items:
            food_data = item.get('data', {})
            nutrition = food_data.get('nutrition', {}) or {}

            # --- Sanitize ingredients ---
            ing = nutrition.get('ingredients', 'N/A')
            if isinstance(ing, str):
                # Remove any disclaimer text starting with "Disclaimer:"
                if "Disclaimer:" in ing:
                    ing = ing.split("Disclaimer:")[0].strip()
            else:
                ing = 'N/A'
            nutrition['ingredients'] = ing

            # --- Build formatted item ---
            formatted_item = {
                "name": food_data.get("food_name", "Unknown"),
                "station": food_data.get("station_name", "Unknown"),
                "meal_type": food_data.get("meal_type", "Unknown"),
                "nutrition": nutrition  # keep ALL fields (macros + micros + extras)
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
        prompt = """
You are an expert nutritionist creating a complete daily meal plan for a university student.

USER PREFERENCES AND GOALS:
{json.dumps(user_preferences, indent=2)}

COMPLETE DINING HALL MENU (ALL AVAILABLE OPTIONS):
{json.dumps(formatted_menu, indent=2)}

CRITICAL PORTION AND NUTRITION CALCULATION RULES:
1. ALWAYS calculate nutrition values based on ACTUAL portions needed.
2. If menu shows "1 egg = 70 calories, 6g protein" but you recommend "3 eggs", then list "210 calories, 18g protein".
3. Scale ALL numeric nutrient fields (macros and micronutrients) proportionally to serving size, including but not limited to:
   - calories, protein_g, carbs_g, fat_g, fiber_g, sodium_mg
   - sugar_g, saturated_fat_g, trans_fat_g, cholesterol_mg
   - calcium_mg, iron_mg, potassium_mg, vitamin_a_re, vitamin_c_mg, vitamin_d_iu
   - plus ANY additional numeric nutrient keys present in the input.
4. If a micronutrient field is missing in the menu data, set it to 0 (do NOT invent values); do not count it toward totals when 0.
5. Give a short reason on why you selected each item in the reason_selected field.

DATA SANITIZATION REQUIREMENTS:
- If "ingredients" contains any substring beginning with "Disclaimer:", remove that entire disclaimer text and return a clean ingredients string.
- Remove trailing whitespace and line breaks in ingredients; use a single space between sentences.

INSTRUCTIONS:
1. PRIORITIZE USER COMMENTS ABOVE ALL OTHER REQUIREMENTS — if user says they want specific foods, portions, or goals, follow exactly.
2. Analyze ALL menu options and select the BEST combinations for breakfast, lunch, and dinner.
3. MANDATORY: Meet or exceed the user's calorie and protein targets; never go under.
4. Ensure the meal plan meets ALL dietary restrictions and avoids ALL allergens.
5. Calculate nutritional values based on actual recommended portions, not menu base portions.
6. Provide variety across meals and different dining stations.
7. Use user's age, height, weight for BMI-informed recommendations.
8. Explain portion calculations and target achievement in your reasoning.
9. Quantity requirement per meal: Return 2-4 items for breakfast, 2-4 items for lunch, and 2-4 items for dinner. NEVER return fewer than 2 items per meal (except the weekend brunch rule below).
10. CRITICAL weekend rule: if it's weekend (saturday's or sunday's), the menu will only have two meal types in total. One is dinner, and other is either from breakfast or lunch because it's Brunch on campus on weekends. So make sure that if it's weekend, you include more meal in just lunch at once (3–6 items) to meet targets.

AUTO-CORRECT LOOP (DO NOT SKIP):
- Before responding, compute totals. If ANY of the following would be true:
  a) total calories < calorie_target OR
  b) total protein_g < protein_target OR
  c) any meal has < 2 items (unless weekend brunch consolidation),
  THEN you MUST add additional items and/or increase portions and recompute until ALL constraints are satisfied.
- You must NOT return a result where goals are missed. Do not output a FAILED status in analysis; adjust the plan instead so it passes.

RESPOND ONLY with valid JSON in this EXACT format:

{
  "breakfast": [
    {
      "name": "Exact Food Name",
      "station": "Exact Station Name",
      "recommended_portion": "X servings (e.g., "2 eggs", "1.5 cups oatmeal")",
      "serving_size": "Portion calculation (e.g., "Menu: 1 egg, Recommended: 2 eggs")",
      "calories": total_cal_for_recommended_portion,
      "protein_g": total_protein_for_recommended_portion,
      "carbs_g": total_carbs_for_recommended_portion,
      "fat_g": total_fat_for_recommended_portion,
      "fiber_g": total_fiber_for_recommended_portion,
      "sodium_mg": total_sodium_for_recommended_portion,
      "allergens": ["list", "of", "allergens"],
      "ingredients": "sanitized_ingredients_without_disclaimer",
      "full_nutrition": {
        "sugar_g": scaled_sugar_g_or_0,
        "saturated_fat_g": scaled_saturated_fat_g_or_0,
        "trans_fat_g": scaled_trans_fat_g_or_0,
        "cholesterol_mg": scaled_cholesterol_mg_or_0,
        "calcium_mg": scaled_calcium_mg_or_0,
        "iron_mg": scaled_iron_mg_or_0,
        "potassium_mg": scaled_potassium_mg_or_0,
        "vitamin_a_re": scaled_vitamin_a_re_or_0,
        "vitamin_c_mg": scaled_vitamin_c_mg_or_0,
        "vitamin_d_iu": scaled_vitamin_d_iu_or_0
      },
      "portion_math": "Example: 3 x 6g protein = 18g; 3 x 70 cal = 210 cal",
      "reason_selected": "Explain: 1) Why chosen, 2) Portion calculation, 3) How it helps targets"
    }
  ],
  "lunch": [ { ... same structure as breakfast item ... } ],
  "dinner": [ { ... same structure as breakfast item ... } ],
  "daily_totals": {
    "total_calories": sum_of_all_calculated_calories,
    "total_protein_g": sum_of_all_calculated_protein,
    "total_carbs_g": sum_of_all_calculated_carbs,
    "total_fat_g": sum_of_all_calculated_fat,
    "total_fiber_g": sum_of_all_calculated_fiber,
    "total_sodium_mg": sum_of_all_calculated_sodium,
    "total_sugar_g": sum_of_all_calculated_sugar_or_0,
    "total_saturated_fat_g": sum_of_all_calculated_saturated_fat_or_0,
    "total_trans_fat_g": sum_of_all_calculated_trans_fat_or_0,
    "total_cholesterol_mg": sum_of_all_calculated_cholesterol_or_0,
    "total_calcium_mg": sum_of_all_calculated_calcium_or_0,
    "total_iron_mg": sum_of_all_calculated_iron_or_0,
    "total_potassium_mg": sum_of_all_calculated_potassium_or_0,
    "total_vitamin_a_re": sum_of_all_calculated_vit_a_or_0,
    "total_vitamin_c_mg": sum_of_all_calculated_vit_c_or_0,
    "total_vitamin_d_iu": sum_of_all_calculated_vit_d_or_0,
    "calorie_target": user_calorie_target,
    "protein_target": user_protein_target,
    "calorie_difference": actual_total_minus_target,
    "protein_difference": actual_total_minus_target
  },
  "meal_plan_analysis": {
    "calorie_goal_status": "Achieved: [actual_calories] vs target [target_calories] (+/- X difference)",
    "protein_goal_status": "Achieved: [actual_protein]g vs target [target_protein]g (+/- X difference)",
    "target_achievement": "SUCCESS - All targets met/exceeded",
    "dietary_compliance": "All restrictions followed" or "Issues: description",
    "nutritional_balance": "Assessment of overall nutritional balance",
    "variety_score": "Good/Excellent variety across stations and food types",
    "health_rating": "Excellent/Good/Fair - brief explanation",
    "portion_transparency": "All nutrition values calculated for recommended portions, not menu base portions",
    "user_comment_compliance": "Followed user's specific requests: [list what was followed]" or "No specific requests in comments",
    "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
  }
}

ABSOLUTE REQUIREMENTS - DO NOT COMPROMISE ON THESE:
1. NEVER go under the user's calorie or protein targets — if targets can't be met with available food, recommend larger portions and/or add more items.
2. Calculate ALL numeric nutrition values (including micronutrients and any extra keys present) for the actual recommended portions.
3. User comments override all other requirements.
4. Total daily calories must be within +50 of target (never more than 50 under).
5. Total daily protein must meet or exceed target by at least 5g.
6. Return 2–4 items per meal (minimum 2 per meal), except on weekends when brunch is consolidated as specified.
7. NO TEXT outside the JSON structure.
8. Use EXACT values from the menu data provided; for missing fields of micronutrients, use integer 0 and do not fabricate.
9. Select 2–4 items per meal for balanced nutrition.
10. DO NOT return a result that fails targets; if your draft would fail, adjust portions/items and try again before responding.

QUALITY CHECK BEFORE RESPONDING:
- Verify total calories ≥ target calories and within +50 of target.
- Verify total protein ≥ target protein + 5g.
- Verify all nutrition values reflect recommended portions (not menu base).
- Verify each meal contains at least 2 items (unless weekend brunch consolidation).
- Verify user's specific comments/requests are addressed.
- Verify ingredients have NO disclaimer text.

JSON FORMATTING REQUIREMENTS:
- Use only standard ASCII characters in text fields.
- Avoid special quotes (use only "straight quotes").
- No line breaks within string values.
- Keep all decimal numbers as simple floats (e.g., 42.5, not 42.50).
- Escape any internal quotes with backslash.
- Test that your JSON is valid before responding.
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
