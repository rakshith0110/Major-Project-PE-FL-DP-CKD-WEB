"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Authentication Models
class AdminLogin(BaseModel):
    username: str
    password: str

class ClientLogin(BaseModel):
    client_name: str
    password: str

class TrainingAuth(BaseModel):
    training_password: str

class AdminPasswordConfirm(BaseModel):
    password: str

# Client Management Models
class ClientCreate(BaseModel):
    client_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    login_password: str = Field(..., min_length=6)
    training_password: str = Field(..., min_length=6)
    description: Optional[str] = None

class ClientResponse(BaseModel):
    id: int
    client_name: str
    email: str
    description: Optional[str]
    status: str
    last_trained_time: Optional[datetime]
    update_status: str
    created_at: datetime

class ClientUpdate(BaseModel):
    client_name: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    login_password: Optional[str] = Field(default=None, min_length=6)
    training_password: Optional[str] = Field(default=None, min_length=6)
    description: Optional[str] = None
    status: Optional[str] = None

# Training Models
class TrainingConfig(BaseModel):
    epochs: int = Field(default=10, ge=1, le=100)
    batch_size: int = Field(default=32, ge=8, le=256)
    learning_rate: float = Field(default=0.001, ge=0.0001, le=0.1)
    noise_multiplier: float = Field(default=1.0, ge=0.1, le=10.0)
    max_grad_norm: float = Field(default=1.0, ge=0.1, le=10.0)

class TrainingRequest(BaseModel):
    training_password: str
    config: TrainingConfig

class TrainingResponse(BaseModel):
    status: str
    message: str
    training_id: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None

# Prediction Models
class PredictionRequest(BaseModel):
    patient_data: Dict[str, Any]

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    patient_data: Dict[str, Any]
    timestamp: datetime

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_count: int
    download_url: Optional[str] = None

# Aggregation Models
class AggregationRequest(BaseModel):
    client_ids: Optional[List[int]] = None  # If None, aggregate all with updates

class AggregationResponse(BaseModel):
    status: str
    message: str
    round_number: int
    clients_participated: List[str]
    previous_accuracy: Optional[float] = None
    global_accuracy: Optional[float] = None
    accuracy_improvement: Optional[float] = None
    global_loss: Optional[float] = None

class AggregationCandidate(BaseModel):
    client_id: int
    client_name: str
    email: str
    last_trained_time: Optional[datetime]
    update_status: str
    accuracy: Optional[float]
    loss: Optional[float]
    dataset_size: Optional[int]
    total_records_trained: int
    training_time: Optional[float]

# Metrics Models
class ClientMetrics(BaseModel):
    client_id: int
    client_name: str
    accuracy: Optional[float]
    loss: Optional[float]
    last_trained: Optional[datetime]
    update_status: str
    training_count: int

class GlobalMetrics(BaseModel):
    round_number: int
    accuracy: Optional[float]
    loss: Optional[float]
    total_clients: int
    active_clients: int
    last_aggregation: Optional[datetime]

# Visualization Models
class VisualizationData(BaseModel):
    type: str  # 'accuracy', 'loss', 'confusion_matrix', 'roc_curve'
    data: Dict[str, Any]
    image_url: Optional[str] = None

# Email Models
class EmailNotification(BaseModel):
    recipient_email: EmailStr
    subject: str
    message: str

# Audit Log Models
class AuditLog(BaseModel):
    user_type: str
    user_id: int
    action: str
    details: str
    ip_address: Optional[str] = None

# Dashboard Stats Models
class AdminDashboardStats(BaseModel):
    total_clients: int
    active_clients: int
    total_training_rounds: int
    global_model_accuracy: Optional[float]
    pending_updates: int
    last_aggregation: Optional[datetime]
    recent_activities: List[Dict[str, Any]]

class ClientDashboardStats(BaseModel):
    client_name: str
    total_trainings: int
    current_accuracy: Optional[float]
    current_loss: Optional[float]
    last_trained: Optional[datetime]
    update_status: str
    dataset_size: Optional[int]
    total_predictions: int
    total_records_trained: int

# File Upload Models
class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_size: int
    num_samples: Optional[int] = None
    message: str

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int
    user_name: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    user_type: Optional[str] = None
    username: Optional[str] = None

# Made with Bob
