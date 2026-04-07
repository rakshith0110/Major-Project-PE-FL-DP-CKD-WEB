"""
Database models for the application
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    HOSPITAL = "hospital"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.HOSPITAL, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")
    training_logs = relationship("TrainingLog", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_name = Column(String(100), unique=True, nullable=False)
    client_dir = Column(String(255), nullable=False)
    dataset_path = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="clients")
    training_logs = relationship("TrainingLog", back_populates="client", cascade="all, delete-orphan")
    models = relationship("ModelVersion", back_populates="client", cascade="all, delete-orphan")


class TrainingLog(Base):
    __tablename__ = "training_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"))
    training_type = Column(String(50))  # 'global', 'client', 'aggregation'
    status = Column(String(50))  # 'started', 'completed', 'failed'
    accuracy = Column(Float)
    f1_score = Column(Float)
    auc = Column(Float)
    loss = Column(Float)
    epochs = Column(Integer)
    batch_size = Column(Integer)
    learning_rate = Column(Float)
    n_samples = Column(Integer)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="training_logs")
    client = relationship("Client", back_populates="training_logs")


class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    model_type = Column(String(50))  # 'global', 'local', 'delta'
    version = Column(Integer, default=1)
    model_path = Column(String(255), nullable=False)
    accuracy = Column(Float)
    f1_score = Column(Float)
    auc = Column(Float)
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="models")


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"))
    patient_data = Column(Text)  # JSON string of patient features
    prediction_class = Column(Integer)  # 0 or 1
    prediction_label = Column(String(10))  # 'NO' or 'YES'
    prediction_probability = Column(Float)
    model_version = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="predictions")


class GlobalModel(Base):
    __tablename__ = "global_models"
    
    id = Column(Integer, primary_key=True, index=True)
    round_number = Column(Integer, default=0)
    model_path = Column(String(255), nullable=False)
    accuracy = Column(Float)
    f1_score = Column(Float)
    auc = Column(Float)
    num_clients = Column(Integer, default=0)
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Made with Bob
