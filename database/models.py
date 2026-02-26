from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os
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
    selected_character = Column(String, default='mia')  # Aktif karakter ID'si
    last_active = Column(DateTime, default=datetime.utcnow)  # Proaktif mesaj için
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    role = Column(String, nullable=False)  # 'user' veya 'assistant'
    content = Column(Text, nullable=False)
    character_id = Column(String, default='mia')  # Hangi karakter cevapladı
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="messages")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer, nullable=False)       # Yüklenen kredi
    price_label = Column(String, nullable=True)     # "100 Kredi - 50 TL"
    payment_method = Column(String, default='stars') # 'stars', 'crypto', 'test'
    telegram_payment_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///ailover.db'), echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
