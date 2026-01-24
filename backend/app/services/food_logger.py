"""
Food Logger Service
Handles all food logging operations and daily progress tracking
"""

import os
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client
from typing import Dict, Optional
from .menu_service import MenuService
from ..utils.portion_calculator import PortionCalculator


class FoodLogger:
    """
    Handles all food logging operations
    """

    def __init__(self):
        load_dotenv()
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )
        self.menu_service = MenuService()

    async def log_food_item(
        self,
        phone_number: str,
        food_name: str,
        portion: str,
        meal_type: str,
        calories: int = None,
        protein_g: float = None,
        carbs_g: float = None,
        fat_g: float = None,
        fiber_g: float = None,
        sodium_mg: float = None,
        sugar_g: float = None,
        was_planned: bool = False,
        is_external: bool = False,
        notes: str = None
    ) -> Dict:
        """
        Log a food item to database

        If calories/protein not provided, look up from menu or estimate

        Returns:
            Logged entry with calculated totals
        """
        # If nutrition not provided, look it up
        if not calories:
            # Try menu first
            menu_item = await self.menu_service.search_by_name(food_name)

            if menu_item:
                # Calculate based on portion
                base_nutrition = {
                    'calories': menu_item['calories'],
                    'protein_g': menu_item['protein_g'],
                    'carbs_g': menu_item['carbs_g'],
                    'fat_g': menu_item['fat_g'],
                    'fiber_g': menu_item.get('fiber_g', 0),
                    'sodium_mg': menu_item.get('sodium_mg', 0)
                }

                # Scale based on portion
                scaled = PortionCalculator.scale_nutrition(
                    base_nutrition,
                    menu_item.get('serving_size', '1 serving'),
                    portion
                )

                calories = int(scaled['calories'])
                protein_g = scaled['protein_g']
                carbs_g = scaled['carbs_g']
                fat_g = scaled['fat_g']
                fiber_g = scaled.get('fiber_g', 0)
                sodium_mg = scaled.get('sodium_mg', 0)
                is_external = False
            else:
                # External food - mark for AI estimation
                is_external = True
                # Use provided values or defaults
                calories = calories or 0
                protein_g = protein_g or 0
                carbs_g = carbs_g or 0
                fat_g = fat_g or 0

        # Insert into database
        log_entry = {
            'phone_number': phone_number,
            'date': datetime.now().date().isoformat(),
            'meal_type': meal_type,
            'food_name': food_name,
            'portion': portion,
            'calories': calories,
            'protein_g': protein_g,
            'carbs_g': carbs_g,
            'fat_g': fat_g,
            'fiber_g': fiber_g,
            'sodium_mg': sodium_mg,
            'sugar_g': sugar_g,
            'was_planned': was_planned,
            'is_external': is_external,
            'notes': notes
        }

        result = self.supabase.table('food_logs').insert(log_entry).execute()

        # Update daily summary
        await self.update_daily_summary(phone_number)

        return result.data[0] if result.data else log_entry

    async def get_daily_progress(self, phone_number: str, target_date: str = None) -> Dict:
        """
        Calculate current progress vs plan for the day

        Returns:
            {
                'actual': {...},
                'target': {...},
                'remaining': {...},
                'adherence': 85.2
            }
        """
        if not target_date:
            target_date = datetime.now().date().isoformat()

        # Get logged foods for the date
        logs = self.supabase.table('food_logs')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .eq('date', target_date)\
            .execute()

        # Calculate totals
        actual_calories = sum(log['calories'] or 0 for log in logs.data)
        actual_protein = sum(log['protein_g'] or 0 for log in logs.data)
        actual_carbs = sum(log['carbs_g'] or 0 for log in logs.data)
        actual_fat = sum(log['fat_g'] or 0 for log in logs.data)
        actual_fiber = sum(log['fiber_g'] or 0 for log in logs.data)

        # Get user profile for targets
        profile_result = self.supabase.table('user_profiles')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .execute()

        if profile_result.data:
            profile = profile_result.data[0]
            target_calories = profile.get('calories_target', 2500)
            target_protein = profile.get('protein_target', 150)
        else:
            # Default targets
            target_calories = 2500
            target_protein = 150

        # Count planned vs actual
        planned_count = sum(1 for log in logs.data if log.get('was_planned'))
        total_count = len(logs.data)

        # Calculate adherence (what % of plan was followed)
        adherence = (planned_count / total_count * 100) if total_count > 0 else 0

        return {
            'actual': {
                'calories': int(actual_calories),
                'protein': round(actual_protein, 1),
                'carbs': round(actual_carbs, 1),
                'fat': round(actual_fat, 1),
                'fiber': round(actual_fiber, 1)
            },
            'target': {
                'calories': target_calories,
                'protein': target_protein
            },
            'remaining': {
                'calories': target_calories - actual_calories,
                'protein': target_protein - actual_protein
            },
            'meals_logged': total_count,
            'planned_meals_eaten': planned_count,
            'adherence': round(adherence, 1)
        }

    def calculate_adherence(self, logs: list, target_cal: int, target_protein: int) -> float:
        """
        Calculate adherence score (0-100%)
        Based on how close to targets and how many planned foods eaten
        """
        if not logs:
            return 0.0

        # Count planned vs unplanned
        planned_count = sum(1 for log in logs if log.get('was_planned'))
        total_count = len(logs)

        # Simple adherence: % of meals that were from plan
        adherence = (planned_count / total_count) * 100 if total_count > 0 else 0

        return round(adherence, 2)

    async def update_daily_summary(self, phone_number: str, target_date: str = None):
        """
        Update or create daily summary entry
        Called after each food log
        """
        if not target_date:
            target_date = datetime.now().date().isoformat()

        progress = await self.get_daily_progress(phone_number, target_date)

        summary_data = {
            'phone_number': phone_number,
            'date': target_date,
            'actual_calories': progress['actual']['calories'],
            'actual_protein': progress['actual']['protein'],
            'actual_carbs': progress['actual']['carbs'],
            'actual_fat': progress['actual']['fat'],
            'actual_fiber': progress['actual']['fiber'],
            'meals_logged': progress['meals_logged'],
            'adherence_score': progress['adherence']
        }

        # Upsert (insert or update if exists)
        # Check if summary exists
        existing = self.supabase.table('daily_summaries')\
            .select('id')\
            .eq('phone_number', phone_number)\
            .eq('date', target_date)\
            .execute()

        if existing.data:
            # Update existing
            self.supabase.table('daily_summaries')\
                .update(summary_data)\
                .eq('phone_number', phone_number)\
                .eq('date', target_date)\
                .execute()
        else:
            # Insert new
            self.supabase.table('daily_summaries').insert(summary_data).execute()

    async def get_logs_by_date(self, phone_number: str, target_date: str) -> list:
        """Get all food logs for a specific date"""
        result = self.supabase.table('food_logs')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .eq('date', target_date)\
            .order('logged_at')\
            .execute()

        return result.data

    async def delete_log(self, log_id: int) -> bool:
        """Delete a food log entry"""
        try:
            self.supabase.table('food_logs').delete().eq('id', log_id).execute()
            return True
        except:
            return False
