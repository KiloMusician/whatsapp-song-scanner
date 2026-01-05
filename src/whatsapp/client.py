"""WhatsApp API client supporting both Twilio and Evolution API."""

from abc import ABC, abstractmethod
from typing import Dict, List, cast

import requests  # type: ignore
from requests import RequestException  # type: ignore
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioClient

from config.settings import WHATSAPP_CONFIG
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WhatsAppProvider(ABC):
    """Abstract base class for WhatsApp providers."""

    @abstractmethod
    def send_message(self, to: str, message: str) -> bool:
        """Send a message."""
        raise NotImplementedError

    @abstractmethod
    def get_messages(self, chat_id: str, limit: int = 100) -> List[Dict]:
        """Get messages from a chat."""
        raise NotImplementedError


class TwilioProvider(WhatsAppProvider):
    """Twilio WhatsApp provider."""

    def __init__(self):
        """Initialize Twilio client."""
        self.client = TwilioClient(
            WHATSAPP_CONFIG["twilio_account_sid"], WHATSAPP_CONFIG["twilio_auth_token"]
        )
        self.from_number = WHATSAPP_CONFIG["twilio_whatsapp_number"]
        logger.info("Twilio WhatsApp provider initialized")

    def send_message(self, to: str, message: str) -> bool:
        """Send a WhatsApp message via Twilio.

        Args:
            to: Recipient phone number (with country code)
            message: Message text

        Returns:
            True if successful
        """
        try:
            message_response = self.client.messages.create(
                from_=f"whatsapp:{self.from_number}", to=f"whatsapp:{to}", body=message
            )
            logger.info("Message sent via Twilio: %s", message_response.sid)
            return True
        except TwilioRestException as exc:
            logger.error("Failed to send message via Twilio: %s", exc)
            return False

    def get_messages(self, chat_id: str, limit: int = 100) -> List[Dict]:
        """Get messages from Twilio (webhook-based, not polling)."""
        logger.warning("Twilio uses webhook-based messages, not polling")
        return []

    def get_chats(self) -> List[Dict]:
        """Get all chats from Twilio (not supported by webhook provider)."""
        logger.warning("Twilio webhook-based provider does not support chat enumeration")
        return []


class EvolutionProvider(WhatsAppProvider):
    """Evolution API WhatsApp provider."""

    def __init__(self):
        """Initialize Evolution API client."""
        self.base_url = WHATSAPP_CONFIG["evolution_api_url"]
        self.api_key = WHATSAPP_CONFIG["evolution_api_key"]
        self.instance_name = WHATSAPP_CONFIG["evolution_instance_name"]
        self.headers = {"apikey": self.api_key, "Content-Type": "application/json"}
        logger.info("Evolution API WhatsApp provider initialized")

    def send_message(self, to: str, message: str) -> bool:
        """Send a WhatsApp message via Evolution API.

        Args:
            to: Recipient phone number (with country code)
            message: Message text

        Returns:
            True if successful
        """
        try:
            url = f"{self.base_url}/message/sendText/{self.instance_name}"
            payload = {"number": to, "textMessage": {"text": message}}
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info("Message sent via Evolution API to %s", to)
            return True
        except RequestException as exc:
            logger.error("Failed to send message via Evolution API: %s", exc)
            return False

    def get_messages(self, chat_id: str, limit: int = 100) -> List[Dict]:
        """Get messages from a chat via Evolution API.

        Args:
            chat_id: Chat identifier
            limit: Maximum messages to retrieve

        Returns:
            List of message dictionaries
        """
        try:
            url = f"{self.base_url}/chat/findMessages/{self.instance_name}"
            payload = {"where": {"key": {"remoteJid": chat_id}}, "limit": limit}
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()

            messages = cast(List[Dict], response.json())
            logger.info("Retrieved %s messages from Evolution API", len(messages))
            return messages
        except RequestException as exc:
            logger.error("Failed to get messages from Evolution API: %s", exc)
            return []

    def get_chats(self) -> List[Dict]:
        """Get all chats from Evolution API.

        Returns:
            List of chat dictionaries
        """
        try:
            url = f"{self.base_url}/chat/findChats/{self.instance_name}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            chats = cast(List[Dict], response.json())
            logger.info("Retrieved %s chats from Evolution API", len(chats))
            return chats
        except RequestException as exc:
            logger.error("Failed to get chats from Evolution API: %s", exc)
            return []


class WhatsAppClient:
    """Main WhatsApp client that uses the configured provider."""

    def __init__(self):
        """Initialize WhatsApp client with configured provider."""
        provider = WHATSAPP_CONFIG.get("provider", "evolution").lower()

        if provider == "twilio":
            self.provider = TwilioProvider()
        elif provider == "evolution":
            self.provider = EvolutionProvider()
        else:
            raise ValueError(f"Unknown WhatsApp provider: {provider}")

        logger.info("WhatsApp client initialized with provider: %s", provider)

    def send_message(self, to: str, message: str) -> bool:
        """Send a message."""
        return cast(bool, self.provider.send_message(to, message))

    def get_messages(self, chat_id: str, limit: int = 100) -> List[Dict]:
        """Get messages from a chat."""
        return cast(List[Dict], self.provider.get_messages(chat_id, limit))

    def get_chats(self) -> List[Dict]:
        """Get all chats (Evolution API only)."""
        if isinstance(self.provider, EvolutionProvider):
            return self.provider.get_chats()
        return []


# SINGLETON INSTANCE
whatsapp_client = WhatsAppClient()
