"""Unit tests for database operations."""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, WhatsAppChat, ChatMessage, ExtractedSong, MatchedSong, SongRequest
from src.database.operations import ChatOperations, MessageOperations, SongOperations, RequestOperations


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestChatOperations:
    """Test chat operations."""
    
    def test_create_chat(self, db_session):
        """Test chat creation."""
        chat = ChatOperations.create_or_update_chat(
            db_session,
            chat_id='test@whatsapp',
            chat_name='Test Chat'
        )
        
        assert chat is not None
        assert chat.chat_id == 'test@whatsapp'
        assert chat.chat_name == 'Test Chat'
        assert chat.is_active == True
    
    def test_get_active_chats(self, db_session):
        """Test getting active chats."""
        ChatOperations.create_or_update_chat(db_session, 'chat1@whatsapp')
        ChatOperations.create_or_update_chat(db_session, 'chat2@whatsapp')
        
        active = ChatOperations.get_active_chats(db_session)
        assert len(active) == 2


class TestMessageOperations:
    """Test message operations."""
    
    def test_create_message(self, db_session):
        """Test message creation."""
        # Create chat first
        ChatOperations.create_or_update_chat(db_session, 'test@whatsapp')
        
        message = MessageOperations.create_message(
            db_session,
            message_id='msg123',
            chat_id='test@whatsapp',
            sender_number='+1234567890',
            sender_name='Test User',
            raw_text='Test message',
            timestamp=datetime.utcnow()
        )
        
        assert message is not None
        assert message.message_id == 'msg123'
        assert message.raw_text == 'Test message'
    
    def test_mark_processed(self, db_session):
        """Test marking message as processed."""
        ChatOperations.create_or_update_chat(db_session, 'test@whatsapp')
        
        message = MessageOperations.create_message(
            db_session,
            message_id='msg123',
            chat_id='test@whatsapp',
            sender_number='+1234567890',
            sender_name='Test',
            raw_text='Test',
            timestamp=datetime.utcnow()
        )
        
        MessageOperations.mark_processed(db_session, message.id, 'cleaned text')
        
        db_session.refresh(message)
        assert message.is_processed == True
        assert message.cleaned_text == 'cleaned text'


class TestSongOperations:
    """Test song operations."""
    
    def test_create_extraction(self, db_session):
        """Test creating song extraction."""
        ChatOperations.create_or_update_chat(db_session, 'test@whatsapp')
        
        message = MessageOperations.create_message(
            db_session,
            message_id='msg123',
            chat_id='test@whatsapp',
            sender_number='+1234567890',
            sender_name='Test',
            raw_text='play test song',
            timestamp=datetime.utcnow()
        )
        
        extraction = SongOperations.create_extraction(
            db_session,
            message_id=message.id,
            original_phrase='test song',
            confidence_score=0.85,
            extraction_method='test_method'
        )
        
        assert extraction is not None
        assert extraction.original_phrase == 'test song'
        assert extraction.confidence_score == 0.85
    
    def test_create_match(self, db_session):
        """Test creating matched song."""
        ChatOperations.create_or_update_chat(db_session, 'test@whatsapp')
        
        message = MessageOperations.create_message(
            db_session,
            message_id='msg123',
            chat_id='test@whatsapp',
            sender_number='+1234567890',
            sender_name='Test',
            raw_text='play test song',
            timestamp=datetime.utcnow()
        )
        
        extraction = SongOperations.create_extraction(
            db_session,
            message_id=message.id,
            original_phrase='test song',
            confidence_score=0.85,
            extraction_method='test'
        )
        
        match = SongOperations.create_match(
            db_session,
            extraction_id=extraction.id,
            song_title='Test Song',
            artist_name='Test Artist',
            match_confidence=0.90,
            match_source='test'
        )
        
        assert match is not None
        assert match.song_title == 'Test Song'
        assert match.artist_name == 'Test Artist'


class TestRequestOperations:
    """Test request operations."""
    
    def test_create_request(self, db_session):
        """Test creating song request."""
        ChatOperations.create_or_update_chat(db_session, 'test@whatsapp')
        
        message = MessageOperations.create_message(
            db_session,
            message_id='msg123',
            chat_id='test@whatsapp',
            sender_number='+1234567890',
            sender_name='Test',
            raw_text='play test',
            timestamp=datetime.utcnow()
        )
        
        extraction = SongOperations.create_extraction(
            db_session,
            message_id=message.id,
            original_phrase='test',
            confidence_score=0.85,
            extraction_method='test'
        )
        
        match = SongOperations.create_match(
            db_session,
            extraction_id=extraction.id,
            song_title='Test',
            artist_name='Test',
            match_confidence=0.90,
            match_source='test'
        )
        
        request = RequestOperations.create_request(
            db_session,
            chat_id='test@whatsapp',
            matched_song_id=match.id,
            requested_by='Test User'
        )
        
        assert request is not None
        assert request.status == 'pending'
    
    def test_approve_request(self, db_session):
        """Test approving request."""
        ChatOperations.create_or_update_chat(db_session, 'test@whatsapp')
        
        message = MessageOperations.create_message(
            db_session,
            message_id='msg123',
            chat_id='test@whatsapp',
            sender_number='+1234567890',
            sender_name='Test',
            raw_text='test',
            timestamp=datetime.utcnow()
        )
        
        extraction = SongOperations.create_extraction(
            db_session,
            message_id=message.id,
            original_phrase='test',
            confidence_score=0.85,
            extraction_method='test'
        )
        
        match = SongOperations.create_match(
            db_session,
            extraction_id=extraction.id,
            song_title='Test',
            artist_name='Test',
            match_confidence=0.90,
            match_source='test'
        )
        
        request = RequestOperations.create_request(
            db_session,
            chat_id='test@whatsapp',
            matched_song_id=match.id,
            requested_by='Test'
        )
        
        RequestOperations.approve_request(db_session, request.id)
        
        db_session.refresh(request)
        assert request.status == 'approved'
