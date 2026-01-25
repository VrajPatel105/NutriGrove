import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import Dict, List


class CalendarService:
    """
    Google Calendar integration for meal planning
    """

    def __init__(self):
        load_dotenv()

        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.service = None
        
        try:
            # Try to load from JSON environment variable first (for Railway/production)
            service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            if service_account_json:
                creds_dict = json.loads(service_account_json)
                creds = Credentials.from_service_account_info(
                    creds_dict,
                    scopes=['https://www.googleapis.com/auth/calendar']
                )
                self.service = build('calendar', 'v3', credentials=creds)
            # Fallback to file path (for local development)
            else:
                service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
                if service_account_file and os.path.exists(service_account_file):
                    creds = Credentials.from_service_account_file(
                        service_account_file,
                        scopes=['https://www.googleapis.com/auth/calendar']
                    )
                    self.service = build('calendar', 'v3', credentials=creds)
        except Exception as e:
            print(f"Warning: Google Calendar credentials error: {e}. Calendar features will not work.")
            self.service = None

    async def add_meal_plan_to_calendar(self, meal_plan: Dict, target_date: str):
        """
        Add daily meal plan to Google Calendar

        Creates calendar events for:
        - Breakfast (7:30 AM)
        - Lunch (12:00 PM)
        - Dinner (6:00 PM)

        Args:
            meal_plan: Complete meal plan dict
            target_date: Date in YYYY-MM-DD format
        """
        if not self.service:
            print("Google Calendar service not initialized")
            return False

        # Parse target date
        date_obj = datetime.fromisoformat(target_date)

        # Meal times
        meal_times = {
            'breakfast': {'hour': 7, 'minute': 30},
            'lunch': {'hour': 12, 'minute': 0},
            'dinner': {'hour': 18, 'minute': 0}
        }

        events_created = []

        for meal_type, time_info in meal_times.items():
            if meal_type not in meal_plan:
                continue

            # Create event time
            start_time = date_obj.replace(
                hour=time_info['hour'],
                minute=time_info['minute'],
                second=0,
                microsecond=0
            )
            end_time = start_time + timedelta(minutes=45)  # 45 min for meal

            # Format meal description
            foods = meal_plan[meal_type]
            description_lines = [f"{meal_type.upper()} PLAN\n"]

            for food in foods:
                description_lines.append(
                    f"• {food['name']} - {food['recommended_portion']}\n"
                    f"  {food['calories']} cal, {food['protein_g']}g protein"
                )

            # Add totals - handle None values safely
            def safe_num(value, default=0):
                try:
                    if value is None:
                        return default
                    return float(value)
                except (ValueError, TypeError):
                    return default

            total_cal = sum(safe_num(f.get('calories')) for f in foods)
            total_protein = sum(safe_num(f.get('protein_g')) for f in foods)
            description_lines.append(f"\nTotal: {total_cal} cal, {total_protein}g protein")

            description = '\n'.join(description_lines)

            # Create calendar event
            event = {
                'summary': f'🍽️ {meal_type.capitalize()} - {total_cal} cal',
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/New_York',  # Adjust timezone
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'colorId': '9',  # Blue color
            }

            try:
                created_event = self.service.events().insert(
                    calendarId=self.calendar_id,
                    body=event
                ).execute()

                events_created.append(created_event['id'])
                print(f"Created calendar event for {meal_type}: {created_event.get('htmlLink')}")

            except Exception as e:
                print(f"Error creating calendar event for {meal_type}: {e}")

        return len(events_created) > 0

    async def add_reminder(self, title: str, description: str, reminder_time: datetime):
        """
        Add a reminder to calendar

        Args:
            title: Reminder title
            description: Reminder description
            reminder_time: When to show reminder
        """
        if not self.service:
            return False

        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': reminder_time.isoformat(),
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': (reminder_time + timedelta(minutes=15)).isoformat(),
                'timeZone': 'America/New_York',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 0},
                ],
            },
        }

        try:
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            print(f"Created reminder: {created_event.get('htmlLink')}")
            return True
        except Exception as e:
            print(f"Error creating reminder: {e}")
            return False
