"""
Date Parser Utility
Parses natural language date references like "tomorrow", "1/24", "next Monday"
"""

from datetime import datetime, timedelta
from dateutil import parser
import re


class DateParser:
    """Parse natural language dates for meal planning"""

    @staticmethod
    def parse_date(date_string: str) -> datetime:
        """
        Parse various date formats into datetime object

        Supports:
        - "today" -> today's date
        - "tomorrow" -> tomorrow's date
        - "1/24" or "01/24" -> January 24 of current year
        - "january 24" -> January 24
        - "next monday" -> next Monday
        - "monday" -> this coming Monday

        Args:
            date_string: Natural language date string

        Returns:
            datetime object

        Examples:
            >>> DateParser.parse_date("tomorrow")
            datetime.datetime(2025, 1, 24, 0, 0)

            >>> DateParser.parse_date("1/24")
            datetime.datetime(2025, 1, 24, 0, 0)
        """
        date_string = date_string.lower().strip()
        today = datetime.now()

        # Handle "today"
        if date_string == "today":
            return today

        # Handle "tomorrow"
        if date_string == "tomorrow":
            return today + timedelta(days=1)

        # Handle "yesterday"
        if date_string == "yesterday":
            return today - timedelta(days=1)

        # Handle day names (monday, tuesday, etc.)
        weekdays = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1, 'tues': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3, 'thurs': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }

        for day_name, day_num in weekdays.items():
            if day_name in date_string:
                days_ahead = day_num - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                return today + timedelta(days=days_ahead)

        # Handle "next <day>"
        if date_string.startswith("next "):
            day_part = date_string.replace("next ", "")
            return DateParser.parse_date(day_part) + timedelta(days=7)

        # Try parsing with dateutil (handles most formats)
        try:
            return parser.parse(date_string, default=today)
        except:
            # If all else fails, return today
            return today

    @staticmethod
    def get_meal_time_context() -> str:
        """
        Get current meal time context based on time of day

        Returns:
            "breakfast", "lunch", "dinner", or "snack"

        Examples:
            >>> DateParser.get_meal_time_context()  # at 7:30 AM
            "breakfast"
        """
        hour = datetime.now().hour

        if 5 <= hour < 11:
            return "breakfast"
        elif 11 <= hour < 15:
            return "lunch"
        elif 15 <= hour < 18:
            return "snack"
        elif 18 <= hour < 23:
            return "dinner"
        else:
            return "snack"

    @staticmethod
    def is_weekend(date: datetime = None) -> bool:
        """
        Check if date is weekend (Saturday or Sunday)

        Args:
            date: datetime object (defaults to today)

        Returns:
            True if weekend, False otherwise
        """
        if date is None:
            date = datetime.now()
        return date.weekday() >= 5  # 5=Saturday, 6=Sunday

    @staticmethod
    def get_week_range(date: datetime = None) -> tuple:
        """
        Get start and end dates for the week containing the given date

        Args:
            date: datetime object (defaults to today)

        Returns:
            Tuple of (start_date, end_date) for the week (Monday-Sunday)
        """
        if date is None:
            date = datetime.now()

        # Get Monday of current week
        start = date - timedelta(days=date.weekday())
        # Get Sunday of current week
        end = start + timedelta(days=6)

        return (start, end)
