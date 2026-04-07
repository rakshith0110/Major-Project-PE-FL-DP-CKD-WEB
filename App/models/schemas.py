"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    HOSPITAL = "hospital"


# ============= Auth Schemas =============
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: UserRole = UserRole.HOSPITAL


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Client Schemas =============
class ClientCreate(BaseModel):
    client_name: str = Field(..., min_length=3, max_length=100)
    dataset_path: Optional[str] = None


class ClientResponse(BaseModel):
    id: int
    user_id: int
    client_name: str
    client_dir: str
    dataset_path: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Training Schemas =============
class GlobalTrainingRequest(BaseModel):
    epochs: int = Field(default=30, ge=1, le=200)
    batch_size: int = Field(default=64, ge=8, le=512)
    learning_rate: float = Field(default=0.001, gt=0, lt=1)


class ClientTrainingRequest(BaseModel):
    client_id: int
    local_epochs: int = Field(default=10, ge=1, le=100)
    batch_size: int = Field(default=64, ge=8, le=512)
    learning_rate: float = Field(default=0.001, gt=0, lt=1)
    max_grad_norm: float = Field(default=1.0, gt=0)
    noise_multiplier: float = Field(default=0.8, gt=0)


class AggregationRequest(BaseModel):
    client_ids: List[int] = Field(..., min_items=1)


class TrainingResponse(BaseModel):
    id: int
    training_type: str
    status: str
    accuracy: Optional[float]
    f1_score: Optional[float]
    auc: Optional[float]
    loss: Optional[float]
    epochs: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============= Prediction Schemas =============
class PredictionRequest(BaseModel):
    client_id: int
    patient_data: dict  # Feature values


class PredictionResponse(BaseModel):
    id: int
    prediction_class: int
    prediction_label: str
    prediction_probability: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Model Schemas =============
class ModelVersionResponse(BaseModel):
    id: int
    model_type: str
    version: int
    accuracy: Optional[float]
    f1_score: Optional[float]
    auc: Optional[float]
    is_current: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class GlobalModelResponse(BaseModel):
    id: int
    round_number: int
    accuracy: Optional[float]
    f1_score: Optional[float]
    auc: Optional[float]
    num_clients: int
    is_current: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Dashboard Schemas =============
class DashboardStats(BaseModel):
    total_clients: int
    active_clients: int
    total_trainings: int
    total_predictions: int
    global_model_accuracy: Optional[float]
    global_model_auc: Optional[float]


class ClientStats(BaseModel):
    client_name: str
    total_trainings: int
    latest_accuracy: Optional[float]
    latest_auc: Optional[float]
    total_predictions: int


# ============= File Upload Schemas =============
class DatasetUploadResponse(BaseModel):
    filename: str
    file_path: str
    size: int
    rows: int
    columns: int
    message: str

# Made with Bob
