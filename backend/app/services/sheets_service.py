"""
Google Sheets Service
Syncs food logs to Google Sheets for daily tracking and analysis
"""

import os
from datetime import datetime, date
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from supabase import create_client
from typing import List, Dict


class SheetsService:
    """
    Sync food logs to Google Sheets
    """

    def __init__(self):
        load_dotenv()

        # Google Sheets setup
        self.spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
        self.service = None
        
        try:
            # Try to load from JSON environment variable first (for Railway/production)
            service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            if service_account_json:
                creds_dict = json.loads(service_account_json)
                creds = Credentials.from_service_account_info(
                    creds_dict,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                self.service = build('sheets', 'v4', credentials=creds)
            # Fallback to file path (for local development)
            else:
                service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
                if service_account_file and os.path.exists(service_account_file):
                    creds = Credentials.from_service_account_file(
                        service_account_file,
                        scopes=['https://www.googleapis.com/auth/spreadsheets']
                    )
                    self.service = build('sheets', 'v4', credentials=creds)
        except Exception as e:
            print(f"Warning: Google Sheets credentials error: {e}. Sheets sync will not work.")
            self.service = None

        # Supabase setup
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )

    async def sync_daily_logs(self, phone_number: str, target_date: str = None):
        """
        Push all food logs for a date to Google Sheets

        Creates rows like:
        Date | Meal | Food | Portion | Cal | Protein | Carbs | Fat | Planned? | Notes
        """
        if not self.service:
            print("Google Sheets service not initialized")
            return False

        if not target_date:
            target_date = datetime.now().date().isoformat()

        # Get all logs for date
        logs = self.supabase.table('food_logs')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .eq('date', target_date)\
            .order('logged_at')\
            .execute()

        # Get daily summary
        summary = self.supabase.table('daily_summaries')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .eq('date', target_date)\
            .execute()

        # Format for Google Sheets
        rows = []

        # Add header if sheet is empty (first sync)
        # Note: You may want to check if header exists first

        # Add food log rows
        for log in logs.data:
            rows.append([
                log['date'],
                log['meal_type'],
                log['food_name'],
                log['portion'],
                log['calories'],
                log['protein_g'],
                log['carbs_g'],
                log['fat_g'],
                '✅' if log['was_planned'] else '➕',
                log['notes'] or ''
            ])

        # Add daily summary row
        if summary.data:
            sum_data = summary.data[0]
            rows.append([
                target_date,
                'DAILY TOTAL',
                '',
                '',
                sum_data['actual_calories'],
                sum_data['actual_protein'],
                sum_data['actual_carbs'],
                sum_data['actual_fat'],
                f"{sum_data['adherence_score']:.1f}%",
                sum_data['notes'] or ''
            ])

        # Add blank row for separation
        rows.append(['', '', '', '', '', '', '', '', '', ''])

        try:
            # Append to sheet
            body = {'values': rows}
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Food Log!A:J',  # Adjust range as needed
                valueInputOption='RAW',
                body=body
            ).execute()

            # Mark as synced
            self.supabase.table('daily_summaries')\
                .update({
                    'synced_to_sheets': True,
                    'synced_at': datetime.now().isoformat()
                })\
                .eq('phone_number', phone_number)\
                .eq('date', target_date)\
                .execute()

            print(f"Successfully synced {len(logs.data)} logs to Google Sheets for {target_date}")
            return True

        except Exception as e:
            print(f"Error syncing to Google Sheets: {e}")
            return False

    async def create_weekly_summary(self, phone_number: str, start_date: str, end_date: str):
        """
        Create weekly summary sheet

        Calculates:
        - Avg daily calories, protein, carbs, fat
        - Adherence score
        - Most/least eaten foods
        - Trends
        """
        if not self.service:
            print("Google Sheets service not initialized")
            return False

        # Get all summaries for the week
        summaries = self.supabase.table('daily_summaries')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .execute()

        if not summaries.data:
            return False

        # Calculate weekly averages
        total_days = len(summaries.data)
        avg_calories = sum(s['actual_calories'] or 0 for s in summaries.data) / total_days
        avg_protein = sum(s['actual_protein'] or 0 for s in summaries.data) / total_days
        avg_carbs = sum(s['actual_carbs'] or 0 for s in summaries.data) / total_days
        avg_fat = sum(s['actual_fat'] or 0 for s in summaries.data) / total_days
        avg_adherence = sum(s['adherence_score'] or 0 for s in summaries.data) / total_days

        # Get most eaten foods
        logs = self.supabase.table('food_logs')\
            .select('food_name')\
            .eq('phone_number', phone_number)\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .execute()

        # Count food frequencies
        food_counts = {}
        for log in logs.data:
            food = log['food_name']
            food_counts[food] = food_counts.get(food, 0) + 1

        # Sort by frequency
        sorted_foods = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)
        top_5_foods = sorted_foods[:5]

        # Format weekly summary
        summary_rows = [
            [f'WEEKLY SUMMARY: {start_date} to {end_date}'],
            [''],
            ['Metric', 'Average'],
            ['Daily Calories', f'{avg_calories:.0f}'],
            ['Daily Protein (g)', f'{avg_protein:.1f}'],
            ['Daily Carbs (g)', f'{avg_carbs:.1f}'],
            ['Daily Fat (g)', f'{avg_fat:.1f}'],
            ['Adherence Score', f'{avg_adherence:.1f}%'],
            [''],
            ['Top 5 Most Eaten Foods'],
        ]

        for food, count in top_5_foods:
            summary_rows.append([food, f'{count} times'])

        summary_rows.append([''])

        try:
            # Write to Weekly Summary sheet
            body = {'values': summary_rows}
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Weekly Summary!A:B',
                valueInputOption='RAW',
                body=body
            ).execute()

            print(f"Successfully created weekly summary for {start_date} to {end_date}")
            return True

        except Exception as e:
            print(f"Error creating weekly summary: {e}")
            return False

    def create_food_log_sheet_if_not_exists(self):
        """
        Create Food Log sheet with headers if it doesn't exist
        """
        if not self.service:
            return False

        try:
            # Get existing sheets
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])

            # Check if "Food Log" exists
            food_log_exists = any(s.get('properties', {}).get('title') == 'Food Log' for s in sheets)

            if not food_log_exists:
                # Create new sheet
                requests = [{
                    'addSheet': {
                        'properties': {
                            'title': 'Food Log'
                        }
                    }
                }]

                body = {'requests': requests}
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body=body
                ).execute()

                # Add header row
                header = [['Date', 'Meal', 'Food', 'Portion', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Planned?', 'Notes']]
                body = {'values': header}
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range='Food Log!A1:J1',
                    valueInputOption='RAW',
                    body=body
                ).execute()

                print("Created Food Log sheet with headers")
                return True

        except Exception as e:
            print(f"Error creating Food Log sheet: {e}")
            return False
