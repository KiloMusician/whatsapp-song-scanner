"""Database CRUD operations."""

from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.database.models import WhatsAppChat, ChatMessage, ExtractedSong, MatchedSong, SongRequest


class ChatOperations:
    """Operations for WhatsApp chats."""

    @staticmethod
    def create_or_update_chat(db: Session, chat_id: str, chat_name: str = None) -> WhatsAppChat:
        """Create or update a WhatsApp chat."""
        chat = db.query(WhatsAppChat).filter(WhatsAppChat.chat_id == chat_id).first()
        if chat:
            if chat_name:
                chat.chat_name = chat_name
            chat.updated_at = datetime.now(timezone.utc)
        else:
            chat = WhatsAppChat(chat_id=chat_id, chat_name=chat_name)
            db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    @staticmethod
    def get_active_chats(db: Session) -> List[WhatsAppChat]:
        """Get all active chats."""
        return db.query(WhatsAppChat).filter(WhatsAppChat.is_active.is_(True)).all()

    @staticmethod
    def update_last_scan(db: Session, chat_id: str, message_id: str = None):
        """Update last scan timestamp for a chat."""
        chat = db.query(WhatsAppChat).filter(WhatsAppChat.chat_id == chat_id).first()
        if chat:
            chat.last_scan_time = datetime.now(timezone.utc)
            if message_id:
                chat.last_message_id = message_id
            db.commit()


class MessageOperations:
    """Operations for chat messages."""

    @staticmethod
    def create_message(
        db: Session,
        message_id: str,
        chat_id: str,
        sender_number: str,
        sender_name: str,
        raw_text: str,
        timestamp: datetime,
    ) -> ChatMessage:
        """Create a new message."""
        message = ChatMessage(
            message_id=message_id,
            chat_id=chat_id,
            sender_number=sender_number,
            sender_name=sender_name,
            raw_text=raw_text,
            timestamp=timestamp,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_unprocessed_messages(db: Session, limit: int = 100) -> List[ChatMessage]:
        """Get unprocessed messages."""
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.is_processed.is_(False))
            .order_by(ChatMessage.timestamp.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def mark_processed(db: Session, message_id: int, cleaned_text: str = None):
        """Mark message as processed."""
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if message:
            message.is_processed = True
            if cleaned_text:
                message.cleaned_text = cleaned_text
            db.commit()

    @staticmethod
    def record_processing_error(db: Session, message_id: int, error: str):
        """Record processing error."""
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if message:
            message.processing_attempts += 1
            message.processing_error = error
            db.commit()


class SongOperations:
    """Operations for extracted and matched songs."""

    @staticmethod
    def create_extraction(
        db: Session,
        message_id: int,
        original_phrase: str,
        confidence_score: float,
        extraction_method: str,
    ) -> ExtractedSong:
        """Create an extracted song entry."""
        extraction = ExtractedSong(
            message_id=message_id,
            original_phrase=original_phrase,
            confidence_score=confidence_score,
            extraction_method=extraction_method,
        )
        db.add(extraction)
        db.commit()
        db.refresh(extraction)
        return extraction

    @staticmethod
    def create_match(
        db: Session,
        extraction_id: int,
        song_title: str,
        artist_name: str = None,
        album_name: str = None,
        musicbrainz_id: str = None,
        match_confidence: float = None,
        match_source: str = None,
        match_metadata: dict = None,
    ) -> MatchedSong:
        """Create a matched song entry."""
        match = MatchedSong(
            extraction_id=extraction_id,
            song_title=song_title,
            artist_name=artist_name,
            album_name=album_name,
            musicbrainz_id=musicbrainz_id,
            match_confidence=match_confidence,
            match_source=match_source,
            match_metadata=match_metadata,
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        return match

    @staticmethod
    def verify_match(db: Session, match_id: int, method: str):
        """Mark match as verified."""
        match = db.query(MatchedSong).filter(MatchedSong.id == match_id).first()
        if match:
            match.is_verified = True
            match.verification_method = method
            db.commit()


class RequestOperations:
    """Operations for song requests."""

    @staticmethod
    def create_request(
        db: Session, chat_id: str, matched_song_id: int, requested_by: str, priority: int = 1
    ) -> SongRequest:
        """Create a song request."""
        request = SongRequest(
            chat_id=chat_id,
            matched_song_id=matched_song_id,
            requested_by=requested_by,
            request_priority=priority,
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def get_pending_requests(db: Session, limit: int = 50) -> List[SongRequest]:
        """Get pending requests."""
        return (
            db.query(SongRequest)
            .filter(SongRequest.status == "pending")
            .order_by(desc(SongRequest.request_priority), SongRequest.created_at)
            .limit(limit)
            .all()
        )

    @staticmethod
    def approve_request(db: Session, request_id: int):
        """Approve a request."""
        request = db.query(SongRequest).filter(SongRequest.id == request_id).first()
        if request:
            request.status = "approved"
            request.updated_at = datetime.now(timezone.utc)
            db.commit()

    @staticmethod
    def reject_request(db: Session, request_id: int, notes: str = None):
        """Reject a request."""
        request = db.query(SongRequest).filter(SongRequest.id == request_id).first()
        if request:
            request.status = "rejected"
            if notes:
                request.notes = notes
            request.updated_at = datetime.now(timezone.utc)
            db.commit()

    @staticmethod
    def mark_queued(db: Session, request_id: int, radiodj_track_id: int = None):
        """Mark request as queued in RadioDJ."""
        request = db.query(SongRequest).filter(SongRequest.id == request_id).first()
        if request:
            request.status = "queued"
            if radiodj_track_id:
                request.radiodj_track_id = radiodj_track_id
            request.updated_at = datetime.now(timezone.utc)
            db.commit()

    @staticmethod
    def mark_played(db: Session, request_id: int):
        """Mark request as played."""
        request = db.query(SongRequest).filter(SongRequest.id == request_id).first()
        if request:
            request.status = "played"
            request.actual_play_time = datetime.now(timezone.utc)
            request.play_count += 1
            request.updated_at = datetime.now(timezone.utc)
            db.commit()
