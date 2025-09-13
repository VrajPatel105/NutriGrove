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
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
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
        prompt = f"""
You are an expert nutritionist. Create a complete daily meal plan for a university student using the dining hall menu provided.

## INPUT DATA:

USER PREFERENCES AND GOALS:
{json.dumps(user_preferences, indent=2)}

COMPLETE DINING HALL MENU (ALL AVAILABLE OPTIONS):
{json.dumps(formatted_menu, indent=2)}

## PRIMARY OBJECTIVES (IN ORDER OF PRIORITY):
1. **Follow user comments/requests EXACTLY** - User-specified foods, portions, or goals override everything else
2. **Meet calorie target** - Must reach or exceed user's calorie goal (never go under)
3. **Meet protein target** - Must reach or exceed user's protein goal (never go under) 
4. **Honor dietary restrictions** - Strictly avoid all allergens and restrictions listed
5. **Provide variety** - Select from different dining stations and food types

## PORTION CALCULATION RULES:
- Base nutrition values are per menu serving size
- Scale ALL nutrients proportionally to your recommended portion
- Example: Menu shows "1 egg = 70 cal, 6g protein" → You recommend "3 eggs" → Calculate as "210 cal, 18g protein"
- Scale these fields: calories, protein_g, carbs_g, fat_g, fiber_g, sodium_mg, sugar_g, saturated_fat_g, trans_fat_g, cholesterol_mg, calcium_mg, iron_mg, potassium_mg, vitamin_a_re, vitamin_c_mg, vitamin_d_iu
- If a nutrient is missing from menu data, use null (don't invent values)

## WEEKEND SPECIAL RULE:
If it's Saturday or Sunday, dining halls serve brunch instead of separate breakfast/lunch. Plan accordingly with larger portions to meet daily targets.

## DATA CLEANING:
- Remove any "Disclaimer:" text from ingredients
- Clean up extra whitespace and line breaks

## REQUIRED JSON OUTPUT FORMAT:

{{
  "breakfast": [
    {{
      "name": "Exact menu item name",
      "station": "Exact station name from menu",
      "recommended_portion": "Clear portion description (e.g. '2 eggs', '1.5 cups')",
      "serving_size": "Menu base vs recommended (e.g. 'Menu: 1 egg, Recommended: 2 eggs')",
      "calories": calculated_total_calories,
      "protein_g": calculated_total_protein,
      "carbs_g": calculated_total_carbs,
      "fat_g": calculated_total_fat,
      "fiber_g": calculated_total_fiber,
      "sodium_mg": calculated_total_sodium,
      "allergens": ["list", "from", "menu"],
      "ingredients": "cleaned ingredients without disclaimers",
      "per_menu_serving_nutrition": {{
        "serving_size": "base serving from menu",
        "calories": base_calories,
        "protein_g": base_protein,
        "carbs_g": base_carbs,
        "fat_g": base_fat,
        "fiber_g": base_fiber,
        "sodium_mg": base_sodium,
        "sugar_g": base_sugar_or_null,
        "saturated_fat_g": base_sat_fat_or_null,
        "trans_fat_g": base_trans_fat_or_null,
        "cholesterol_mg": base_cholesterol_or_null,
        "calcium_mg": base_calcium_or_null,
        "iron_mg": base_iron_or_null,
        "potassium_mg": base_potassium_or_null,
        "vitamin_a_re": base_vit_a_or_null,
        "vitamin_c_mg": base_vit_c_or_null,
        "vitamin_d_iu": base_vit_d_or_null
      }},
      "full_nutrition": {{
        "calories": scaled_calories,
        "protein_g": scaled_protein,
        "carbs_g": scaled_carbs,
        "fat_g": scaled_fat,
        "fiber_g": scaled_fiber,
        "sodium_mg": scaled_sodium,
        "sugar_g": scaled_sugar_or_null,
        "saturated_fat_g": scaled_sat_fat_or_null,
        "trans_fat_g": scaled_trans_fat_or_null,
        "cholesterol_mg": scaled_cholesterol_or_null,
        "calcium_mg": scaled_calcium_or_null,
        "iron_mg": scaled_iron_or_null,
        "potassium_mg": scaled_potassium_or_null,
        "vitamin_a_re": scaled_vit_a_or_null,
        "vitamin_c_mg": scaled_vit_c_or_null,
        "vitamin_d_iu": scaled_vit_d_or_null
      }},
      "portion_math": "Show calculation: 3 servings x 70 cal = 210 cal, 3 x 6g protein = 18g",
      "reason_selected": "Explain: 1) Why chosen 2) How portion was calculated 3) How it helps meet targets"
    }}
  ],
  "lunch": [
    // Same structure as breakfast items
  ],
  "dinner": [
    // Same structure as breakfast items
  ],
  "daily_totals": {{
    "total_calories": sum_all_meal_calories,
    "total_protein_g": sum_all_meal_protein,
    "total_carbs_g": sum_all_meal_carbs,
    "total_fat_g": sum_all_meal_fat,
    "total_fiber_g": sum_all_meal_fiber,
    "total_sodium_mg": sum_all_meal_sodium,
    "calorie_target": user_target_calories,
    "protein_target": user_target_protein,
    "calorie_difference": actual_minus_target,
    "protein_difference": actual_minus_target
  }},
  "meal_plan_analysis": {{
    "calorie_goal_status": "Met: [actual] vs target [target] (+/- difference)",
    "protein_goal_status": "Met: [actual]g vs target [target]g (+/- difference)",
    "target_achievement": "SUCCESS - All targets met" or "FAILED - Missing: [what was missed]",
    "dietary_compliance": "All restrictions followed" or "Issues: [specific issues]",
    "user_comment_compliance": "Followed: [list user requests]" or "No specific requests",
    "suggestions": ["tip 1", "tip 2", "tip 3"]
  }}
}}

## CRITICAL SUCCESS CRITERIA:
✓ Total daily calories ≥ user's calorie target
✓ Total daily protein ≥ user's protein target  
✓ All allergens and dietary restrictions avoided
✓ User's specific comments/requests followed exactly
✓ 3-5 food items per meal for balanced nutrition
✓ All nutrition calculations based on recommended portions (not menu base)
✓ Portion math clearly shown

## BEFORE RESPONDING:
1. Check: Does total calories meet/exceed target?
2. Check: Does total protein meet/exceed target?
3. Check: Are user's specific requests addressed?
4. Check: Are all dietary restrictions followed?
5. Check: Is nutrition calculated for recommended portions?
6. ALso make sure that when you respond, you give top 3 recommendations to the user on what they should be doing to maintain. and make sure that they are not too large recommendations.

Respond with ONLY the JSON - no additional text or explanations outside the JSON structure.
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
