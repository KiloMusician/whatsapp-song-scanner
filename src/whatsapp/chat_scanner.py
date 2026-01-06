"""Scan and process WhatsApp chat history."""

from typing import Dict

from sqlalchemy.orm import Session

from src.database.operations import ChatOperations
from src.utils.logger import get_logger
from src.whatsapp.client import whatsapp_client
from src.whatsapp.message_handler import message_handler

logger = get_logger(__name__)


class ChatScanner:
    """Scan WhatsApp chats for new messages."""

    def __init__(self):
        """Initialize chat scanner."""
        self.client = whatsapp_client
        self.handler = message_handler

    def scan_chat(self, db: Session, chat_id: str, limit: int = 100) -> int:
        """Scan a chat for new messages.

        Args:
            db: Database session
            chat_id: Chat identifier
            limit: Maximum messages to retrieve

        Returns:
            Number of messages processed
        """
        logger.info("Scanning chat: %s", chat_id)

        # Ensure chat exists in database
        ChatOperations.create_or_update_chat(db, chat_id)

        # Get messages from WhatsApp
        messages = self.client.get_messages(chat_id, limit)

        if not messages:
            logger.info("No messages found in chat %s", chat_id)
            return 0

        processed = 0
        for message in messages:
            try:
                success = self.handler.handle_evolution_message(db, message)
                if success:
                    processed += 1
            except Exception as exc:  # noqa: BLE001
                logger.error("Error processing message: %s", exc)
                continue

        # Update last scan time
        ChatOperations.update_last_scan(db, chat_id)

        logger.info("Processed %s/%s messages from chat %s", processed, len(messages), chat_id)
        return processed

    def scan_all_active_chats(self, db: Session) -> Dict[str, int]:
        """Scan all active chats.

        Args:
            db: Database session

        Returns:
            Dictionary of chat_id -> messages_processed
        """
        logger.info("Scanning all active chats")

        chats = ChatOperations.get_active_chats(db)
        results = {}

        for chat in chats:
            chat_id = str(chat.chat_id)
            try:
                count = self.scan_chat(db, chat_id)
                results[chat_id] = count
            except Exception as exc:  # noqa: BLE001
                logger.error("Error scanning chat %s: %s", chat_id, exc)
                results[chat_id] = 0
                continue

        logger.info(f"Scanned {len(results)} chats")
        return results


# SINGLETON INSTANCE
chat_scanner = ChatScanner()
