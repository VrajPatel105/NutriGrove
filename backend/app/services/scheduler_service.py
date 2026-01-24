"""
Scheduler Service
Handles all scheduled tasks:
- 7 AM: Generate and send daily meal plan
- 9 PM: Sync to Google Sheets
- Sunday 8 PM: Weekly check-in
- Hourly: Check for reminders
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from supabase import create_client

from .whatsapp_handler import WhatsAppHandler
from .sheets_service import SheetsService
from .reminder_service import ReminderService
from .analytics_service import AnalyticsService
from ..ai_food_recommendation import FoodRecommender


class SchedulerService:
    """
    Handles all scheduled tasks:
    - 7 AM: Generate and send daily meal plan
    - 9 PM: Sync to Google Sheets
    - Sunday 8 PM: Weekly check-in
    - Hourly: Check for reminders
    """

    def __init__(self):
        load_dotenv()
        self.scheduler = AsyncIOScheduler(timezone='America/New_York')  # Adjust timezone
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )

        # Initialize services
        self.whatsapp = WhatsAppHandler()
        self.sheets = SheetsService()
        self.reminder = ReminderService()
        self.analytics = AnalyticsService()
        self.recommender = FoodRecommender()

    def start(self):
        """
        Start all scheduled jobs
        """
        print("Starting Scheduler Service...")

        # 7 AM: Morning meal plan
        self.scheduler.add_job(
            self.send_morning_plans,
            CronTrigger(hour=7, minute=0),
            id='morning_plan',
            name='Send morning meal plans'
        )

        # 9 PM: Evening sync to Google Sheets
        self.scheduler.add_job(
            self.evening_sync,
            CronTrigger(hour=21, minute=0),
            id='evening_sync',
            name='Sync to Google Sheets'
        )

        # Sunday 8 PM: Weekly check-in
        self.scheduler.add_job(
            self.weekly_checkin,
            CronTrigger(day_of_week='sun', hour=20, minute=0),
            id='weekly_checkin',
            name='Weekly nutrition check-in'
        )

        # Every hour: Check reminders
        self.scheduler.add_job(
            self.check_reminders,
            CronTrigger(minute=0),
            id='hourly_reminders',
            name='Check for reminders'
        )

        # Start the scheduler
        self.scheduler.start()
        print("Scheduler started successfully!")
        print("Scheduled jobs:")
        for job in self.scheduler.get_jobs():
            print(f"  - {job.name} (ID: {job.id}) - Next run: {job.next_run_time}")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print("Scheduler stopped")

    async def send_morning_plans(self):
        """
        7 AM Job: Generate and send daily meal plan to all active users
        """
        print(f"[{datetime.now()}] Running morning meal plan job...")

        # Get all user profiles
        users = self.supabase.table('user_profiles').select('*').execute()

        for user in users.data:
            phone_number = user['phone_number']

            try:
                # Generate meal plan using existing FoodRecommender
                user_preferences = {
                    'age': user.get('age'),
                    'gender': user.get('gender'),
                    'weight': user.get('weight'),
                    'height': user.get('height'),
                    'activity_level': user.get('activity_level'),
                    'goal': user.get('goal'),
                    'diet': user.get('diet'),
                    'dietary_restrictions': user.get('dietary_restrictions'),
                    'calories': user.get('calories_target'),
                    'protein': user.get('protein_target'),
                    'comments': '',
                    'allergens': user.get('allergens', []),
                    'dislikes': user.get('dislikes', [])
                }

                meal_plan = self.recommender.get_daily_meal_schedule(user_preferences)

                # Format meal plan for WhatsApp
                message = self.format_meal_plan_message(meal_plan)

                # Send via WhatsApp
                self.whatsapp.send_whatsapp_message(phone_number, message)

                print(f"Sent meal plan to {phone_number}")

            except Exception as e:
                print(f"Error sending meal plan to {phone_number}: {e}")

    async def evening_sync(self):
        """
        9 PM Job: Sync all users' food logs to Google Sheets
        """
        print(f"[{datetime.now()}] Running evening Google Sheets sync...")

        today = datetime.now().date().isoformat()

        # Get all user profiles
        users = self.supabase.table('user_profiles').select('phone_number').execute()

        for user in users.data:
            phone_number = user['phone_number']

            try:
                # Sync to Google Sheets
                await self.sheets.sync_daily_logs(phone_number, today)
                print(f"Synced {phone_number} to Google Sheets")

            except Exception as e:
                print(f"Error syncing {phone_number} to Sheets: {e}")

    async def weekly_checkin(self):
        """
        Sunday 8 PM Job: Send weekly nutrition analysis to all users
        """
        print(f"[{datetime.now()}] Running weekly check-in job...")

        # Get all user profiles
        users = self.supabase.table('user_profiles').select('phone_number').execute()

        # Calculate week range (last 7 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)

        for user in users.data:
            phone_number = user['phone_number']

            try:
                # Generate weekly analysis
                analysis = await self.analytics.generate_weekly_analysis(
                    phone_number,
                    start_date.isoformat(),
                    end_date.isoformat()
                )

                # Format message
                message = self.analytics.format_weekly_message(analysis)

                # Send via WhatsApp
                self.whatsapp.send_whatsapp_message(phone_number, message)

                # Also create weekly summary in Google Sheets
                await self.sheets.create_weekly_summary(
                    phone_number,
                    start_date.isoformat(),
                    end_date.isoformat()
                )

                print(f"Sent weekly check-in to {phone_number}")

            except Exception as e:
                print(f"Error sending weekly check-in to {phone_number}: {e}")

    async def check_reminders(self):
        """
        Hourly Job: Check for reminders based on user behavior
        """
        print(f"[{datetime.now()}] Checking for reminders...")

        # Get all user profiles
        users = self.supabase.table('user_profiles').select('phone_number').execute()

        for user in users.data:
            phone_number = user['phone_number']

            try:
                # Check meal logging reminders
                await self.reminder.check_meal_logging(phone_number)

            except Exception as e:
                print(f"Error checking reminders for {phone_number}: {e}")

    def format_meal_plan_message(self, meal_plan: dict) -> str:
        """
        Format meal plan into WhatsApp-friendly message

        Args:
            meal_plan: Complete meal plan from AI

        Returns:
            Formatted WhatsApp message
        """
        if 'error' in meal_plan:
            return "Sorry, I couldn't generate your meal plan today. Please try again later."

        msg = f"🌅 Good morning! Here's your meal plan for today:\n\n"

        # Breakfast
        if 'breakfast' in meal_plan and meal_plan['breakfast']:
            msg += "🍳 BREAKFAST\n"
            for food in meal_plan['breakfast']:
                msg += f"• {food.get('name')} - {food.get('recommended_portion')}\n"
                msg += f"  {food.get('calories')}cal, {food.get('protein_g')}g protein\n"
            msg += "\n"

        # Lunch
        if 'lunch' in meal_plan and meal_plan['lunch']:
            msg += "🥗 LUNCH\n"
            for food in meal_plan['lunch']:
                msg += f"• {food.get('name')} - {food.get('recommended_portion')}\n"
                msg += f"  {food.get('calories')}cal, {food.get('protein_g')}g protein\n"
            msg += "\n"

        # Dinner
        if 'dinner' in meal_plan and meal_plan['dinner']:
            msg += "🍽️ DINNER\n"
            for food in meal_plan['dinner']:
                msg += f"• {food.get('name')} - {food.get('recommended_portion')}\n"
                msg += f"  {food.get('calories')}cal, {food.get('protein_g')}g protein\n"
            msg += "\n"

        # Daily totals
        if 'daily_totals' in meal_plan:
            totals = meal_plan['daily_totals']
            msg += f"📊 DAILY TOTALS\n"
            msg += f"• {totals.get('total_calories')}cal / {totals.get('calorie_target')}cal target\n"
            msg += f"• {totals.get('total_protein_g')}g protein / {totals.get('protein_target')}g target\n\n"

        msg += "Reply with any questions or to swap foods! 💬"

        return msg

    def run_job_now(self, job_id: str):
        """
        Manually trigger a specific job (for testing)

        Args:
            job_id: ID of the job to run ('morning_plan', 'evening_sync', etc.)
        """
        job = self.scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            print(f"Job {job_id} will run immediately")
        else:
            print(f"Job {job_id} not found")
