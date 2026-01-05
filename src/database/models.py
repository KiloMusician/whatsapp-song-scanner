"""Database models for WhatsApp Song Scanner."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from config.database import Base, engine

class WhatsAppChat(Base):
    """WhatsApp chat tracking."""
    __tablename__ = 'whatsapp_chats'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(String(255), unique=True, nullable=False, index=True)
    chat_name = Column(String(255))
    last_message_id = Column(String(255))
    last_scan_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    messages = relationship('ChatMessage', back_populates='chat', cascade='all, delete-orphan')
    song_requests = relationship('SongRequest', back_populates='chat', cascade='all, delete-orphan')

class ChatMessage(Base):
    """Individual WhatsApp messages."""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(255), unique=True, nullable=False, index=True)
    chat_id = Column(String(255), ForeignKey('whatsapp_chats.chat_id'), nullable=False)
    sender_number = Column(String(50))
    sender_name = Column(String(255))
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text)
    timestamp = Column(DateTime, nullable=False, index=True)
    is_processed = Column(Boolean, default=False)
    processing_attempts = Column(Integer, default=0)
    processing_error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # RELATIONSHIPS
    chat = relationship('WhatsAppChat', back_populates='messages')
    extracted_songs = relationship('ExtractedSong', back_populates='message', cascade='all, delete-orphan')

class ExtractedSong(Base):
    """Songs extracted from messages."""
    __tablename__ = 'extracted_songs'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('chat_messages.id'), nullable=False)
    original_phrase = Column(String(500), nullable=False)
    confidence_score = Column(Float)
    extraction_method = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # RELATIONSHIPS
    message = relationship('ChatMessage', back_populates='extracted_songs')
    matched_results = relationship('MatchedSong', back_populates='extraction', cascade='all, delete-orphan')

class MatchedSong(Base):
    """Verified song matches from APIs."""
    __tablename__ = 'matched_songs'
    
    id = Column(Integer, primary_key=True)
    extraction_id = Column(Integer, ForeignKey('extracted_songs.id'), nullable=False)
    song_title = Column(String(500), nullable=False, index=True)
    artist_name = Column(String(500), index=True)
    album_name = Column(String(500))
    musicbrainz_id = Column(String(255), index=True)
    spotify_id = Column(String(255))
    deezer_id = Column(String(255))
    match_confidence = Column(Float)
    match_source = Column(String(50))
    match_metadata = Column(JSON)
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # RELATIONSHIPS
    extraction = relationship('ExtractedSong', back_populates='matched_results')
    requests = relationship('SongRequest', back_populates='matched_song', cascade='all, delete-orphan')

class SongRequest(Base):
    """Final song requests for RadioDJ."""
    __tablename__ = 'song_requests'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(String(255), ForeignKey('whatsapp_chats.chat_id'), nullable=False)
    matched_song_id = Column(Integer, ForeignKey('matched_songs.id'), nullable=False)
    requested_by = Column(String(255))
    request_priority = Column(Integer, default=1)
    status = Column(String(50), default='pending', index=True)  # pending, approved, queued, played, rejected
    radiodj_playlist_id = Column(Integer)
    radiodj_track_id = Column(Integer)
    scheduled_play_time = Column(DateTime)
    actual_play_time = Column(DateTime)
    play_count = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIPS
    chat = relationship('WhatsAppChat', back_populates='song_requests')
    matched_song = relationship('MatchedSong', back_populates='requests')

def init_database():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def drop_all_tables():
    """Drop all database tables (use with caution)."""
    Base.metadata.drop_all(bind=engine)
    print("All database tables dropped")
