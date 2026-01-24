"""
WhatsApp Handler
Handles all Twilio WhatsApp integrations
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from .conversational_agent import ConversationalAgent


class WhatsAppHandler:
    """
    Handle all Twilio WhatsApp integrations
    """

    def __init__(self):
        load_dotenv()
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

        if self.twilio_account_sid and self.twilio_auth_token:
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.twilio_client = None
            print("Warning: Twilio credentials not found. WhatsApp features will not work.")

        # Lazy load agent to avoid circular imports
        self._agent = None

    @property
    def agent(self):
        """Lazy load conversational agent"""
        if self._agent is None:
            self._agent = ConversationalAgent()
        return self._agent

    async def handle_incoming_message(self, from_number: str, message_body: str) -> str:
        """
        Process incoming WhatsApp message

        Args:
            from_number: User's phone number (e.g., "whatsapp:+1234567890")
            message_body: Text content of message

        Returns:
            Response text to send back
        """
        # Clean phone number (remove "whatsapp:" prefix)
        phone_number = from_number.replace('whatsapp:', '').strip()

        print(f"Incoming WhatsApp from {phone_number}: {message_body}")

        # Process through conversational agent
        response_text = await self.agent.process_message(message_body, phone_number)

        print(f"Response to {phone_number}: {response_text}")

        return response_text

    def send_whatsapp_message(self, to_number: str, message: str) -> bool:
        """
        Send WhatsApp message to user

        Args:
            to_number: Phone number (e.g., "+1234567890")
            message: Text to send

        Returns:
            True if sent successfully
        """
        if not self.twilio_client:
            print("Error: Twilio client not initialized")
            return False

        try:
            self.twilio_client.messages.create(
                from_=f'whatsapp:{self.whatsapp_number}',
                to=f'whatsapp:{to_number}',
                body=message
            )
            print(f"WhatsApp message sent to {to_number}")
            return True
        except Exception as e:
            print(f"Error sending WhatsApp: {e}")
            return False

    def create_twiml_response(self, message: str) -> str:
        """
        Create TwiML response for Twilio webhook

        Args:
            message: Response text

        Returns:
            XML TwiML response
        """
        response = MessagingResponse()
        response.message(message)
        return str(response)
