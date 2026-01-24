"""
Reminder Service
Smart reminders based on user behavior
"""

import os
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client
from .whatsapp_handler import WhatsAppHandler
from .food_logger import FoodLogger


class ReminderService:
    """
    Smart reminders based on user behavior
    """

    def __init__(self):
        load_dotenv()
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )
        self.whatsapp = WhatsAppHandler()
        self.food_logger = FoodLogger()

    async def check_meal_logging(self, phone_number: str):
        """
        Check if user has logged meals
        Send gentle reminders if not

        Called periodically (e.g., every hour during meal times)
        """
        now = datetime.now()
        today = now.date().isoformat()
        hour = now.hour

        # Get today's logs
        logs = self.supabase.table('food_logs')\
            .select('meal_type')\
            .eq('phone_number', phone_number)\
            .eq('date', today)\
            .execute()

        logged_meals = [log['meal_type'] for log in logs.data]

        # Check based on time of day
        if hour == 12 and 'lunch' not in logged_meals:
            # 12 PM and no lunch logged
            message = "Hey! Did you eat lunch? 🥗\n\nJust reply with what you ate, or say 'skip' if you haven't eaten yet."
            self.whatsapp.send_whatsapp_message(phone_number, message)

        elif hour == 20:  # 8 PM
            # Check if under target
            progress = await self.food_logger.get_daily_progress(phone_number)

            if progress['remaining']['calories'] > 500:
                message = (
                    f"You're {progress['remaining']['calories']} cal short of your goal today. 📊\n\n"
                    f"Want a snack suggestion to hit your target? 🍎\n"
                    f"Or are you done eating for the day?"
                )
                self.whatsapp.send_whatsapp_message(phone_number, message)

    async def send_plan_confirmation_reminder(self, phone_number: str):
        """
        Remind user to confirm morning plan if not done by 8 AM
        """
        # Check conversation state
        context = self.supabase.table('conversation_state')\
            .select('context_data')\
            .eq('phone_number', phone_number)\
            .execute()

        if context.data:
            context_data = context.data[0].get('context_data', {})
            plan_sent = context_data.get('plan_sent_today', False)
            plan_confirmed = context_data.get('plan_confirmed', False)

            if plan_sent and not plan_confirmed:
                message = "Good morning! 🌅\n\nI sent you today's meal plan earlier. Did you get a chance to review it?"
                self.whatsapp.send_whatsapp_message(phone_number, message)

    async def send_weekly_checkin_reminder(self, phone_number: str):
        """
        Remind user about weekly check-in
        Sent on Sunday evening
        """
        message = (
            "📊 Weekly Check-In Time!\n\n"
            "Let's review your nutrition this week. "
            "Reply 'weekly' to see your stats and get insights!"
        )
        self.whatsapp.send_whatsapp_message(phone_number, message)

    async def send_custom_reminder(self, phone_number: str, message: str):
        """
        Send a custom reminder message
        """
        self.whatsapp.send_whatsapp_message(phone_number, message)
