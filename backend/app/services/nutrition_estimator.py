"""
Nutrition Estimator Service
Estimates nutrition for external foods not in dining hall menu
Uses Claude's built-in knowledge + optional external APIs
"""

import os
import httpx
from typing import Dict, Optional
from dotenv import load_dotenv


class NutritionEstimator:
    """
    Estimate nutrition for external foods not in dining hall menu
    Uses Claude's built-in knowledge + optional external APIs
    """

    def __init__(self):
        load_dotenv()
        self.nutritionix_app_id = os.getenv("NUTRITIONIX_APP_ID")
        self.nutritionix_api_key = os.getenv("NUTRITIONIX_API_KEY")

    async def estimate_external_food(self, food_description: str) -> Optional[Dict]:
        """
        Estimate nutrition for external food

        Priority:
        1. Use Claude's knowledge (handled by ConversationalAgent)
        2. Fall back to Nutritionix API if available
        3. Fall back to USDA FoodData Central API

        Args:
            food_description: "Ferrero Rocher", "Starbucks Frappuccino Grande", "Doritos small bag"

        Returns:
            {
                'food_name': 'Ferrero Rocher',
                'portion': '1 piece',
                'calories': 73,
                'protein_g': 1.0,
                'carbs_g': 8.5,
                'fat_g': 4.5,
                'confidence': 'high'  # high/medium/low
            }
        """
        # Try Nutritionix first if API keys available
        if self.nutritionix_app_id and self.nutritionix_api_key:
            result = await self.query_nutritionix(food_description)
            if result:
                return result

        # Fall back to USDA
        result = await self.query_usda(food_description)
        if result:
            return result

        # If all APIs fail, return None
        # The ConversationalAgent (Claude) will handle estimation using its knowledge
        return None

    async def query_nutritionix(self, food_description: str) -> Optional[Dict]:
        """
        Query Nutritionix API for nutrition data
        Free tier: 500 requests/day

        Docs: https://www.nutritionix.com/business/api
        """
        if not self.nutritionix_app_id or not self.nutritionix_api_key:
            return None

        url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {
            "x-app-id": self.nutritionix_app_id,
            "x-app-key": self.nutritionix_api_key,
            "Content-Type": "application/json"
        }
        data = {"query": food_description}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data, timeout=10.0)
                response.raise_for_status()

                # Safe JSON parsing
                try:
                    result = response.json()
                except (ValueError, TypeError) as json_err:
                    print(f"Nutritionix JSON parse error: {json_err}")
                    return None

            if result and result.get('foods'):
                food = result['foods'][0]

                # Safe numeric conversion helper
                def safe_float(value, default=0):
                    try:
                        if value is None:
                            return default
                        if isinstance(value, str):
                            value = value.replace('<', '').replace('trace', '0').strip()
                        return float(value)
                    except (ValueError, TypeError):
                        return default

                return {
                    'food_name': food['food_name'],
                    'portion': f"{food['serving_qty']} {food['serving_unit']}",
                    'calories': int(safe_float(food.get('nf_calories', 0))),
                    'protein_g': round(safe_float(food.get('nf_protein', 0)), 1),
                    'carbs_g': round(safe_float(food.get('nf_total_carbohydrate', 0)), 1),
                    'fat_g': round(safe_float(food.get('nf_total_fat', 0)), 1),
                    'fiber_g': round(safe_float(food.get('nf_dietary_fiber', 0)), 1),
                    'sugar_g': round(safe_float(food.get('nf_sugars', 0)), 1),
                    'sodium_mg': round(safe_float(food.get('nf_sodium', 0)), 1),
                    'confidence': 'high'
                }
        except Exception as e:
            print(f"Nutritionix API error: {e}")
            return None

        return None

    async def query_usda(self, food_description: str) -> Optional[Dict]:
        """
        Query USDA FoodData Central
        100% free, no API key required

        Docs: https://fdc.nal.usda.gov/api-guide.html
        """
        # USDA API key (optional, but recommended for higher rate limits)
        api_key = os.getenv("USDA_API_KEY", "DEMO_KEY")

        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {
            "query": food_description,
            "pageSize": 1,
            "api_key": api_key
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()

                # Safe JSON parsing
                try:
                    result = response.json()
                except (ValueError, TypeError) as json_err:
                    print(f"USDA JSON parse error: {json_err}")
                    return None

            if result and result.get('foods'):
                food = result['foods'][0]
                nutrients = {n['nutrientName']: n['value'] for n in food.get('foodNutrients', [])}

                # Safe numeric conversion helper
                def safe_float(value, default=0):
                    try:
                        if value is None:
                            return default
                        if isinstance(value, str):
                            value = value.replace('<', '').replace('trace', '0').strip()
                        return float(value)
                    except (ValueError, TypeError):
                        return default

                return {
                    'food_name': food['description'],
                    'portion': '100g',  # USDA uses 100g as base
                    'calories': int(safe_float(nutrients.get('Energy', 0))),
                    'protein_g': round(safe_float(nutrients.get('Protein', 0)), 1),
                    'carbs_g': round(safe_float(nutrients.get('Carbohydrate, by difference', 0)), 1),
                    'fat_g': round(safe_float(nutrients.get('Total lipid (fat)', 0)), 1),
                    'fiber_g': round(safe_float(nutrients.get('Fiber, total dietary', 0)), 1),
                    'sugar_g': round(safe_float(nutrients.get('Sugars, total including NLEA', 0)), 1),
                    'sodium_mg': round(safe_float(nutrients.get('Sodium, Na', 0)), 1),
                    'confidence': 'medium'
                }
        except Exception as e:
            print(f"USDA API error: {e}")
            return None

        return None

    def estimate_from_common_knowledge(self, food_description: str) -> Optional[Dict]:
        """
        Estimate nutrition for very common foods using built-in knowledge
        Used as a fast local fallback before API calls

        This is a simple database of common foods that students eat
        """
        # Common foods database (rough estimates per serving)
        common_foods = {
            # Snacks
            'ferrero rocher': {'calories': 73, 'protein_g': 1.0, 'carbs_g': 8.5, 'fat_g': 4.5, 'portion': '1 piece'},
            'chips': {'calories': 150, 'protein_g': 2.0, 'carbs_g': 15.0, 'fat_g': 10.0, 'portion': '1 oz'},
            'doritos': {'calories': 150, 'protein_g': 2.0, 'carbs_g': 18.0, 'fat_g': 8.0, 'portion': '1 oz'},
            'oreos': {'calories': 160, 'protein_g': 2.0, 'carbs_g': 25.0, 'fat_g': 7.0, 'portion': '3 cookies'},

            # Starbucks (approximate)
            'frappuccino': {'calories': 380, 'protein_g': 5.0, 'carbs_g': 54.0, 'fat_g': 15.0, 'portion': 'Grande'},
            'latte': {'calories': 190, 'protein_g': 12.0, 'carbs_g': 18.0, 'fat_g': 7.0, 'portion': 'Grande'},

            # Fast food
            'pizza': {'calories': 285, 'protein_g': 12.0, 'carbs_g': 36.0, 'fat_g': 10.0, 'portion': '1 slice'},
            'burger': {'calories': 540, 'protein_g': 25.0, 'carbs_g': 45.0, 'fat_g': 25.0, 'portion': '1 burger'},

            # Drinks
            'soda': {'calories': 140, 'protein_g': 0.0, 'carbs_g': 39.0, 'fat_g': 0.0, 'portion': '12 oz'},
            'beer': {'calories': 150, 'protein_g': 1.0, 'carbs_g': 13.0, 'fat_g': 0.0, 'portion': '12 oz'},
        }

        # Check for matches
        food_lower = food_description.lower()
        for key, nutrition in common_foods.items():
            if key in food_lower:
                return {
                    'food_name': food_description,
                    'portion': nutrition['portion'],
                    'calories': nutrition['calories'],
                    'protein_g': nutrition['protein_g'],
                    'carbs_g': nutrition['carbs_g'],
                    'fat_g': nutrition['fat_g'],
                    'confidence': 'medium'
                }

        return None
