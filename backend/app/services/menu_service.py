"""
Menu Service - Token-Optimized Menu Search
Handles all menu-related operations with smart filtering to minimize token usage
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from typing import List, Dict, Optional
from ..model.schema import MenuSearchParams, FoodItem


class MenuService:
    """
    Handles all menu-related operations with smart filtering
    CRITICAL: Implements token optimization by filtering BEFORE sending to AI
    """

    def __init__(self):
        load_dotenv()
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )

    async def search_menu_minimal(
        self,
        meal_type: str = None,
        min_protein: int = None,
        max_calories: int = None,
        exclude_allergens: List[str] = None,
        station: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search menu with filters - returns MINIMAL data for token efficiency

        This is the KEY function for token optimization:
        - Filter in database FIRST (use Supabase queries)
        - Return only 5-10 relevant items (not 500!)
        - Return only essential fields (not full nutrition breakdown)

        Args:
            meal_type: "breakfast", "lunch", "dinner"
            min_protein: Minimum protein in grams
            max_calories: Maximum calories
            exclude_allergens: List of allergens to avoid
            station: Specific dining station
            limit: Max number of results (default 10)

        Returns:
            List of food items with MINIMAL data:
            [
                {
                    "name": "Chicken Alfredo",
                    "station": "Pasta Station",
                    "meal_type": "lunch",
                    "calories": 900,
                    "protein_g": 45,
                    "carbs_g": 85,
                    "fat_g": 35,
                    "allergens": ["dairy", "gluten"]
                },
                ... (max 10 items)
            ]

        Token usage: ~500-1000 tokens (vs 100k+ for full menu)
        """
        # Start building query - select only minimal fields
        query = self.supabase.table('cleaned_data').select(
            'data'
        )

        # Execute initial query to get data
        result = query.execute()

        # Filter in Python (since Supabase JSONB queries can be complex)
        filtered_items = []

        for row in result.data:
            food_data = row.get('data', {})
            nutrition = food_data.get('nutrition', {})

            # Apply filters
            if meal_type and food_data.get('meal_type', '').lower() != meal_type.lower():
                continue

            if station and food_data.get('station_name', '').lower() != station.lower():
                continue

            # Protein filter
            food_protein = float(nutrition.get('protein_g', 0) or 0)
            if min_protein and food_protein < min_protein:
                continue

            # Calorie filter
            food_calories = int(nutrition.get('calories', 0) or 0)
            if max_calories and food_calories > max_calories:
                continue

            # Allergen filter
            food_allergens = nutrition.get('allergens', []) or []
            if exclude_allergens and any(allergen in food_allergens for allergen in exclude_allergens):
                continue

            # Add minimal item
            filtered_items.append({
                "name": food_data.get('food_name', 'Unknown'),
                "station": food_data.get('station_name', 'Unknown'),
                "meal_type": food_data.get('meal_type', 'Unknown'),
                "calories": food_calories,
                "protein_g": food_protein,
                "carbs_g": float(nutrition.get('carbs_g', 0) or 0),
                "fat_g": float(nutrition.get('fat_g', 0) or 0),
                "allergens": food_allergens
            })

            # Stop once we have enough
            if len(filtered_items) >= limit:
                break

        return filtered_items[:limit]

    async def get_food_details(self, food_name: str) -> Optional[Dict]:
        """
        Get COMPLETE nutrition data for ONE specific food
        Only called when user asks for detailed info

        Args:
            food_name: Name of food to look up

        Returns:
            Complete nutrition breakdown including micronutrients

        Token usage: ~200 tokens for one item
        """
        result = self.supabase.table('cleaned_data')\
            .select('data')\
            .execute()

        # Search for food (case-insensitive partial match)
        for row in result.data:
            food_data = row.get('data', {})
            if food_name.lower() in food_data.get('food_name', '').lower():
                nutrition = food_data.get('nutrition', {})

                return {
                    "name": food_data.get('food_name'),
                    "station": food_data.get('station_name'),
                    "meal_type": food_data.get('meal_type'),
                    "serving_size": nutrition.get('serving_size'),
                    "calories": nutrition.get('calories'),
                    "protein_g": nutrition.get('protein_g'),
                    "carbs_g": nutrition.get('carbs_g'),
                    "fat_g": nutrition.get('fat_g'),
                    "fiber_g": nutrition.get('fiber_g'),
                    "sugar_g": nutrition.get('sugar_g'),
                    "sodium_mg": nutrition.get('sodium_mg'),
                    "saturated_fat_g": nutrition.get('saturated_fat_g'),
                    "trans_fat_g": nutrition.get('trans_fat_g'),
                    "cholesterol_mg": nutrition.get('cholesterol_mg'),
                    "calcium_mg": nutrition.get('calcium_mg'),
                    "iron_mg": nutrition.get('iron_mg'),
                    "potassium_mg": nutrition.get('potassium_mg'),
                    "vitamin_a_re": nutrition.get('vitamin_a_re'),
                    "vitamin_c_mg": nutrition.get('vitamin_c_mg'),
                    "vitamin_d_iu": nutrition.get('vitamin_d_iu'),
                    "ingredients": nutrition.get('ingredients'),
                    "allergens": nutrition.get('allergens', [])
                }

        return None

    async def search_by_name(self, food_name: str) -> Optional[Dict]:
        """
        Quick search for exact food match
        Used when logging food from plan

        Returns: Minimal nutrition data for logging
        """
        result = self.supabase.table('cleaned_data')\
            .select('data')\
            .execute()

        # Search for food (case-insensitive partial match)
        for row in result.data:
            food_data = row.get('data', {})
            if food_name.lower() in food_data.get('food_name', '').lower():
                nutrition = food_data.get('nutrition', {})

                return {
                    "name": food_data.get('food_name'),
                    "calories": int(nutrition.get('calories', 0) or 0),
                    "protein_g": float(nutrition.get('protein_g', 0) or 0),
                    "carbs_g": float(nutrition.get('carbs_g', 0) or 0),
                    "fat_g": float(nutrition.get('fat_g', 0) or 0),
                    "fiber_g": float(nutrition.get('fiber_g', 0) or 0),
                    "sodium_mg": float(nutrition.get('sodium_mg', 0) or 0),
                    "serving_size": nutrition.get('serving_size', '1 serving')
                }

        return None

    async def get_all_stations(self) -> List[str]:
        """Get list of all dining stations"""
        result = self.supabase.table('cleaned_data')\
            .select('data')\
            .execute()

        stations = set()
        for row in result.data:
            food_data = row.get('data', {})
            station = food_data.get('station_name')
            if station:
                stations.add(station)

        return sorted(list(stations))
