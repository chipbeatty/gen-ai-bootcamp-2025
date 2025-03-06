from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pydantic import BaseModel

Base = declarative_base()

# Pydantic models for serialization
class ConversationSchema(BaseModel):
    id: Optional[int] = None
    title: str
    created_at: datetime
    messages: Dict[str, Any]
    model_settings: Dict[str, Any]
    user_id: str
    
    class Config:
        from_attributes = True

class VoicePreferenceSchema(BaseModel):
    id: Optional[int] = None
    user_id: str
    voice_id: str
    speaking_rate: float
    pitch: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Conversation(Base):
    """Store conversation history"""
    __tablename__ = 'conversation'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = Column(JSON)
    model_settings = Column(JSON)
    user_id = Column(String)  # Could be IP or session ID for now

class VoicePreference(Base):
    """Store user voice preferences"""
    __tablename__ = 'voice_preference'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    voice_id = Column(String, default="en-US-Neural2-H")
    speaking_rate = Column(Float, default=1.0)
    pitch = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database URL from environment or default to SQLite
DATABASE_URL = "sqlite:///./voicechat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create tables
Base.metadata.create_all(engine)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseService:
    @staticmethod
    async def save_conversation(user_id: str, title: str, messages: Dict[str, Any], model_settings: Dict[str, Any]) -> ConversationSchema:
        conversation = Conversation(
            user_id=user_id,
            title=title,
            messages=messages,
            model_settings=model_settings
        )
        db = SessionLocal()
        try:
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return ConversationSchema.from_orm(conversation)
        finally:
            db.close()

    @staticmethod
    async def get_conversations(user_id: str) -> List[ConversationSchema]:
        db = SessionLocal()
        try:
            conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
            return [ConversationSchema.from_orm(conv) for conv in conversations]
        finally:
            db.close()

    @staticmethod
    async def save_voice_preference(user_id: str, voice_id: str, speaking_rate: float, pitch: float) -> VoicePreferenceSchema:
        db = SessionLocal()
        try:
            # Update if exists, create if not
            preference = db.query(VoicePreference).filter(VoicePreference.user_id == user_id).first()
            
            if preference:
                preference.voice_id = voice_id
                preference.speaking_rate = speaking_rate
                preference.pitch = pitch
                preference.updated_at = datetime.utcnow()
            else:
                preference = VoicePreference(
                    user_id=user_id,
                    voice_id=voice_id,
                    speaking_rate=speaking_rate,
                    pitch=pitch
                )
                db.add(preference)
            
            db.commit()
            db.refresh(preference)
            return VoicePreferenceSchema.from_orm(preference)
        finally:
            db.close()

    @staticmethod
    async def get_voice_preference(user_id: str) -> VoicePreferenceSchema:
        db = SessionLocal()
        try:
            preference = db.query(VoicePreference).filter(VoicePreference.user_id == user_id).first()
            if preference:
                return VoicePreferenceSchema.from_orm(preference)
            else:
                # Return default preferences
                return VoicePreferenceSchema(
                    user_id=user_id,
                    voice_id="en-US-Neural2-H",
                    speaking_rate=1.0,
                    pitch=0.0,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
        finally:
            db.close()
