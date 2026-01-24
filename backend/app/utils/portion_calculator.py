"""
Portion Calculator Utility
Scales nutrition values based on portions
"""

from typing import Dict, Optional
import re


class PortionCalculator:
    """Calculate nutrition values for different portions"""

    # Standard conversion factors
    CONVERSIONS = {
        # Volume
        'cup': 1.0,
        'cups': 1.0,
        'tablespoon': 0.0625,  # 1/16 cup
        'tablespoons': 0.0625,
        'tbsp': 0.0625,
        'teaspoon': 0.0208,  # 1/48 cup
        'teaspoons': 0.0208,
        'tsp': 0.0208,

        # Weight
        'oz': 1.0,
        'ounce': 1.0,
        'ounces': 1.0,
        'lb': 16.0,  # 16 oz per lb
        'lbs': 16.0,
        'pound': 16.0,
        'pounds': 16.0,
        'gram': 0.035274,  # oz
        'grams': 0.035274,
        'g': 0.035274,
        'kg': 35.274,

        # Count
        'piece': 1.0,
        'pieces': 1.0,
        'slice': 1.0,
        'slices': 1.0,
        'serving': 1.0,
        'servings': 1.0,
        'egg': 1.0,
        'eggs': 1.0,
    }

    @staticmethod
    def extract_quantity(portion_str: str) -> float:
        """
        Extract numeric quantity from portion string

        Args:
            portion_str: Portion description like "3 eggs", "1.5 cups", "half cup"

        Returns:
            Numeric quantity

        Examples:
            >>> PortionCalculator.extract_quantity("3 eggs")
            3.0

            >>> PortionCalculator.extract_quantity("half cup")
            0.5
        """
        portion_str = portion_str.lower().strip()

        # Handle fractions written as words
        fraction_map = {
            'half': 0.5,
            'quarter': 0.25,
            'third': 0.33,
            'one': 1.0,
            'two': 2.0,
            'three': 3.0,
            'four': 4.0,
            'five': 5.0,
            'six': 6.0,
            'seven': 7.0,
            'eight': 8.0,
            'nine': 9.0,
            'ten': 10.0
        }

        for word, value in fraction_map.items():
            if portion_str.startswith(word):
                return value

        # Handle "a" or "an" as 1
        if portion_str.startswith('a ') or portion_str.startswith('an '):
            return 1.0

        # Extract first number (handles "3", "1.5", etc.)
        match = re.search(r'(\d+(?:\.\d+)?)', portion_str)
        if match:
            return float(match.group(1))

        # Default to 1 if no number found
        return 1.0

    @staticmethod
    def scale_nutrition(
        base_nutrition: Dict[str, float],
        base_serving: str,
        target_portion: str,
        quantity_multiplier: float = None
    ) -> Dict[str, float]:
        """
        Scale nutrition values from base serving to target portion

        Args:
            base_nutrition: Dict with nutrition values (calories, protein_g, etc.)
            base_serving: Base serving size from menu (e.g., "1 egg", "100g")
            target_portion: Target portion (e.g., "3 eggs", "250g")
            quantity_multiplier: Optional manual multiplier (overrides calculation)

        Returns:
            Scaled nutrition dict

        Examples:
            >>> base = {'calories': 70, 'protein_g': 6, 'fat_g': 5}
            >>> PortionCalculator.scale_nutrition(base, "1 egg", "3 eggs")
            {'calories': 210, 'protein_g': 18, 'fat_g': 15}
        """
        # If manual multiplier provided, use it
        if quantity_multiplier is not None:
            multiplier = quantity_multiplier
        else:
            # Calculate multiplier from portions
            base_qty = PortionCalculator.extract_quantity(base_serving)
            target_qty = PortionCalculator.extract_quantity(target_portion)
            multiplier = target_qty / base_qty if base_qty > 0 else 1.0

        # Scale all nutrition values
        scaled = {}
        for key, value in base_nutrition.items():
            if value is not None and isinstance(value, (int, float)):
                scaled[key] = round(value * multiplier, 2)
            else:
                scaled[key] = value

        return scaled

    @staticmethod
    def calculate_portion_math(
        base_serving: str,
        target_portion: str,
        base_calories: float,
        base_protein: float
    ) -> str:
        """
        Generate human-readable portion calculation explanation

        Args:
            base_serving: Base serving from menu
            target_portion: Recommended portion
            base_calories: Calories per base serving
            base_protein: Protein per base serving

        Returns:
            Human-readable math explanation

        Examples:
            >>> PortionCalculator.calculate_portion_math("1 egg", "3 eggs", 70, 6)
            "3 servings × 70 cal = 210 cal, 3 × 6g protein = 18g protein"
        """
        base_qty = PortionCalculator.extract_quantity(base_serving)
        target_qty = PortionCalculator.extract_quantity(target_portion)
        multiplier = target_qty / base_qty if base_qty > 0 else 1.0

        total_cal = base_calories * multiplier
        total_protein = base_protein * multiplier

        return (
            f"{multiplier:.1f} servings × {base_calories:.0f} cal = {total_cal:.0f} cal, "
            f"{multiplier:.1f} × {base_protein:.1f}g protein = {total_protein:.1f}g protein"
        )

    @staticmethod
    def estimate_portion_from_description(description: str) -> Dict[str, any]:
        """
        Estimate portion size from vague descriptions

        Args:
            description: Vague portion like "some chips", "a lot of rice"

        Returns:
            Dict with estimated quantity and unit

        Examples:
            >>> PortionCalculator.estimate_portion_from_description("some chips")
            {'quantity': 1.0, 'unit': 'oz', 'description': '1 small bag'}
        """
        description = description.lower().strip()

        # Size indicators
        if any(word in description for word in ['some', 'a little', 'a bit']):
            return {'quantity': 1.0, 'unit': 'serving', 'description': '1 small serving'}

        if any(word in description for word in ['a lot', 'lots', 'bunch', 'many']):
            return {'quantity': 2.0, 'unit': 'servings', 'description': '2 large servings'}

        if 'handful' in description:
            return {'quantity': 0.25, 'unit': 'cup', 'description': '1 handful (~1/4 cup)'}

        # Default to 1 serving
        return {'quantity': 1.0, 'unit': 'serving', 'description': '1 serving'}
