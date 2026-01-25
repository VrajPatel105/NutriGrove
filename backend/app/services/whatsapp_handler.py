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

    def strip_emojis(self, text: str) -> str:
        """
        Remove emojis from text to avoid TwiML encoding issues
        Twilio's WhatsApp TwiML responses don't handle emojis well
        """
        import re
        # Remove emojis using regex
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub('', text)

    def create_twiml_response(self, message: str) -> str:
        """
        Create TwiML response for Twilio webhook
        Splits long messages into chunks (WhatsApp has 1600 char limit)

        Args:
            message: Response text

        Returns:
            XML TwiML response
        """
        # Strip emojis to avoid TwiML encoding issues
        message = self.strip_emojis(message)

        response = MessagingResponse()

        # WhatsApp has a 1600 character limit per message
        MAX_LENGTH = 1500  # Leave some buffer

        if len(message) <= MAX_LENGTH:
            response.message(message)
        else:
            # Split into chunks
            chunks = []
            current_chunk = ""

            for line in message.split('\n'):
                if len(current_chunk) + len(line) + 1 <= MAX_LENGTH:
                    current_chunk += line + '\n'
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = line + '\n'

            if current_chunk:
                chunks.append(current_chunk.strip())

            # Add each chunk as a separate message
            for chunk in chunks:
                response.message(chunk)

        return str(response)
