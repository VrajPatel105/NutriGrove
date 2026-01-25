"""
Conversational Agent - Main AI Brain
Uses Claude API with function calling to handle all WhatsApp conversations
"""

import os
import json
import anthropic
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from typing import Dict, List, Optional, Any

from .menu_service import MenuService
from .food_logger import FoodLogger
from .nutrition_estimator import NutritionEstimator
from ..utils.date_parser import DateParser
from ..utils.food_parser import FoodParser
from ..config.user_health_profile import VRAJ_HEALTH_PROFILE


class ConversationalAgent:
    """
    Main AI agent that handles all WhatsApp conversations
    Uses Claude API (Anthropic) with function calling
    """

    def __init__(self):
        load_dotenv()

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY in environment variables")

        self.client = anthropic.Anthropic(api_key=api_key)

        # Initialize Supabase
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )

        # Initialize services
        self.menu_service = MenuService()
        self.food_logger = FoodLogger()
        self.nutrition_estimator = NutritionEstimator()

    async def process_message(self, user_message: str, phone_number: str) -> str:
        """
        Main function that processes every WhatsApp message

        Steps:
        1. Load conversation context from conversation_state table
        2. Load user profile
        3. Send to Claude API with:
           - System prompt (defines bot personality & capabilities)
           - Conversation history (last 10 messages)
           - User profile context
           - Available functions
           - Current message
        4. Claude decides what to do:
           - Call function(s) if needed
           - Respond directly if no functions needed
        5. If functions called, execute them and get results
        6. Send function results back to Claude for final response
        7. Update conversation state
        8. Return response text

        Args:
            user_message: What the user sent via WhatsApp
            phone_number: User's phone number (unique identifier)

        Returns:
            Bot's response text to send back via WhatsApp
        """
        # Load context
        context = await self.load_conversation_context(phone_number)
        profile = await self.load_user_profile(phone_number)

        # Build conversation history
        messages = context.get('history', [])
        messages.append({"role": "user", "content": user_message})

        # Keep only last 20 messages to avoid token limits
        if len(messages) > 20:
            messages = messages[-20:]

        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,  # Increased to allow longer responses
                system=self.get_system_prompt(profile),
                messages=messages,
                tools=self.get_function_definitions()
            )

            # Handle function calls
            if response.stop_reason == "tool_use":
                # Execute functions
                function_results = await self.execute_functions(response.content)

                # Build messages for next call
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": function_results
                })

                # Get final response from Claude with function results
                final_response = self.client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4096,
                    system=self.get_system_prompt(profile),
                    messages=messages
                )

                response_text = self.extract_text(final_response.content)

                # Add final assistant message to history
                # IMPORTANT: Save the full content (not just text) to preserve any tool_use blocks
                if response_text:
                    # If there's text, save the full content to preserve structure
                    messages.append({
                        "role": "assistant",
                        "content": final_response.content  # Save full content, not just text
                    })
                else:
                    # If Claude returned no text after function call, this is an error
                    # Return a helpful message instead of "Done."
                    response_text = "I found some options but had trouble formatting the response. Could you ask me again? (e.g., 'show me lunch options')"
                    messages.append({
                        "role": "assistant",
                        "content": response_text
                    })
                    print(f"[ERROR] Claude returned empty content after tool use. Stop reason: {final_response.stop_reason}")
            else:
                response_text = self.extract_text(response.content)

                # Add assistant message to history
                # IMPORTANT: Save the full content to preserve structure
                if response_text:
                    messages.append({
                        "role": "assistant",
                        "content": response.content  # Save full content, not just text
                    })
                else:
                    # Fallback if no text extracted
                    response_text = "Okay."
                    messages.append({
                        "role": "assistant",
                        "content": response_text
                    })

            # Update conversation state
            await self.save_conversation_state(phone_number, messages, response_text)

            return response_text

        except Exception as e:
            import traceback
            print(f"Error in conversational agent: {e}")
            traceback.print_exc()
            return "Sorry, I encountered an error. Please try again."

    def get_system_prompt(self, user_profile: Dict) -> str:
        """
        System prompt that defines bot's personality and capabilities

        This is critical - tells Claude how to behave
        """
        now = datetime.now()
        current_time = now.strftime('%I:%M %p')
        current_date = now.strftime('%A, %B %d, %Y')
        current_meal = DateParser.get_meal_time_context()

        # Build profile summary
        if user_profile:
            profile_summary = f"""
USER PROFILE:
- Age: {user_profile.get('age', 'Not set')}, Gender: {user_profile.get('gender', 'Not set')}
- Weight: {user_profile.get('weight', 'Not set')} lbs, Height: {user_profile.get('height', 'Not set')} cm
- Goal: {user_profile.get('goal', 'Not set')}
- Activity: {user_profile.get('activity_level', 'Not set')}
- Daily targets: {user_profile.get('calories_target', 'Not set')} cal, {user_profile.get('protein_target', 'Not set')}g protein
- Diet: {user_profile.get('diet', 'None')}
- Restrictions: {user_profile.get('dietary_restrictions', 'None')}
- Allergens: {', '.join(user_profile.get('allergens', [])) or 'None'}
- Dislikes: {', '.join(user_profile.get('dislikes', [])) or 'None'}
"""
        else:
            profile_summary = "USER PROFILE: Not set up yet. Ask user to provide their info."

        # Get health profile information
        health_profile = VRAJ_HEALTH_PROFILE
        glucose_current = health_profile['blood_work_results']['glucose_fasting']['value']
        glucose_target = health_profile['health_conditions']['glucose_management']['target_glucose']

        # Get day of week for training day check
        day_of_week = now.strftime('%A')
        is_training_day = day_of_week in ['Monday', 'Wednesday', 'Friday']

        return f"""You are Vraj's personal AI nutrition coach via WhatsApp.

{profile_summary}

CRITICAL HEALTH CONTEXT:
==========================================
GLUCOSE MANAGEMENT - HIGHEST PRIORITY
==========================================
⚠️ Current fasting glucose: {glucose_current} mg/dL (borderline prediabetic)
🎯 Target: {glucose_target}
📅 Next blood test: April 2026

MANDATORY GLUCOSE MANAGEMENT PROTOCOL:
1. **Meal Sequencing (NON-NEGOTIABLE)**:
   - ALWAYS eat in this order: Vegetables → Protein → Carbs → Treats
   - This reduces glucose spikes by 30-40%
   - Remind user of this order for EVERY meal

2. **Post-Meal Activity**:
   - Walk 10-15 minutes after high-carb meals (pizza, pasta, rice)
   - ALWAYS remind user to walk after these meals

3. **Pizza Protocol** (STRICTLY ENFORCED):
   - Current day: {day_of_week} {"✅ TRAINING DAY" if is_training_day else "❌ NON-TRAINING DAY"}
   - Pizza ONLY allowed on: Monday, Wednesday, Friday (training days)
   - Pizza ONLY allowed post-workout (within 2 hours)
   - Maximum 2-3 times per week total
   - Maximum 3-4 slices per meal
   - MUST be paired with large salad eaten FIRST
   - MUST walk 10-15 minutes after eating
   - If user asks about pizza on non-training day: Firmly remind about glucose management and training day rule

4. **Carb Hierarchy**:
   - ✅ BEST: Brown rice, quinoa, beans, lentils, chickpeas (high fiber + protein)
   - ⚠️ MODERATE: White rice (small portions), whole wheat pasta
   - ❌ LIMIT: White bread, pastries
   - 🚫 AVOID: Soda, candy, sugary drinks

5. **Protein Buffer Strategy**:
   - 25-35g protein per meal, eaten BEFORE carbs
   - Slows carb absorption and reduces glucose spikes
   - Remind user if they log carbs without sufficient protein

6. **Fiber Requirements**:
   - Every meal must include high-fiber foods
   - Vegetables with EVERY meal (eaten first)
   - Beans/lentils daily (best plant protein + fiber)

NUTRITION TARGETS:
- Daily Calories: 2800
- Daily Protein: 150g (range: 140-175g)
- Weight: 139 lbs → Target: 154 lbs
- Goal: Lean muscle gain while managing glucose

YOUR ROLE:
You are a friendly, knowledgeable nutrition coach who helps Vraj:
1. Plan his daily meals from the UMass Dartmouth dining hall menu
2. Track what he actually eats throughout the day
3. Keep him on track with his nutrition goals
4. Provide smart suggestions and motivation

PERSONALITY:
- Conversational and natural (like texting a friend)
- Use emojis appropriately (food emojis, checkmarks, etc.)
- Be encouraging but honest
- Keep messages concise (WhatsApp style - under 200 words)
- Don't be overly formal or robotic

CRITICAL CAPABILITIES:

1. UNDERSTAND CONTEXT:
   - Current time: {current_time}
   - Current date: {current_date}
   - Likely meal: {current_meal}
   - Remember what was just discussed in conversation
   - Track today's plan vs what's been logged

2. PARSE NATURAL LANGUAGE:
   - "ate eggs and toast" -> extract: eggs, toast
   - "had some chips" -> estimate portion, log
   - "the salmon" -> refer to earlier context or today's menu
   - Handle typos, variations, casual language

3. SMART DECISION MAKING:
   - When to ask for clarification vs when to estimate
   - When to search menu vs when to estimate external foods
   - When to call functions vs when to respond directly

4. FOOD LOGGING INTELLIGENCE:
   - If food is from dining hall -> use search_menu_minimal or log_food_item
   - If food is external (Ferrero Rocher, Starbucks, etc.) -> use your built-in knowledge to estimate
   - If portion unclear -> ask "how much approximately?"
   - If multiple items -> parse and log each separately

5. PROACTIVE SUGGESTIONS:
   - If user is 500+ cal under target late in day -> suggest snack
   - If user hasn't logged lunch by 1 PM -> gentle reminder
   - If protein is low -> suggest protein-rich options

CONVERSATION FLOW EXAMPLES:

Example 1: Food Logging
User: "ate 3 eggs and toast"
You think: User ate breakfast, need to log these items
You call: log_food_item for eggs (3 eggs, breakfast)
You call: log_food_item for toast (2 slices, breakfast)
You call: get_daily_progress to show updated totals
You respond: "Logged from your plan:
- 3 eggs - 210 cal, 18g protein
- 2 slices toast - 160 cal, 8g protein

Breakfast: 370 cal, 26g protein
Today's progress: 370/2800 cal, 26/150g protein"

Example 2: External Food
User: "ate some ferrero rocher"
You think: External food, I know this! Each piece ~73 cal
You respond: "How many pieces did you eat?"
User: "like 3"
You call: log_food_item("Ferrero Rocher", "3 pieces", "snack", 219, 3, 26, 13, False, True)
You respond: "Logged:
+ Ferrero Rocher - 3 pieces (219 cal, 3g protein)

Updated: 1739/2800 cal, 82/150g protein"

Example 3: Meal Suggestions
User: "what should i eat for lunch?"
You call: search_menu_minimal(meal_type="lunch", min_protein=40)
You respond: "Here are your best lunch options today:

1. 🍗 Chicken Alfredo (900 cal, 45g protein) - Pasta Station
2. 🐟 Grilled Salmon Bowl (650 cal, 40g protein) - Global Kitchen
3. 🥙 Turkey Club Wrap (720 cal, 38g protein) - Deli

Which sounds good?"

Example 4: Profile Update
User: "my weight is 170 now"
You call: update_user_profile(phone_number, {{"weight":170}})
You respond: "Updated your weight to 170 lbs! Your calorie target is now 2850 (recalculated). Want me to regenerate today's meal plan?"

AVAILABLE FUNCTIONS:
You have access to these functions - use them intelligently:

- search_menu_minimal: Search dining hall menu with filters
- get_food_details: Get complete nutrition for specific item
- log_food_item: Save what user ate
- get_daily_progress: Show current vs target
- update_user_profile: Update user's info
- save_custom_rule: Save ongoing preferences
- generate_meal_plan: Create daily meal plan

RULES:
- ALWAYS log food when user mentions eating something
- ALWAYS show daily progress after logging
- Be natural and conversational
- Use emojis but don't overdo it
- Keep responses under 200 words
- Ask clarifying questions when needed
- Be encouraging and supportive
- For external foods, use YOUR knowledge first before calling estimate_external_food

Current time: {current_time}
Current date: {current_date}
Current meal context: {current_meal}
"""

    def get_function_definitions(self) -> List[Dict]:
        """
        Define all functions available to Claude
        Claude will decide which to call based on context
        """
        return [
            {
                "name": "search_menu_minimal",
                "description": "Search dining hall menu with filters. Returns 5-10 relevant items with basic nutrition (name, calories, protein, carbs, fat). Use this when user asks for meal suggestions or 'what should I eat?'",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "meal_type": {
                            "type": "string",
                            "enum": ["breakfast", "lunch", "dinner"],
                            "description": "Which meal to search for"
                        },
                        "min_protein": {
                            "type": "integer",
                            "description": "Minimum protein in grams"
                        },
                        "max_calories": {
                            "type": "integer",
                            "description": "Maximum calories"
                        },
                        "exclude_allergens": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Allergens to exclude"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results (default 10)"
                        }
                    }
                }
            },
            {
                "name": "get_food_details",
                "description": "Get complete nutrition information for a specific food item. Use when user asks detailed questions about a specific food's nutrition.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "food_name": {
                            "type": "string",
                            "description": "Name of the food item to look up"
                        }
                    },
                    "required": ["food_name"]
                }
            },
            {
                "name": "log_food_item",
                "description": "Log a food item that user ate. Save to database. Call this whenever user mentions eating something.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "phone_number": {"type": "string"},
                        "food_name": {"type": "string"},
                        "portion": {"type": "string", "description": "e.g. '3 eggs', '1 cup', 'small bag'"},
                        "meal_type": {"type": "string", "enum": ["breakfast", "lunch", "dinner", "snack"]},
                        "calories": {"type": "integer"},
                        "protein_g": {"type": "number"},
                        "carbs_g": {"type": "number"},
                        "fat_g": {"type": "number"},
                        "was_planned": {"type": "boolean", "description": "true if from morning plan"},
                        "is_external": {"type": "boolean", "description": "true if not from dining hall"}
                    },
                    "required": ["phone_number", "food_name", "portion", "meal_type"]
                }
            },
            {
                "name": "get_daily_progress",
                "description": "Get current nutrition progress vs targets for today. Returns planned vs actual calories, protein, etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "phone_number": {"type": "string"},
                        "date": {"type": "string", "description": "YYYY-MM-DD format, defaults to today"}
                    },
                    "required": ["phone_number"]
                }
            },
            {
                "name": "update_user_profile",
                "description": "Update user's profile (weight, goals, targets, etc.). Use when user mentions changes to their stats or preferences.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "phone_number": {"type": "string"},
                        "updates": {
                            "type": "object",
                            "description": "Fields to update: weight, calories_target, protein_target, goal, activity_level, etc."
                        }
                    },
                    "required": ["phone_number", "updates"]
                }
            },
        ]

    async def execute_functions(self, tool_calls: List) -> List[Dict]:
        """
        Execute all function calls requested by Claude
        Return results formatted for Claude to process
        """
        results = []

        for block in tool_calls:
            if hasattr(block, 'type') and block.type == "tool_use":
                function_name = block.name
                function_args = block.input
                tool_use_id = block.id

                print(f"Executing function: {function_name} with args: {function_args}")

                # Call the actual function
                try:
                    if function_name == "search_menu_minimal":
                        result = await self.menu_service.search_menu_minimal(**function_args)
                    elif function_name == "get_food_details":
                        result = await self.menu_service.get_food_details(**function_args)
                    elif function_name == "log_food_item":
                        result = await self.food_logger.log_food_item(**function_args)
                    elif function_name == "get_daily_progress":
                        result = await self.food_logger.get_daily_progress(**function_args)
                    elif function_name == "update_user_profile":
                        result = await self.update_user_profile(**function_args)
                    else:
                        result = {"error": f"Unknown function: {function_name}"}

                    # Safe JSON serialization - handle date objects and other non-serializable types
                    try:
                        json_result = json.dumps(result, default=str)
                    except (TypeError, ValueError) as json_err:
                        print(f"JSON serialization error for {function_name}: {json_err}")
                        json_result = json.dumps({"error": "Could not serialize result", "raw": str(result)})

                    results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json_result
                    })
                except Exception as e:
                    import traceback
                    print(f"Error executing {function_name}: {e}")
                    traceback.print_exc()
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps({"error": str(e)})
                    })

        return results

    async def update_user_profile(self, phone_number: str, updates: Dict) -> Dict:
        """Update user profile in database"""
        try:
            # Check if profile exists
            existing = self.supabase.table('user_profiles')\
                .select('*')\
                .eq('phone_number', phone_number)\
                .execute()

            if existing.data:
                # Update existing profile
                self.supabase.table('user_profiles')\
                    .update(updates)\
                    .eq('phone_number', phone_number)\
                    .execute()
            else:
                # Create new profile
                updates['phone_number'] = phone_number
                self.supabase.table('user_profiles').insert(updates).execute()

            return {"success": True, "message": "Profile updated", "updates": updates}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def load_conversation_context(self, phone_number: str) -> Dict:
        """Load conversation state from database"""
        result = self.supabase.table('conversation_state')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .execute()

        if result.data:
            context_data = result.data[0].get('context_data', {})
            history = context_data.get('conversation_history', [])

            # Convert stored dictionaries back to proper format for anthropic
            converted_history = []
            for msg in history:
                if isinstance(msg, dict) and 'content' in msg:
                    content = msg['content']

                    # If content is a list of dicts (complex content like tool calls)
                    if isinstance(content, list):
                        # For assistant messages with tool_use blocks, keep as-is
                        # The dicts are already in the correct format
                        converted_history.append(msg)
                    # If content is a string (simple text message)
                    elif isinstance(content, str):
                        converted_history.append(msg)
                    else:
                        # Fallback - convert to string
                        converted_history.append({
                            'role': msg['role'],
                            'content': str(content)
                        })
                else:
                    converted_history.append(msg)

            return {
                'history': converted_history,
                'current_phase': result.data[0].get('current_phase'),
                'context': context_data
            }
        else:
            return {'history': [], 'current_phase': None, 'context': {}}

    async def load_user_profile(self, phone_number: str) -> Optional[Dict]:
        """Load user profile from database"""
        result = self.supabase.table('user_profiles')\
            .select('*')\
            .eq('phone_number', phone_number)\
            .execute()

        if result.data:
            return result.data[0]
        else:
            return None

    async def save_conversation_state(self, phone_number: str, messages: List, last_response: str):
        """Save conversation state to database"""
        import json

        # Convert messages to JSON-serializable format
        serializable_messages = []
        for msg in messages:
            content = msg.get('content')

            if isinstance(content, list):
                # Handle list of content blocks (new anthropic format)
                serializable_content = []

                for block in content:
                    # Check if it's a TextBlock object
                    if hasattr(block, 'type'):
                        block_type = getattr(block, 'type', None)

                        # If it's a tool_use block, we need to preserve it
                        if block_type == 'tool_use':
                            if hasattr(block, 'model_dump'):
                                serializable_content.append(block.model_dump())
                            elif hasattr(block, 'dict'):
                                serializable_content.append(block.dict())
                            else:
                                serializable_content.append({'type': 'tool_use', 'id': block.id, 'name': block.name, 'input': block.input})

                        # If it's a text block, extract just the text string
                        elif block_type == 'text':
                            if hasattr(block, 'text'):
                                serializable_content.append({'type': 'text', 'text': block.text})
                            else:
                                serializable_content.append(str(block))
                        else:
                            # Unknown block type, serialize it
                            if hasattr(block, 'model_dump'):
                                serializable_content.append(block.model_dump())
                            elif hasattr(block, 'dict'):
                                serializable_content.append(block.dict())
                            else:
                                serializable_content.append(str(block))

                    # If it's already a dict (from database), keep it
                    elif isinstance(block, dict):
                        serializable_content.append(block)
                    else:
                        serializable_content.append(str(block))

                # ALWAYS keep as list to preserve message structure
                # This is critical for maintaining tool_use/tool_result pairing
                serializable_messages.append({
                    'role': msg['role'],
                    'content': serializable_content
                })
            else:
                # Content is already a string, keep it as-is
                serializable_messages.append(msg)

        context_data = {
            'conversation_history': serializable_messages,
            'last_response': last_response,
            'last_interaction': datetime.now().isoformat()
        }

        # Check if exists
        existing = self.supabase.table('conversation_state')\
            .select('id')\
            .eq('phone_number', phone_number)\
            .execute()

        if existing.data:
            # Update
            self.supabase.table('conversation_state')\
                .update({
                    'context_data': context_data,
                    'last_interaction': datetime.now().isoformat()
                })\
                .eq('phone_number', phone_number)\
                .execute()
        else:
            # Insert
            self.supabase.table('conversation_state').insert({
                'phone_number': phone_number,
                'context_data': context_data,
                'last_interaction': datetime.now().isoformat()
            }).execute()

    def extract_text(self, content: Any) -> str:
        """Extract text from Claude response content"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            text_parts = []
            for block in content:
                if hasattr(block, 'type') and block.type == "text":
                    text_parts.append(block.text)
            return ''.join(text_parts)
        else:
            return str(content)
