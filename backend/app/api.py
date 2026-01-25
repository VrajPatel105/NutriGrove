# Using fastapi for getting response and sending resopnses to the user
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from .model.schema import UserInput, WhatsAppMessage
from .ai_food_recommendation import FoodRecommender
from .services.whatsapp_handler import WhatsAppHandler
from .services.scheduler_service import SchedulerService
import asyncio

recommender = FoodRecommender()

# Initialize WhatsApp handler with error handling
try:
    whatsapp_handler = WhatsAppHandler()
    print("[OK] WhatsApp handler initialized")
except Exception as e:
    print(f"[WARNING] WhatsApp handler failed to initialize: {e}")
    whatsapp_handler = None

app = FastAPI()

# Initialize scheduler (will be started when app starts)
scheduler = None

@app.on_event("startup")
async def startup_event():
    """Start the scheduler when FastAPI app starts"""
    global scheduler
    try:
        scheduler = SchedulerService()
        scheduler.start()
        print("[OK] Scheduler service started!")
    except Exception as e:
        print(f"[WARNING] Scheduler failed to start: {e}")
        print("Server will continue without scheduled jobs.")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler when FastAPI app shuts down"""
    if scheduler:
        scheduler.stop()
        print("Scheduler service stopped!")

@app.get('/')
def hello():
    return {'message':'Hello, This is API system for NutriGrove WhatsApp Nutrition Coach'}

@app.post('/recommendations')
def recommendations(data: UserInput):
    user_preferences = {
        'age': data.age,
        'gender': data.gender,
        'weight': data.weight,
        'height': data.height,
        'activity level': data.activity_level,
        'goal' : data.goal,
        'diet' : data.diet,
        'dietary_restrictions': data.dietary_restrictions,
        'calories' : data.calories,
        'protein': data.protein,
        'comments': data.comments,
        'allergens': data.allergens,
        'dislikes': data.dislikes
    }

    schedule = recommender.get_daily_meal_schedule(user_preferences)

    return JSONResponse(status_code=200, content=schedule)

@app.post('/whatsapp-webhook')
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(None)
):
    """
    Twilio WhatsApp webhook endpoint

    Twilio sends POST requests here when users send WhatsApp messages

    Args:
        From: Sender's phone number (format: "whatsapp:+1234567890")
        Body: Message text
        MessageSid: Unique message ID from Twilio

    Returns:
        TwiML response with bot's reply
    """
    print(f"Received WhatsApp message from {From}: {Body}")

    if not whatsapp_handler:
        print("Error: WhatsApp handler not initialized")
        return PlainTextResponse(
            "WhatsApp service not available. Please check server configuration.",
            status_code=503
        )

    try:
        # Process message through WhatsApp handler
        response_text = await whatsapp_handler.handle_incoming_message(From, Body)

        print(f"Response to {From}: {response_text}")

        # Create TwiML response
        twiml_response = whatsapp_handler.create_twiml_response(response_text)

        print(f"TwiML Response: {twiml_response}")

        # Return as UTF-8 encoded XML
        return Response(
            content=twiml_response,
            media_type="application/xml; charset=utf-8"
        )

    except Exception as e:
        print(f"Error processing WhatsApp message: {e}")
        import traceback
        traceback.print_exc()

        error_response = whatsapp_handler.create_twiml_response(
            "Sorry, I encountered an error. Please try again."
        )
        return Response(content=error_response, media_type="application/xml")

@app.get('/whatsapp-webhook')
async def whatsapp_webhook_validation():
    """
    GET endpoint for Twilio webhook validation
    Twilio sends a GET request to verify the webhook URL
    """
    return PlainTextResponse("WhatsApp webhook is active!")

# Adding a new api endpoint for getting the entire menu data. Used the function from class FoodRecommender. : EDIT - will need to figure it out later on.
@app.get('/menu')
def todays_menu():
    return recommender.get_all_menu_data()

#   Essential Parameters (definitely add these):
# age
# weight
# height
# dietary_restrictions
# calories
# protein
# comments 
# THE ALL ABOVE ALREADY EXISTS IN THE API, BUT THE ONE'S BELOW NEEDS TO BE ADDED TO THE API. (09/09/25)
#   - gender (male/female)
#   - activity_level (active/sedentary/moderate)
#   - goal (build_muscle/lose_weight/maintain)
#   - diet (Keto/Paleo/Vegan/etc.)
#   - allergens (array like [Eggs, Fish, Shellfish])
#   - dislikes (array of disliked foods)