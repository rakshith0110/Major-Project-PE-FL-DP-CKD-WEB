"""
Prediction API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from App.database.database import get_db
from App.database.models import User, Client, Prediction
from App.models.schemas import PredictionRequest, PredictionResponse
from App.utils.auth import get_current_user
from App.services.ml_service import ml_service

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def make_prediction(
    prediction_request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Make a prediction on patient data"""
    # Get client
    client = db.query(Client).filter(Client.id == prediction_request.client_id).first()
    
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
    
    # Make prediction
    try:
        result = ml_service.predict(
            client_name=client.client_name,
            client_dir=client.client_dir,
            patient_data=prediction_request.patient_data
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error")
            )
        
        # Save prediction to database
        prediction = Prediction(
            user_id=current_user.id,
            client_id=client.id,
            patient_data=json.dumps(prediction_request.patient_data),
            prediction_class=result["prediction_class"],
            prediction_label=result["prediction_label"],
            prediction_probability=result["prediction_probability"],
            model_version=f"{client.client_name}_latest"
        )
        
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    client_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get prediction history"""
    query = db.query(Prediction)
    
    if current_user.role != "admin":
        query = query.filter(Prediction.user_id == current_user.id)
    
    if client_id:
        # Check if user has access to this client
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        if current_user.role != "admin" and client.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        query = query.filter(Prediction.client_id == client_id)
    
    predictions = query.order_by(Prediction.created_at.desc()).limit(100).all()
    return predictions


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific prediction"""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and prediction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return prediction

# Made with Bob
