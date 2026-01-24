"""
Food Parser Utility
Extracts food items and portions from natural language text
"""

import re
from typing import List, Dict, Optional


class FoodParser:
    """Parse food items from natural language user messages"""

    # Common portion indicators
    PORTION_PATTERNS = [
        r'(\d+(?:\.\d+)?)\s*(eggs?|pieces?|cups?|bowls?|slices?|servings?|oz|ounces?|grams?|g|lbs?|pounds?)',
        r'(a|an|one|two|three|four|five|six|seven|eight|nine|ten)\s+(egg|piece|cup|bowl|slice|serving)',
        r'(small|medium|large|big|huge)\s+(bag|bowl|plate|portion|serving)',
        r'(half|quarter)\s+(cup|bowl|plate|bag)',
    ]

    # Common food verbs
    FOOD_VERBS = [
        'ate', 'had', 'eating', 'having', 'consumed', 'finished',
        'grabbed', 'got', 'took', 'tried', 'tasted'
    ]

    # Common conjunctions
    FOOD_CONJUNCTIONS = ['and', 'with', 'plus', ',']

    @staticmethod
    def extract_foods(text: str) -> List[Dict[str, any]]:
        """
        Extract food items and portions from natural language text

        Args:
            text: User message like "ate 3 eggs and toast" or "had some chips"

        Returns:
            List of dicts with 'food', 'portion', 'quantity' keys

        Examples:
            >>> FoodParser.extract_foods("ate 3 eggs and toast")
            [
                {'food': 'eggs', 'portion': '3 eggs', 'quantity': 3},
                {'food': 'toast', 'portion': 'some', 'quantity': None}
            ]

            >>> FoodParser.extract_foods("had a large bowl of pasta")
            [{'food': 'pasta', 'portion': 'large bowl', 'quantity': 1}]
        """
        text = text.lower().strip()

        # Remove food verbs to simplify parsing
        for verb in FoodParser.FOOD_VERBS:
            text = text.replace(f"{verb} ", "")

        # Split by conjunctions to get individual food items
        # Replace conjunctions with a delimiter
        for conj in FoodParser.FOOD_CONJUNCTIONS:
            text = text.replace(f" {conj} ", " |SPLIT| ")

        # Split into parts
        parts = [p.strip() for p in text.split("|SPLIT|") if p.strip()]

        foods = []
        for part in parts:
            # Try to extract portion and food name
            portion_match = None
            quantity = None

            # Try each portion pattern
            for pattern in FoodParser.PORTION_PATTERNS:
                match = re.search(pattern, part, re.IGNORECASE)
                if match:
                    portion_match = match.group(0)
                    # Extract quantity if it's numeric
                    qty_match = re.search(r'(\d+(?:\.\d+)?)', portion_match)
                    if qty_match:
                        quantity = float(qty_match.group(1))
                    break

            # Extract food name (everything after portion, or whole part if no portion)
            if portion_match:
                # Food is what comes after the portion indicator
                food_name = part.replace(portion_match, "").strip()
                # Also clean up leading 'of' if present
                food_name = re.sub(r'^of\s+', '', food_name)
            else:
                # No portion found, whole part is food name
                food_name = part
                portion_match = "some"  # default portion

            # Clean up food name
            food_name = food_name.strip()

            if food_name:
                foods.append({
                    'food': food_name,
                    'portion': portion_match if portion_match else 'some',
                    'quantity': quantity
                })

        return foods

    @staticmethod
    def normalize_portion(portion: str, quantity: float = None) -> str:
        """
        Normalize portion descriptions

        Args:
            portion: Original portion string
            quantity: Numeric quantity if available

        Returns:
            Normalized portion string

        Examples:
            >>> FoodParser.normalize_portion("3 eggs", 3)
            "3 servings"

            >>> FoodParser.normalize_portion("large bowl")
            "1.5 cups"
        """
        portion = portion.lower().strip()

        # Size to multiplier mapping
        size_multipliers = {
            'small': 0.75,
            'medium': 1.0,
            'large': 1.5,
            'big': 1.5,
            'huge': 2.0
        }

        # If it's a size descriptor, convert to estimated serving
        for size, multiplier in size_multipliers.items():
            if size in portion:
                if 'bowl' in portion or 'plate' in portion:
                    return f"{multiplier} cups"
                elif 'bag' in portion:
                    return f"{multiplier} oz"
                elif 'serving' in portion or 'portion' in portion:
                    return f"{multiplier} servings"

        # If already has a quantity and unit, return as-is
        if quantity and any(unit in portion for unit in ['cup', 'oz', 'gram', 'lb', 'serving', 'piece', 'egg', 'slice']):
            return portion

        # Default
        return portion if portion else "1 serving"

    @staticmethod
    def detect_meal_type(text: str, hour: int = None) -> str:
        """
        Detect meal type from context

        Args:
            text: User message
            hour: Hour of day (0-23), defaults to current hour

        Returns:
            "breakfast", "lunch", "dinner", or "snack"
        """
        text = text.lower()

        # Explicit meal mentions
        if any(word in text for word in ['breakfast', 'morning', 'brunch']):
            return 'breakfast'
        if any(word in text for word in ['lunch', 'noon', 'midday']):
            return 'lunch'
        if any(word in text for word in ['dinner', 'supper', 'evening']):
            return 'dinner'
        if 'snack' in text:
            return 'snack'

        # Use time-based detection if no explicit mention
        if hour is None:
            from datetime import datetime
            hour = datetime.now().hour

        if 5 <= hour < 11:
            return 'breakfast'
        elif 11 <= hour < 15:
            return 'lunch'
        elif 15 <= hour < 18:
            return 'snack'
        elif 18 <= hour < 23:
            return 'dinner'
        else:
            return 'snack'

    @staticmethod
    def is_logging_message(text: str) -> bool:
        """
        Determine if message is about logging food (vs asking questions)

        Args:
            text: User message

        Returns:
            True if message is logging food, False if it's a question

        Examples:
            >>> FoodParser.is_logging_message("ate 3 eggs")
            True

            >>> FoodParser.is_logging_message("what should I eat for lunch?")
            False
        """
        text = text.lower()

        # Question indicators
        question_words = ['what', 'should', 'can', 'could', 'would', 'how', 'when', 'where', 'why', '?']
        if any(word in text for word in question_words):
            return False

        # Food logging indicators
        logging_verbs = ['ate', 'had', 'eating', 'having', 'consumed', 'finished', 'grabbed', 'got', 'took']
        if any(verb in text for verb in logging_verbs):
            return True

        # Default to False (safer to ask than to assume)
        return False
