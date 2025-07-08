import numpy as np
import pandas as pd
import json
import re

class clean_data:
    # Load the data
    data = pd.read_json("food_items_breakfast.json")
    df = data.copy()

    # Your existing cleaning steps
    df['nutritional_info'] = df["nutritional_info"].str.replace("\n"," ").str.replace("Close","")
    df['nutritional_info'] = df["nutritional_info"].str.replace("Daily Value*","")
    df['nutritional_info'] = df['nutritional_info'].str.replace('* The % Daily Value (DV) tells you how much a nutrient in a serving of food contributes to a daily diet. 2,000 calories a day is used for general nutrition advice. ','')
    df['nutritional_info'] = df['nutritional_info'].str.replace("^","")


    def remove_capitalized_food_name(text):
        # Split by spaces and remove the first all-caps words
        words = text.split()
        # Find where the capitalized food name ends (usually 1-3 words)
        start_index = 0
        for i, word in enumerate(words):
            if word.isupper() and not any(char.isdigit() for char in word):
                start_index = i + 1
            else:
                break
        # Return text without the capitalized food name
        return ' '.join(words[start_index:])

    df['nutritional_info'] = df['nutritional_info'].apply(remove_capitalized_food_name)

    df['nutritional_info'] = df['nutritional_info'].str.replace(r'\s+', ' ', regex=True)  # Multiple spaces to single space
    df['nutritional_info'] = df['nutritional_info'].str.replace('% ', '', regex=False)  # Remove remaining %
    df['nutritional_info'] = df['nutritional_info'].str.strip()  # Remove leading/trailing spaces

    def format_with_pipes(text):
        
        patterns = [
            (r'Calories (\d+) kcal', r'Calories: \1 kcal'),
            (r'Protein \(g\) ([\d.]+) g', r'Protein: \1 g'),
            (r'Total Carbohydrates \(g\) ([\d.]+|less than \d+ gram) g', r'Total Carbohydrates: \1 g'),
            (r'Sugar \(g\) ([\d.]+|less than \d+ gram) g', r'Sugar: \1 g'),
            (r'Total Fat \(g\) ([\d.]+) g', r'Total Fat: \1 g'),
            (r'Saturated Fat \(g\) ([\d.]+) g', r'Saturated Fat: \1 g'),
            (r'Cholesterol \(mg\) ([\d.]+|less than \d+ milligrams) mg', r'Cholesterol: \1 mg'),
            (r'Dietary Fiber \(g\) ([\d.]+|less than \d+ gram) g', r'Dietary Fiber: \1 g'),
            (r'Sodium \(mg\) ([\d.]+) mg', r'Sodium: \1 mg'),
            (r'Potassium \(mg\) ([\d.]+|-) mg', r'Potassium: \1 mg'),
            (r'Calcium \(mg\) ([\d.]+) mg', r'Calcium: \1 mg'),
            (r'Iron \(mg\) ([\d.]+) mg', r'Iron: \1 mg'),
            (r'Trans Fat \(g\) ([\d.]+) g', r'Trans Fat: \1 g'),
            (r'Vitamin D \(IU\) ([\d.]+\+?|0\+?|-) IU', r'Vitamin D: \1 IU'),
            (r'Vitamin C \(mg\) ([\d.]+\+?|0\+?|-) mg', r'Vitamin C: \1 mg'),
            (r'Vitamin A \(RE\) ([\d.]+|-) RE', r'Vitamin A: \1 RE'),
        ]
        
        # Apply all pattern replacements
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Add pipes between different nutrients
        # Split by known nutrient patterns and rejoin with pipes
        nutrients = re.split(r'(?=(?:Calories|Protein|Total Carbohydrates|Sugar|Total Fat|Saturated Fat|Cholesterol|Dietary Fiber|Sodium|Potassium|Calcium|Iron|Trans Fat|Vitamin [A-Z]|Serving size|Allergens):)', text)
        
        # Clean up and filter out empty strings
        nutrients = [nutrient.strip() for nutrient in nutrients if nutrient.strip()]
        
        # Join with pipe separators
        return ' | '.join(nutrients)

    df['nutritional_info'] = df['nutritional_info'].apply(format_with_pipes)

    df['nutritional_info'] = df['nutritional_info'].str.replace(r'\s*\|\s*', ' | ', regex=True)  # Standardize pipe spacing
    df['nutritional_info'] = df['nutritional_info'].str.replace('Calories From Fat.*?(?=\||$)', '', regex=True)  # Remove "Calories From Fat"
    df['nutritional_info'] = df['nutritional_info'].str.replace('Saturated Fat \+ Trans Fat.*?(?=\||$)', '', regex=True)  # Remove combined fat info

    # Save the cleaned data
    df.to_json('backend/app/data/cleaned_data/cleaned_food_items_breakfast.json', orient='records', indent=2)
    print(f"\nSaved cleaned data to: backend/app/data/cleaned_data/cleaned_food_items_breakfast.json")