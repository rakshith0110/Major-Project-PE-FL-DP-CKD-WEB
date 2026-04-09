"""
Client API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

from backend.models.schemas import (
    ClientLogin, Token, TrainingRequest, TrainingResponse,
    PredictionRequest, PredictionResponse, BatchPredictionResponse,
    ClientDashboardStats, FileUploadResponse, TrainingConfig
)
from backend.core.auth import (
    authenticate_client, create_access_token, require_client,
    verify_training_password, log_audit
)
from backend.core.database import get_db_connection
from backend.services.fl_service import FederatedLearningService
from backend.services.email_service import email_service

router = APIRouter(prefix="/api/client", tags=["Client"])
fl_service = FederatedLearningService()

@router.post("/login", response_model=Token)
async def client_login(credentials: ClientLogin):
    """Client login endpoint"""
    client = authenticate_client(credentials.client_name, credentials.password)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client name or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "user_id": client["id"],
            "user_type": "client",
            "username": client["client_name"]
        }
    )
    
    log_audit("client", client["id"], "login", "Client logged in", None)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_type="client",
        user_id=client["id"],
        user_name=client["client_name"]
    )

@router.get("/dashboard/stats", response_model=ClientDashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(require_client)):
    """Get client dashboard statistics"""
    client_id = current_user["user_id"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get client info
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    
    # Total trainings
    cursor.execute("""
        SELECT COUNT(*) as count FROM training_logs
        WHERE client_id = ?
    """, (client_id,))
    total_trainings = cursor.fetchone()["count"]
    
    # Latest model metrics
    cursor.execute("""
        SELECT accuracy, loss FROM local_models
        WHERE client_id = ?
        ORDER BY created_at DESC LIMIT 1
    """, (client_id,))
    latest_model = cursor.fetchone()
    
    # Dataset size
    cursor.execute("""
        SELECT num_samples FROM client_datasets
        WHERE client_id = ?
        ORDER BY uploaded_at DESC LIMIT 1
    """, (client_id,))
    dataset = cursor.fetchone()
    
    # Total predictions
    cursor.execute("""
        SELECT COUNT(*) as count FROM predictions
        WHERE client_id = ?
    """, (client_id,))
    total_predictions = cursor.fetchone()["count"]
    
    conn.close()
    
    return ClientDashboardStats(
        client_name=client["client_name"],
        total_trainings=total_trainings,
        current_accuracy=latest_model["accuracy"] if latest_model else None,
        current_loss=latest_model["loss"] if latest_model else None,
        last_trained=client["last_trained_time"],
        update_status=client["update_status"],
        dataset_size=dataset["num_samples"] if dataset else None,
        total_predictions=total_predictions,
        total_records_trained=client["total_records_trained"] or 0
    )

@router.post("/upload-dataset", response_model=FileUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_client)
):
    """Upload client dataset"""
    client_id = current_user["user_id"]
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    try:
        # Save file
        uploads_dir = Path(__file__).parent.parent.parent / "uploads" / f"client_{client_id}"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = uploads_dir / f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Read and validate CSV
        df = pd.read_csv(file_path)
        num_samples = len(df)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO client_datasets (client_id, dataset_path, num_samples)
            VALUES (?, ?, ?)
        """, (client_id, str(file_path), num_samples))
        
        conn.commit()
        conn.close()
        
        log_audit(
            "client",
            client_id,
            "upload_dataset",
            f"Uploaded dataset with {num_samples} samples",
            None
        )
        
        return FileUploadResponse(
            filename=file.filename,
            file_path=str(file_path),
            file_size=len(content),
            num_samples=num_samples,
            message="Dataset uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload dataset: {str(e)}"
        )

@router.post("/train", response_model=TrainingResponse)
async def train_model(
    training_password: str = Form(...),
    epochs: int = Form(10),
    batch_size: int = Form(32),
    learning_rate: float = Form(0.001),
    noise_multiplier: float = Form(1.0),
    max_grad_norm: float = Form(1.0),
    current_user: dict = Depends(require_client)
):
    """Train local model with DP"""
    client_id = current_user["user_id"]
    
    # Verify training password
    if not verify_training_password(client_id, training_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid training password"
        )
    
    # Get latest dataset
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT dataset_path FROM client_datasets 
        WHERE client_id = ? 
        ORDER BY uploaded_at DESC LIMIT 1
    """, (client_id,))
    
    dataset = cursor.fetchone()
    
    if not dataset:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No dataset uploaded. Please upload a dataset first."
        )
    
    # Get client email
    cursor.execute("SELECT email, client_name FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    conn.close()
    
    # Send training started notification
    email_service.notify_training_started(
        client["email"],
        client["client_name"],
        epochs,
        batch_size
    )
    
    # Create config
    config = {
        'epochs': epochs,
        'batch_size': batch_size,
        'learning_rate': learning_rate,
        'noise_multiplier': noise_multiplier,
        'max_grad_norm': max_grad_norm
    }
    
    # Template CSV path (use main dataset)
    template_csv = str(Path(__file__).parent.parent.parent.parent / "Datasets" / "chronic_kidney_disease_5000.csv")
    
    # Train model
    result = fl_service.train_client_model(
        client_id=client_id,
        dataset_path=dataset["dataset_path"],
        config=config,
        template_csv=template_csv
    )
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    # Get admin email and notify
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM admin LIMIT 1")
    admin = cursor.fetchone()
    conn.close()
    
    if admin:
        email_service.notify_admin_training_complete(
            client["client_name"],
            result.get("accuracy", 0.0),
            admin["email"]
        )
    
    log_audit(
        "client",
        client_id,
        "train_model",
        f"Completed training with accuracy: {result.get('accuracy', 0):.2%}",
        None
    )
    
    return TrainingResponse(
        status=result["status"],
        message=result["message"],
        metrics=result.get("metrics")
    )

@router.post("/predict", response_model=PredictionResponse)
async def predict_single(
    prediction_data: PredictionRequest,
    current_user: dict = Depends(require_client)
):
    """Make single prediction"""
    client_id = current_user["user_id"]
    
    template_csv = str(Path(__file__).parent.parent.parent.parent / "Datasets" / "chronic_kidney_disease_5000.csv")
    
    result = fl_service.predict(
        client_id=client_id,
        patient_data=prediction_data.patient_data,
        template_csv=template_csv
    )
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    log_audit(
        "client",
        client_id,
        "predict",
        f"Made prediction: {result['prediction']}",
        None
    )
    
    return PredictionResponse(
        prediction=result["prediction"],
        confidence=result["confidence"],
        patient_data=result["patient_data"],
        timestamp=datetime.now()
    )

@router.post("/predict-batch")
async def predict_batch(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_client)
):
    """Make batch predictions from CSV"""
    client_id = current_user["user_id"]
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    try:
        # Read CSV
        content = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(content))
        
        template_csv = str(Path(__file__).parent.parent.parent.parent / "Datasets" / "chronic_kidney_disease_5000.csv")
        
        predictions = []
        for idx, row in df.iterrows():
            patient_data = row.to_dict()
            result = fl_service.predict(
                client_id=client_id,
                patient_data=patient_data,
                template_csv=template_csv
            )
            
            if result["status"] == "success":
                predictions.append({
                    "prediction": result["prediction"],
                    "confidence": result["confidence"],
                    "patient_data": patient_data
                })
        
        # Save predictions to CSV
        predictions_dir = Path(__file__).parent.parent.parent / "uploads" / f"client_{client_id}" / "predictions"
        predictions_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = predictions_dir / f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        predictions_df = pd.DataFrame(predictions)
        predictions_df.to_csv(output_file, index=False)
        
        log_audit(
            "client",
            client_id,
            "predict_batch",
            f"Made {len(predictions)} batch predictions",
            None
        )
        
        return {
            "status": "success",
            "total_predictions": len(predictions),
            "download_url": f"/api/client/download-predictions/{output_file.name}",
            "predictions": predictions[:10]  # Return first 10 for preview
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )

@router.get("/download-predictions/{filename}")
async def download_predictions(
    filename: str,
    current_user: dict = Depends(require_client)
):
    """Download prediction results"""
    client_id = current_user["user_id"]
    
    file_path = Path(__file__).parent.parent.parent / "uploads" / f"client_{client_id}" / "predictions" / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='text/csv'
    )

@router.get("/training-history")
async def get_training_history(current_user: dict = Depends(require_client)):
    """Get training history"""
    client_id = current_user["user_id"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, round_number, epochs, batch_size, learning_rate,
            noise_multiplier, max_grad_norm, accuracy, loss,
            training_time, dataset_size, completed_at
        FROM training_logs
        WHERE client_id = ?
        ORDER BY completed_at DESC
    """, (client_id,))
    
    history = []
    for row in cursor.fetchall():
        history.append({
            "id": row["id"],
            "round_number": row["round_number"],
            "epochs": row["epochs"],
            "batch_size": row["batch_size"],
            "learning_rate": row["learning_rate"],
            "noise_multiplier": row["noise_multiplier"],
            "max_grad_norm": row["max_grad_norm"],
            "accuracy": row["accuracy"],
            "loss": row["loss"],
            "training_time": row["training_time"],
            "dataset_size": row["dataset_size"],
            "completed_at": row["completed_at"]
        })
    
    conn.close()
    return history

@router.get("/prediction-history")
async def get_prediction_history(
    limit: int = 50,
    current_user: dict = Depends(require_client)
):
    """Get prediction history"""
    client_id = current_user["user_id"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id, patient_data_json, prediction_result, 
            confidence, created_at
        FROM predictions
        WHERE client_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (client_id, limit))
    
    history = []
    for row in cursor.fetchall():
        history.append({
            "id": row["id"],
            "patient_data": json.loads(row["patient_data_json"]),
            "prediction": row["prediction_result"],
            "confidence": row["confidence"],
            "timestamp": row["created_at"]
        })
    
    conn.close()
    return history

@router.get("/notifications")
async def get_notifications(current_user: dict = Depends(require_client)):
    """Get client notifications"""
    client_id = current_user["user_id"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT
            id, title, message, notification_type, is_read, created_at
        FROM client_notifications
        WHERE client_id = ?
        ORDER BY created_at DESC
        LIMIT 50
    """, (client_id,))
    
    notifications = []
    for row in cursor.fetchall():
        notifications.append({
            "id": row["id"],
            "title": row["title"],
            "message": row["message"],
            "type": row["notification_type"],
            "is_read": bool(row["is_read"]),
            "created_at": row["created_at"]
        })
    
    conn.close()
    return notifications

@router.get("/notifications/unread-count")
async def get_unread_count(current_user: dict = Depends(require_client)):
    """Get count of unread notifications"""
    client_id = current_user["user_id"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM client_notifications
        WHERE client_id = ? AND is_read = 0
    """, (client_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return {"unread_count": result["count"]}

@router.post("/notifications/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: int,
    current_user: dict = Depends(require_client)
):
    """Mark a notification as read"""
    client_id = current_user["user_id"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE client_notifications
        SET is_read = 1
        WHERE id = ? AND client_id = ?
    """, (notification_id, client_id))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Notification marked as read"}

@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(current_user: dict = Depends(require_client)):
    """Mark all notifications as read"""
    client_id = current_user["user_id"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE client_notifications
        SET is_read = 1
        WHERE client_id = ? AND is_read = 0
    """, (client_id,))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "All notifications marked as read"}

@router.get("/recent-activities")
async def get_recent_activities(
    limit: int = 10,
    current_user: dict = Depends(require_client)
):
    """Get recent activities for the client"""
    client_id = current_user["user_id"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT action, details, created_at
        FROM audit_logs
        WHERE user_type = 'client' AND user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (client_id, limit))
    
    activities = []
    for row in cursor.fetchall():
        activities.append({
            "action": row["action"],
            "details": row["details"],
            "timestamp": row["created_at"]
        })
    
    conn.close()
    return activities

@router.post("/delete-prediction-history")
async def delete_prediction_history(
    password: str = Form(...),
    current_user: dict = Depends(require_client)
):
    """Delete all prediction history for the client with password verification"""
    from backend.core.database import hash_password
    
    client_id = current_user["user_id"]
    
    # Verify password
    conn = get_db_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute("""
        SELECT id FROM clients
        WHERE id = ? AND login_password_hash = ?
    """, (client_id, password_hash))
    
    client = cursor.fetchone()
    
    if not client:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Delete all predictions for this client
    cursor.execute("DELETE FROM predictions WHERE client_id = ?", (client_id,))
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    log_audit(
        "client",
        client_id,
        "delete_prediction_history",
        f"Deleted {deleted_count} prediction records",
        None
    )
    
    return {
        "status": "success",
        "message": f"Successfully deleted {deleted_count} prediction records",
        "deleted_count": deleted_count
    }

# Made with Bob
