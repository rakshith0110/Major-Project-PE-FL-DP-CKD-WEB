"""
Client management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import pandas as pd

from App.database.database import get_db
from App.database.models import User, Client, TrainingLog
from App.models.schemas import (
    ClientCreate,
    ClientResponse,
    ClientTrainingRequest,
    TrainingResponse,
    DatasetUploadResponse
)
from App.utils.auth import get_current_user
from App.services.ml_service import ml_service
from App.configs.config import settings

router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new client (hospital)"""
    # Check if client name already exists
    if db.query(Client).filter(Client.client_name == client_data.client_name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client name already exists"
        )
    
    # Create client directory
    client_dir = os.path.join(settings.CLIENTS_BASE_DIR, client_data.client_name.lower())
    os.makedirs(client_dir, exist_ok=True)
    os.makedirs(os.path.join(client_dir, "dataset"), exist_ok=True)
    
    # Create client record
    new_client = Client(
        user_id=current_user.id,
        client_name=client_data.client_name,
        client_dir=client_dir,
        dataset_path=client_data.dataset_path
    )
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    return new_client


@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all clients for current user"""
    if current_user.role == "admin":
        clients = db.query(Client).all()
    else:
        clients = db.query(Client).filter(Client.user_id == current_user.id).all()
    
    return clients


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get client details"""
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and client.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return client


@router.post("/{client_id}/upload-dataset", response_model=DatasetUploadResponse)
async def upload_dataset(
    client_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload dataset for a client"""
    # Get client
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and client.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Save file
    dataset_dir = os.path.join(client.client_dir, "dataset")
    os.makedirs(dataset_dir, exist_ok=True)
    
    file_path = os.path.join(dataset_dir, f"{client.client_name.lower()}_ckd.csv")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Read and validate CSV
    try:
        df = pd.read_csv(file_path)
        rows = len(df)
        columns = len(df.columns)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV file: {str(e)}"
        )
    
    # Update client record
    client.dataset_path = file_path
    db.commit()
    
    return DatasetUploadResponse(
        filename=file.filename,
        file_path=file_path,
        size=os.path.getsize(file_path),
        rows=rows,
        columns=columns,
        message="Dataset uploaded successfully"
    )


@router.post("/{client_id}/train", response_model=TrainingResponse)
async def train_client(
    client_id: int,
    training_request: ClientTrainingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train client model"""
    # Get client
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and client.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if dataset exists
    if not client.dataset_path or not os.path.exists(client.dataset_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset not uploaded. Please upload dataset first."
        )
    
    # Create training log
    training_log = TrainingLog(
        user_id=current_user.id,
        client_id=client.id,
        training_type="client",
        status="started",
        epochs=training_request.local_epochs,
        batch_size=training_request.batch_size,
        learning_rate=training_request.learning_rate
    )
    db.add(training_log)
    db.commit()
    db.refresh(training_log)
    
    # Train model
    try:
        result = ml_service.train_client_model(
            client_name=client.client_name,
            client_dir=client.client_dir,
            client_csv=client.dataset_path,
            local_epochs=training_request.local_epochs,
            batch_size=training_request.batch_size,
            learning_rate=training_request.learning_rate,
            max_grad_norm=training_request.max_grad_norm,
            noise_multiplier=training_request.noise_multiplier
        )
        
        if result["status"] == "success":
            metrics = result["metrics"]["val"]
            training_log.status = "completed"
            training_log.accuracy = metrics.get("accuracy")
            training_log.f1_score = metrics.get("f1")
            training_log.auc = metrics.get("auc")
            training_log.n_samples = result["metrics"].get("n_samples")
            training_log.completed_at = pd.Timestamp.now()
        else:
            training_log.status = "failed"
            training_log.error_message = result.get("error")
        
        db.commit()
        db.refresh(training_log)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error")
            )
        
        return training_log
        
    except Exception as e:
        training_log.status = "failed"
        training_log.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{client_id}/training-history", response_model=List[TrainingResponse])
async def get_training_history(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get training history for a client"""
    # Get client
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and client.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    training_logs = db.query(TrainingLog).filter(
        TrainingLog.client_id == client_id
    ).order_by(TrainingLog.started_at.desc()).all()
    
    return training_logs

# Made with Bob
