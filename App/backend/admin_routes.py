"""
Admin API routes - Global model management and aggregation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import os
import pandas as pd
import asyncio
import json
import uuid

from App.database.database import get_db
from App.database.models import User, Client, TrainingLog, GlobalModel
from App.models.schemas import (
    GlobalTrainingRequest,
    AggregationRequest,
    TrainingResponse,
    GlobalModelResponse,
    DashboardStats,
    ClientStats
)
from App.utils.auth import get_current_admin_user
from App.utils.progress import progress_tracker
from App.services.ml_service import ml_service
from App.configs.config import settings

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/progress/{operation_id}")
async def get_operation_progress(
    operation_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get progress of a long-running operation"""
    progress = progress_tracker.get_progress(operation_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operation not found"
        )
    return progress


@router.post("/init-global-model")
async def initialize_global_model(
    training_request: GlobalTrainingRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Initialize global model (Admin only) - Returns operation ID for progress tracking"""
    operation_id = str(uuid.uuid4())
    
    # Create training log
    training_log = TrainingLog(
        user_id=current_user.id,
        training_type="global",
        status="started",
        epochs=training_request.epochs,
        batch_size=training_request.batch_size,
        learning_rate=training_request.learning_rate
    )
    db.add(training_log)
    db.commit()
    db.refresh(training_log)
    
    # Start progress tracking
    progress_tracker.start_operation(operation_id, "Initializing global model training...")
    
    # Train global model in background
    async def train_in_background():
        try:
            def progress_callback(message: str, percentage: int):
                progress_tracker.update_progress(operation_id, message, percentage)
            
            result = ml_service.train_global_model(
                epochs=training_request.epochs,
                batch_size=training_request.batch_size,
                learning_rate=training_request.learning_rate,
                progress_callback=progress_callback
            )
            
            if result["status"] == "success":
                metrics = result["metrics"]["val"]
                training_log.status = "completed"
                training_log.accuracy = metrics.get("accuracy")
                training_log.f1_score = metrics.get("f1")
                training_log.auc = metrics.get("auc")
                training_log.completed_at = pd.Timestamp.now()
                
                # Create global model record
                global_model = GlobalModel(
                    round_number=0,
                    model_path=result["model_path"],
                    accuracy=metrics.get("accuracy"),
                    f1_score=metrics.get("f1"),
                    auc=metrics.get("auc"),
                    num_clients=0,
                    is_current=True
                )
                db.add(global_model)
                progress_tracker.complete_operation(operation_id, "Global model training completed!")
            else:
                training_log.status = "failed"
                training_log.error_message = result.get("error")
                progress_tracker.fail_operation(operation_id, result.get("error", "Unknown error"))
            
            db.commit()
            db.refresh(training_log)
            
        except Exception as e:
            training_log.status = "failed"
            training_log.error_message = str(e)
            progress_tracker.fail_operation(operation_id, str(e))
            db.commit()
    
    # Start background task
    asyncio.create_task(train_in_background())
    
    return {"operation_id": operation_id, "status": "started", "message": "Training started in background"}


@router.post("/aggregate")
async def aggregate_models(
    aggregation_request: AggregationRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Perform federated aggregation (Admin only) - Returns operation ID for progress tracking"""
    operation_id = str(uuid.uuid4())
    
    # Get client directories
    clients = db.query(Client).filter(Client.id.in_(aggregation_request.client_ids)).all()
    
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No clients found"
        )
    
    client_dirs = [client.client_dir for client in clients]
    
    # Create training log
    training_log = TrainingLog(
        user_id=current_user.id,
        training_type="aggregation",
        status="started"
    )
    db.add(training_log)
    db.commit()
    db.refresh(training_log)
    
    # Start progress tracking
    progress_tracker.start_operation(operation_id, "Starting federated aggregation...")
    
    # Perform aggregation in background
    async def aggregate_in_background():
        try:
            def progress_callback(message: str, percentage: int):
                progress_tracker.update_progress(operation_id, message, percentage)
            
            result = ml_service.aggregate_models(client_dirs, progress_callback=progress_callback)
            
            if result["status"] == "success":
                metrics = result["metrics"]["val"]
                training_log.status = "completed"
                training_log.accuracy = metrics.get("accuracy")
                training_log.f1_score = metrics.get("f1")
                training_log.auc = metrics.get("auc")
                training_log.completed_at = pd.Timestamp.now()
                
                # Update global model record
                # Mark previous as not current
                db.query(GlobalModel).update({"is_current": False})
                
                # Get latest round number
                latest = db.query(GlobalModel).order_by(GlobalModel.round_number.desc()).first()
                next_round = (latest.round_number + 1) if latest else 1
                
                # Create new global model record
                global_model = GlobalModel(
                    round_number=next_round,
                    model_path=os.path.join(settings.SERVER_DIR, "global_final.pt"),
                    accuracy=metrics.get("accuracy"),
                    f1_score=metrics.get("f1"),
                    auc=metrics.get("auc"),
                    num_clients=result["num_clients"],
                    is_current=True
                )
                db.add(global_model)
                progress_tracker.complete_operation(operation_id, "Aggregation completed successfully!")
            else:
                training_log.status = "failed"
                training_log.error_message = result.get("error")
                progress_tracker.fail_operation(operation_id, result.get("error", "Unknown error"))
            
            db.commit()
            db.refresh(training_log)
            
        except Exception as e:
            training_log.status = "failed"
            training_log.error_message = str(e)
            progress_tracker.fail_operation(operation_id, str(e))
            db.commit()
    
    # Start background task
    asyncio.create_task(aggregate_in_background())
    
    return {"operation_id": operation_id, "status": "started", "message": "Aggregation started in background"}


@router.get("/dashboard-stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics (Admin only)"""
    from App.database.models import Prediction
    
    total_clients = db.query(Client).count()
    active_clients = db.query(Client).filter(Client.is_active == True).count()
    total_trainings = db.query(TrainingLog).count()
    total_predictions = db.query(Prediction).count()
    
    # Get latest global model metrics
    global_model = db.query(GlobalModel).filter(
        GlobalModel.is_current == True
    ).first()
    
    return DashboardStats(
        total_clients=total_clients,
        active_clients=active_clients,
        total_trainings=total_trainings,
        total_predictions=total_predictions,
        global_model_accuracy=global_model.accuracy if global_model else None,
        global_model_auc=global_model.auc if global_model else None
    )


@router.get("/client-stats", response_model=List[ClientStats])
async def get_client_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get statistics for all clients (Admin only)"""
    from App.database.models import Prediction
    from sqlalchemy import func
    
    clients = db.query(Client).all()
    stats = []
    
    for client in clients:
        # Get training count
        training_count = db.query(TrainingLog).filter(
            TrainingLog.client_id == client.id,
            TrainingLog.status == "completed"
        ).count()
        
        # Get latest training metrics
        latest_training = db.query(TrainingLog).filter(
            TrainingLog.client_id == client.id,
            TrainingLog.status == "completed"
        ).order_by(TrainingLog.completed_at.desc()).first()
        
        # Get prediction count
        prediction_count = db.query(Prediction).filter(
            Prediction.client_id == client.id
        ).count()
        
        stats.append(ClientStats(
            client_name=client.client_name,
            total_trainings=training_count,
            latest_accuracy=latest_training.accuracy if latest_training else None,
            latest_auc=latest_training.auc if latest_training else None,
            total_predictions=prediction_count
        ))
    
    return stats


@router.get("/global-models", response_model=List[GlobalModelResponse])
async def get_global_models(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all global model versions (Admin only)"""
    models = db.query(GlobalModel).order_by(GlobalModel.round_number.desc()).all()
    return models


@router.get("/training-logs", response_model=List[TrainingResponse])
async def get_all_training_logs(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all training logs (Admin only)"""
    logs = db.query(TrainingLog).order_by(TrainingLog.started_at.desc()).limit(100).all()
    return logs

# Made with Bob
