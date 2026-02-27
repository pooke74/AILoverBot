from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    credits = Column(Integer, default=50)
    is_vip = Column(Boolean, default=False)
    selected_character = Column(String, default='mia')
    last_active = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Sprint 2: Gunluk ucretsiz mesaj
    daily_free_remaining = Column(Integer, default=5)     # Kalan gunluk bedava mesaj
    daily_free_reset_date = Column(String, default='')    # Son sifirlama tarihi (YYYY-MM-DD)
    
    # Sprint 2: Flort seviyesi
    intimacy_level = Column(Integer, default=1)           # 1-5 arasi yakinlik seviyesi
    total_messages_sent = Column(Integer, default=0)      # Toplam gonderilen mesaj
    
    # Sprint 2: Referral
    referral_code = Column(String, default='')             # Kullanicinin davet kodu
    referred_by = Column(String, nullable=True)            # Kim davet etti
    referral_count = Column(Integer, default=0)            # Kac kisi davet etti
    
    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    character_id = Column(String, default='mia')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="messages")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer, nullable=False)
    price_label = Column(String, nullable=True)
    payment_method = Column(String, default='stars')
    telegram_payment_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///ailover.db'), echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def generate_referral_code():
    """Benzersiz 6 haneli referral kodu uretir."""
    return uuid.uuid4().hex[:6].upper()
