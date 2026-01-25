"""
Analytics Service
Weekly check-ins and nutrition analysis
"""

import os
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from supabase import create_client
from typing import Dict, List
from collections import Counter


class AnalyticsService:
    """
    Weekly check-in analysis and nutrition trends
    """

    def __init__(self):
        load_dotenv()
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )

    async def generate_weekly_analysis(self, phone_number: str, start_date: str = None, end_date: str = None) -> Dict:
        """
        Generate comprehensive weekly nutrition analysis

        Returns:
            {
                'summary': {...},
                'adherence': {...},
                'top_foods': [...],
                'trends': {...},
                'suggestions': [...]
            }
        """
        # Default to last 7 days if dates not provided
        if not end_date:
            end_date = datetime.now().date().isoformat()
        if not start_date:
            start_dt = datetime.fromisoformat(end_date) - timedelta(days=6)
            start_date = start_dt.date().isoformat()

        # Get all daily summaries for the week
        summaries = self.supabase.table('daily_summaries')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .order('date')\
            .execute()

        # Get all food logs for the week
        logs = self.supabase.table('food_logs')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .execute()

        # Get user profile for targets
        profile = self.supabase.table('user_profiles')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .execute()

        if not summaries.data:
            return {'error': 'No data for this week'}

        # Safe numeric helper
        def safe_num(value, default=0):
            try:
                if value is None:
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default

        # Calculate weekly averages
        days_logged = len(summaries.data)
        total_calories = sum(safe_num(s.get('actual_calories')) for s in summaries.data)
        total_protein = sum(safe_num(s.get('actual_protein')) for s in summaries.data)
        total_carbs = sum(safe_num(s.get('actual_carbs')) for s in summaries.data)
        total_fat = sum(safe_num(s.get('actual_fat')) for s in summaries.data)

        avg_calories = total_calories / days_logged if days_logged > 0 else 0
        avg_protein = total_protein / days_logged if days_logged > 0 else 0
        avg_carbs = total_carbs / days_logged if days_logged > 0 else 0
        avg_fat = total_fat / days_logged if days_logged > 0 else 0

        # Calculate adherence
        total_adherence = sum(safe_num(s.get('adherence_score')) for s in summaries.data)
        avg_adherence = total_adherence / days_logged if days_logged > 0 else 0

        # Get targets
        if profile.data:
            target_calories = profile.data[0].get('calories_target', 2500)
            target_protein = profile.data[0].get('protein_target', 150)
        else:
            target_calories = 2500
            target_protein = 150

        # Compare to targets
        calorie_diff = avg_calories - target_calories
        protein_diff = avg_protein - target_protein

        # Analyze most eaten foods
        food_counter = Counter()
        external_count = 0
        planned_count = 0

        for log in logs.data:
            food_counter[log['food_name']] += 1
            if log.get('is_external'):
                external_count += 1
            if log.get('was_planned'):
                planned_count += 1

        top_5_foods = food_counter.most_common(5)
        total_logs = len(logs.data)

        # Identify trends
        trends = []

        # Calorie trend
        if abs(calorie_diff) < 100:
            trends.append("✅ Consistently hitting calorie targets")
        elif calorie_diff > 0:
            trends.append(f"⚠️ Averaging {int(calorie_diff)} cal/day over target")
        else:
            trends.append(f"⚠️ Averaging {int(abs(calorie_diff))} cal/day under target")

        # Protein trend
        if abs(protein_diff) < 10:
            trends.append("✅ Meeting protein goals consistently")
        elif protein_diff < 0:
            trends.append(f"⚠️ Protein is {int(abs(protein_diff))}g/day below target")

        # Adherence trend
        if avg_adherence >= 80:
            trends.append("✅ Excellent plan adherence!")
        elif avg_adherence >= 60:
            trends.append("⚠️ Good adherence, but room for improvement")
        else:
            trends.append("⚠️ Low plan adherence - consider adjusting your meal plans")

        # External food trend
        external_pct = (external_count / total_logs * 100) if total_logs > 0 else 0
        if external_pct > 30:
            trends.append(f"⚠️ {external_pct:.0f}% of meals were off-campus foods")

        # Generate suggestions
        suggestions = []

        if calorie_diff < -300:
            suggestions.append("Consider adding healthy snacks to meet calorie goals")
        if protein_diff < -20:
            suggestions.append("Add more protein-rich foods (eggs, chicken, Greek yogurt)")
        if avg_adherence < 70:
            suggestions.append("Try planning meals that you actually enjoy eating")
        if external_pct > 40:
            suggestions.append("Explore more dining hall options to save money and hit targets")

        # Positive suggestions
        if avg_adherence >= 80:
            suggestions.append("Keep up the great work with meal planning! 💪")
        if abs(calorie_diff) < 100 and abs(protein_diff) < 10:
            suggestions.append("You're crushing your nutrition goals! 🎯")

        return {
            'week_period': f"{start_date} to {end_date}",
            'days_logged': days_logged,
            'summary': {
                'avg_calories': round(avg_calories, 0),
                'avg_protein': round(avg_protein, 1),
                'avg_carbs': round(avg_carbs, 1),
                'avg_fat': round(avg_fat, 1),
                'target_calories': target_calories,
                'target_protein': target_protein,
                'calorie_diff': round(calorie_diff, 0),
                'protein_diff': round(protein_diff, 1)
            },
            'adherence': {
                'avg_adherence_score': round(avg_adherence, 1),
                'planned_meals': planned_count,
                'total_meals': total_logs,
                'external_meals': external_count
            },
            'top_foods': [{'food': food, 'count': count} for food, count in top_5_foods],
            'trends': trends,
            'suggestions': suggestions if suggestions else ['Keep doing what you\'re doing!']
        }

    async def get_daily_streak(self, phone_number: str) -> int:
        """
        Calculate consecutive days of logging

        Returns number of consecutive days user has logged food
        """
        # Get all summaries ordered by date descending
        summaries = self.supabase.table('daily_summaries')\
            .select('date, meals_logged')\
            .eq('phone_number', phone_number)\
            .order('date', desc=True)\
            .execute()

        if not summaries.data:
            return 0

        streak = 0
        current_date = datetime.now().date()

        for summary in summaries.data:
            summary_date = datetime.fromisoformat(summary['date']).date()

            # Check if this date is consecutive
            expected_date = current_date - timedelta(days=streak)

            if summary_date == expected_date and summary.get('meals_logged', 0) > 0:
                streak += 1
            else:
                break

        return streak

    def format_weekly_message(self, analysis: Dict) -> str:
        """
        Format weekly analysis into WhatsApp-friendly message

        Args:
            analysis: Output from generate_weekly_analysis

        Returns:
            Formatted message string
        """
        msg = f"""📊 WEEKLY NUTRITION SUMMARY
{analysis['week_period']}

📈 AVERAGES ({analysis['days_logged']} days)
• Calories: {int(analysis['summary']['avg_calories'])} / {analysis['summary']['target_calories']} target
  ({'+' if analysis['summary']['calorie_diff'] > 0 else ''}{int(analysis['summary']['calorie_diff'])} cal)
• Protein: {analysis['summary']['avg_protein']}g / {analysis['summary']['target_protein']}g target
  ({'+' if analysis['summary']['protein_diff'] > 0 else ''}{analysis['summary']['protein_diff']}g)
• Carbs: {analysis['summary']['avg_carbs']}g
• Fat: {analysis['summary']['avg_fat']}g

✅ ADHERENCE
• Plan adherence: {analysis['adherence']['avg_adherence_score']}%
• Planned meals: {analysis['adherence']['planned_meals']}/{analysis['adherence']['total_meals']}
• Off-campus meals: {analysis['adherence']['external_meals']}

🍽️ TOP 5 FOODS THIS WEEK
"""
        for i, item in enumerate(analysis['top_foods'], 1):
            msg += f"{i}. {item['food']} ({item['count']}x)\n"

        msg += f"\n📊 TRENDS\n"
        for trend in analysis['trends']:
            msg += f"{trend}\n"

        msg += f"\n💡 SUGGESTIONS\n"
        for suggestion in analysis['suggestions']:
            msg += f"• {suggestion}\n"

        return msg
