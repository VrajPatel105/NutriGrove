"""
VRAJ'S COMPLETE HEALTH PROFILE
Hardcoded health context for AI nutrition coaching system
Last Updated: January 2026
"""

VRAJ_HEALTH_PROFILE = {
    "personal_info": {
        "age": 21,
        "gender": "male",
        "current_weight_lbs": 139,  # 63kg
        "target_weight_lbs": 154,   # 70kg
        "height_cm": 170,
        "goal": "lean_muscle_gain",
        "target_date": "December 2026",
        "activity_level": "active_runner",
        "running_pace_current": "sub-6 min/km",
        "education": "UMass Dartmouth CS student, graduating Spring 2027"
    },

    "blood_work_results": {
        "test_date": "January 2026",
        "glucose_fasting": {
            "value": 106.2,
            "unit": "mg/dL",
            "status": "borderline_high",
            "normal_range": "70-99 mg/dL",
            "concern_level": "moderate",
            "action_required": "glucose management protocol required"
        },
        "vitamin_d": {
            "status": "deficient",
            "action_required": "supplementation started"
        },
        "vitamin_b12": {
            "status": "suboptimal",
            "action_required": "supplementation started"
        },
        "overall_assessment": "Borderline prediabetic glucose levels requiring dietary intervention and monitoring. Vitamin deficiencies addressed through supplementation."
    },

    "health_conditions": {
        "glucose_management": {
            "priority": "HIGH",
            "current_glucose": 106.2,
            "target_glucose": "<100 mg/dL",
            "next_retest": "April 2026",
            "risk_level": "borderline_prediabetic",
            "interventions_required": [
                "Meal sequencing (veggies → protein → carbs → treats)",
                "Post-meal walks (10-15 min after high-carb meals)",
                "Limit simple carbs, prioritize complex carbs",
                "Fiber intake with every meal",
                "Protein before carbs to slow glucose spike",
                "Monitor pizza intake strictly (max 2-3x/week, post-workout only)",
                "Hydration: 3-4 liters water daily"
            ]
        }
    },

    "nutrition_targets": {
        "daily_calories": 2800,
        "protein_g": 150,
        "protein_range": "140-175g",
        "carbs_priority": "complex carbs, high fiber",
        "glucose_management": "CRITICAL - always consider glucose impact",

        "meal_breakdown": {
            "breakfast": {"time": "7:45 AM", "calories": 700, "protein_g": 50},
            "lunch": {"time": "12:00 PM", "calories": 750, "protein_g": 40},
            "snack_1": {"time": "3:00 PM", "calories": 350, "protein_g": 20},
            "dinner": {"time": "6:00 PM", "calories": 750, "protein_g": 40},
            "snack_2": {"time": "8:30 PM", "calories": 250, "protein_g": 25}
        }
    },

    "dietary_rules": {
        "CRITICAL_GLUCOSE_MANAGEMENT": {
            "meal_sequencing": {
                "rule": "ALWAYS eat in this order: Vegetables → Protein → Carbs → Treats",
                "impact": "Reduces glucose spike by 30-40%",
                "exceptions": "NONE - this is mandatory for every meal"
            },
            "post_meal_activity": {
                "rule": "Walk 10-15 minutes after high-carb meals",
                "especially_after": ["pizza", "pasta", "rice-heavy meals"],
                "benefit": "Significantly reduces glucose spike"
            },
            "carb_timing": {
                "best_times": ["post-workout", "lunch on training days"],
                "worst_times": ["late night", "when sedentary", "before bed"],
                "reason": "Insulin sensitivity highest post-workout"
            },
            "fiber_strategy": {
                "requirements": [
                    "Add chia seeds to morning shake",
                    "Eat vegetables FIRST at every meal",
                    "Choose brown rice over white rice",
                    "Include beans/lentils daily (high fiber + protein)"
                ]
            },
            "protein_buffer": {
                "rule": "25-35g protein per meal, eaten BEFORE carbs",
                "benefit": "Slows carb absorption, reduces glucose spike"
            }
        },

        "pizza_protocol": {
            "frequency": "Maximum 2-3 times per week",
            "timing": "ONLY on workout days (Monday/Wednesday/Friday)",
            "condition": "ONLY post-workout (within 2 hours)",
            "portion": "Maximum 3-4 slices",
            "mandatory_pairing": "Always with large salad eaten FIRST",
            "post_pizza": "10-15 minute walk immediately after",
            "rationale": "Glucose is 106.2 (borderline). Pizza spikes glucose significantly. Post-workout timing + walking + salad first = damage control."
        },

        "smart_carb_hierarchy": {
            "best": ["brown rice", "quinoa", "beans", "lentils", "chickpeas", "whole wheat"],
            "moderate": ["white rice (small portions)", "whole wheat pasta", "oatmeal"],
            "limit": ["white bread", "pastries", "sugary foods"],
            "avoid": ["soda", "candy", "processed sweets"]
        },

        "hydration": {
            "daily_target": "3-4 liters water",
            "importance": "Crucial for glucose management and muscle recovery"
        }
    },

    "current_supplements": {
        "vitamin_d3_k2": {
            "dosage": "4000 IU D3 + K2",
            "timing": "with breakfast (fat-soluble)",
            "reason": "Vitamin D deficiency from blood work",
            "started": "January 2026"
        },
        "magnesium_bisglycinate": {
            "dosage": "400mg",
            "timing": "evening (promotes sleep)",
            "reason": "Supports muscle recovery, glucose metabolism, sleep quality",
            "started": "January 2026"
        },
        "vitamin_b12": {
            "dosage": "1000 mcg",
            "timing": "with breakfast",
            "reason": "Suboptimal B12 from blood work"
        },
        "omega_3": {
            "dosage": "1000-2000mg",
            "timing": "with breakfast",
            "reason": "Anti-inflammatory, heart health, glucose management"
        },
        "multivitamin": {
            "timing": "with breakfast",
            "reason": "General micronutrient insurance"
        },
        "protein_powder": {
            "dosage": "2 scoops daily (45g protein)",
            "timing": "breakfast shake",
            "reason": "Convenient protein to hit 150g daily target"
        }
    },

    "dining_hall_protein_sources": {
        "beans": "15g protein per cup",
        "lentils": "18g protein per cup (BEST plant option)",
        "chickpeas": "12g protein per cup",
        "tofu": "15g protein per 100g",
        "greek_yogurt": "20g protein per cup",
        "cottage_cheese": "25g protein per cup",
        "peanut_butter": "8g protein per 2 tbsp",
        "quinoa": "8g protein per cup"
    },

    "plate_formula": {
        "protein": "2 palm-sized portions",
        "vegetables": "2 fist-sized portions (EAT FIRST)",
        "carbs": "2 cupped hand portions (EAT LAST)",
        "fats": "2 thumb-sized portions"
    },

    "red_flags": {
        "stop_if": [
            "Gaining over 1kg per week",
            "Feeling sluggish after meals (glucose spike indicator)",
            "Strength/performance dropping"
        ],
        "increase_calories_if": [
            "No weight gain after 2 weeks",
            "Constantly hungry",
            "Low energy throughout day",
            "Recovery taking longer"
        ]
    },

    "monthly_tracking": {
        "schedule": "Last Sunday of every month",
        "metrics": [
            "Body weight",
            "Progress photos",
            "Body measurements",
            "Strength PRs (personal records)",
            "Review food logs and adherence"
        ],
        "glucose_retest": "April 2026"
    },

    "ai_coaching_instructions": {
        "personality": "Supportive but firm on glucose management rules",
        "priorities": [
            "1. GLUCOSE MANAGEMENT (non-negotiable)",
            "2. Protein target (140-175g daily)",
            "3. Calorie target (2800 daily)",
            "4. Meal timing and sequencing",
            "5. Hydration"
        ],
        "always_remind_about": [
            "Eat vegetables FIRST",
            "Walk after high-carb meals",
            "Pizza only post-workout on training days",
            "Protein before carbs"
        ],
        "never_suggest": [
            "Sugary drinks/soda",
            "Pizza more than 3x/week",
            "Pizza on non-training days",
            "High-carb meals late at night",
            "Skipping post-meal walks after pizza/pasta"
        ],
        "smart_suggestions": [
            "If user logs pizza on non-training day → gentle reminder about glucose + training day rule",
            "If user logs high-carb meal → remind to walk 10-15 min",
            "If user logs carbs without vegetables → remind about meal sequencing",
            "If protein is low by evening → suggest high-protein snack",
            "If user is under 2800 cal → suggest nutrient-dense additions"
        ]
    },

    "context_for_meal_planning": {
        "glucose_priority": "Every meal recommendation MUST consider glucose impact",
        "fiber_requirement": "Every meal should include high-fiber foods",
        "protein_distribution": "Spread protein across all meals (never less than 25g per main meal)",
        "carb_quality": "Always prefer complex carbs, never suggest simple sugars",
        "meal_sequencing_reminder": "Always mention eating vegetables first",
        "pizza_intelligence": "If user asks about pizza, check: (1) Is it a training day? (2) Is it post-workout? (3) Has user had pizza already this week?"
    }
}

# Quick access constants
GLUCOSE_CURRENT = 106.2
GLUCOSE_TARGET = 100
DAILY_CALORIES = 2800
DAILY_PROTEIN = 150
CURRENT_WEIGHT = 139  # lbs
TARGET_WEIGHT = 154   # lbs
