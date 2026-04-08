"""
Admin API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from datetime import datetime
import json

from backend.models.schemas import (
    AdminLogin, Token, ClientCreate, ClientResponse, ClientUpdate,
    AggregationRequest, AggregationResponse, AggregationCandidate, AdminDashboardStats,
    GlobalMetrics, ClientMetrics, AdminPasswordConfirm
)
from backend.core.auth import (
    authenticate_admin, create_access_token, require_admin,
    get_current_user, log_audit, hash_password
)
from backend.core.database import get_db_connection
from backend.services.fl_service import FederatedLearningService
from backend.services.email_service import email_service

router = APIRouter(prefix="/api/admin", tags=["Admin"])
fl_service = FederatedLearningService()

@router.post("/login", response_model=Token)
async def admin_login(credentials: AdminLogin):
    """Admin login endpoint"""
    admin = authenticate_admin(credentials.username, credentials.password)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "user_id": admin["id"],
            "user_type": "admin",
            "username": admin["username"]
        }
    )
    
    log_audit("admin", admin["id"], "login", "Admin logged in", None)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_type="admin",
        user_id=admin["id"],
        user_name=admin["username"]
    )

@router.get("/dashboard/stats", response_model=AdminDashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(require_admin)):
    """Get admin dashboard statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total clients
    cursor.execute("SELECT COUNT(*) as count FROM clients WHERE status = 'active'")
    total_clients = cursor.fetchone()["count"]
    
    # Active clients (trained in last 7 days)
    cursor.execute("""
        SELECT COUNT(*) as count FROM clients 
        WHERE status = 'active' 
        AND last_trained_time >= datetime('now', '-7 days')
    """)
    active_clients = cursor.fetchone()["count"]
    
    # Total training rounds
    cursor.execute("SELECT COUNT(*) as count FROM aggregation_logs")
    total_training_rounds = cursor.fetchone()["count"]
    
    # Global model accuracy
    cursor.execute("""
        SELECT accuracy FROM global_model 
        ORDER BY round_number DESC LIMIT 1
    """)
    result = cursor.fetchone()
    global_model_accuracy = result["accuracy"] if result else None
    
    # Pending updates
    cursor.execute("""
        SELECT COUNT(*) as count FROM clients 
        WHERE update_status = 'New Update Available'
    """)
    pending_updates = cursor.fetchone()["count"]
    
    # Last aggregation
    cursor.execute("""
        SELECT created_at FROM aggregation_logs 
        ORDER BY created_at DESC LIMIT 1
    """)
    result = cursor.fetchone()
    last_aggregation = result["created_at"] if result else None
    
    # Recent activities
    cursor.execute("""
        SELECT 
            al.action,
            al.details,
            al.created_at,
            CASE 
                WHEN al.user_type = 'admin' THEN a.username
                WHEN al.user_type = 'client' THEN c.client_name
            END as user_name
        FROM audit_logs al
        LEFT JOIN admin a ON al.user_type = 'admin' AND al.user_id = a.id
        LEFT JOIN clients c ON al.user_type = 'client' AND al.user_id = c.id
        ORDER BY al.created_at DESC
        LIMIT 10
    """)
    activities = []
    for row in cursor.fetchall():
        activities.append({
            "action": row["action"],
            "details": row["details"],
            "user_name": row["user_name"],
            "timestamp": row["created_at"]
        })
    
    conn.close()
    
    return AdminDashboardStats(
        total_clients=total_clients,
        active_clients=active_clients,
        total_training_rounds=total_training_rounds,
        global_model_accuracy=global_model_accuracy,
        pending_updates=pending_updates,
        last_aggregation=last_aggregation,
        recent_activities=activities
    )

@router.post("/clients", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    current_user: dict = Depends(require_admin)
):
    """Create a new client"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if client name or email already exists
        cursor.execute("""
            SELECT id FROM clients 
            WHERE client_name = ? OR email = ?
        """, (client_data.client_name, client_data.email))
        
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client name or email already exists"
            )
        
        # Hash passwords
        login_password_hash = hash_password(client_data.login_password)
        training_password_hash = hash_password(client_data.training_password)
        
        # Insert client
        cursor.execute("""
            INSERT INTO clients 
            (client_name, email, login_password_hash, training_password_hash, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            client_data.client_name,
            client_data.email,
            login_password_hash,
            training_password_hash,
            client_data.description
        ))
        
        client_id = cursor.lastrowid
        conn.commit()
        
        # Get created client
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        client = cursor.fetchone()
        
        # Email notifications disabled - using in-app notifications only
        
        log_audit(
            "admin",
            current_user["user_id"],
            "create_client",
            f"Created client: {client_data.client_name}",
            None
        )
        
        return ClientResponse(
            id=client["id"],
            client_name=client["client_name"],
            email=client["email"],
            description=client["description"],
            status=client["status"],
            last_trained_time=client["last_trained_time"],
            update_status=client["update_status"],
            created_at=client["created_at"]
        )
        
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        conn.close()

@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(current_user: dict = Depends(require_admin)):
    """List all clients"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM clients 
        ORDER BY created_at DESC
    """)
    
    clients = []
    for row in cursor.fetchall():
        clients.append(ClientResponse(
            id=row["id"],
            client_name=row["client_name"],
            email=row["email"],
            description=row["description"],
            status=row["status"],
            last_trained_time=row["last_trained_time"],
            update_status=row["update_status"],
            created_at=row["created_at"]
        ))
    
    conn.close()
    return clients

@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    current_user: dict = Depends(require_admin)
):
    """Get client details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    conn.close()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return ClientResponse(
        id=client["id"],
        client_name=client["client_name"],
        email=client["email"],
        description=client["description"],
        status=client["status"],
        last_trained_time=client["last_trained_time"],
        update_status=client["update_status"],
        created_at=client["created_at"]
    )

@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    current_user: dict = Depends(require_admin)
):
    """Update client details and passwords"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    existing_client = cursor.fetchone()

    if not existing_client:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    if client_data.client_name:
        cursor.execute("""
            SELECT id FROM clients
            WHERE client_name = ? AND id != ?
        """, (client_data.client_name, client_id))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client name already exists"
            )

    if client_data.email:
        cursor.execute("""
            SELECT id FROM clients
            WHERE email = ? AND id != ?
        """, (client_data.email, client_id))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

    update_fields = []
    update_values = []

    if client_data.client_name is not None:
        update_fields.append("client_name = ?")
        update_values.append(client_data.client_name)

    if client_data.email is not None:
        update_fields.append("email = ?")
        update_values.append(client_data.email)

    if client_data.description is not None:
        update_fields.append("description = ?")
        update_values.append(client_data.description)

    if client_data.status is not None:
        update_fields.append("status = ?")
        update_values.append(client_data.status)

    if client_data.login_password is not None:
        update_fields.append("login_password_hash = ?")
        update_values.append(hash_password(client_data.login_password))

    if client_data.training_password is not None:
        update_fields.append("training_password_hash = ?")
        update_values.append(hash_password(client_data.training_password))

    if not update_fields:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    update_values.append(client_id)

    cursor.execute(f"""
        UPDATE clients
        SET {', '.join(update_fields)}
        WHERE id = ?
    """, update_values)

    conn.commit()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    updated_client = cursor.fetchone()
    conn.close()

    log_audit(
        "admin",
        current_user["user_id"],
        "update_client",
        f"Updated client ID: {client_id}",
        None
    )

    return ClientResponse(
        id=updated_client["id"],
        client_name=updated_client["client_name"],
        email=updated_client["email"],
        description=updated_client["description"],
        status=updated_client["status"],
        last_trained_time=updated_client["last_trained_time"],
        update_status=updated_client["update_status"],
        created_at=updated_client["created_at"]
    )

@router.patch("/clients/{client_id}/status", response_model=ClientResponse)
async def update_client_status(
    client_id: int,
    client_data: ClientUpdate,
    current_user: dict = Depends(require_admin)
):
    """Activate or deactivate a client"""
    if client_data.status not in ["active", "inactive"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either 'active' or 'inactive'"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clients
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (client_data.status, client_id))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    conn.commit()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    conn.close()

    log_audit(
        "admin",
        current_user["user_id"],
        "update_client_status",
        f"Set client ID {client_id} status to {client_data.status}",
        None
    )

    return ClientResponse(
        id=client["id"],
        client_name=client["client_name"],
        email=client["email"],
        description=client["description"],
        status=client["status"],
        last_trained_time=client["last_trained_time"],
        update_status=client["update_status"],
        created_at=client["created_at"]
    )

@router.get("/clients-metrics", response_model=List[ClientMetrics])
async def get_clients_metrics(current_user: dict = Depends(require_admin)):
    """Get metrics for all clients"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT
            c.id,
            c.client_name,
            c.last_trained_time,
            c.update_status,
            lm.accuracy,
            lm.loss,
            COUNT(DISTINCT tl.id) as training_count
        FROM clients c
        LEFT JOIN local_models lm ON c.id = lm.client_id
            AND lm.id = (SELECT MAX(id) FROM local_models WHERE client_id = c.id)
        LEFT JOIN training_logs tl ON c.id = tl.client_id
        WHERE c.status = 'active'
        GROUP BY c.id
        ORDER BY c.client_name
    """)
    
    metrics = []
    for row in cursor.fetchall():
        metrics.append(ClientMetrics(
            client_id=row["id"],
            client_name=row["client_name"],
            accuracy=row["accuracy"],
            loss=row["loss"],
            last_trained=row["last_trained_time"],
            update_status=row["update_status"],
            training_count=row["training_count"]
        ))
    
    conn.close()
    return metrics

@router.get("/aggregation-candidates", response_model=List[AggregationCandidate])
async def get_aggregation_candidates(current_user: dict = Depends(require_admin)):
    """Get clients ready for aggregation"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.id as client_id,
            c.client_name,
            c.email,
            c.last_trained_time,
            c.update_status,
            c.total_records_trained,
            lm.accuracy,
            lm.loss,
            tl.dataset_size,
            tl.training_time
        FROM clients c
        LEFT JOIN local_models lm ON c.id = lm.client_id
            AND lm.id = (SELECT MAX(id) FROM local_models WHERE client_id = c.id)
        LEFT JOIN training_logs tl ON c.id = tl.client_id
            AND tl.id = (SELECT MAX(id) FROM training_logs WHERE client_id = c.id)
        WHERE c.status = 'active'
          AND c.update_status = 'New Update Available'
        ORDER BY c.last_trained_time DESC, c.client_name ASC
    """)

    candidates = []
    for row in cursor.fetchall():
        candidates.append(AggregationCandidate(
            client_id=row["client_id"],
            client_name=row["client_name"],
            email=row["email"],
            last_trained_time=row["last_trained_time"],
            update_status=row["update_status"],
            accuracy=row["accuracy"],
            loss=row["loss"],
            dataset_size=row["dataset_size"],
            total_records_trained=row["total_records_trained"] or 0,
            training_time=row["training_time"]
        ))

    conn.close()
    return candidates

@router.post("/global-model/reset")
async def reset_global_model(
    reset_request: AdminPasswordConfirm,
    current_user: dict = Depends(require_admin)
):
    """Reset global model after admin password confirmation"""
    admin = authenticate_admin(current_user["username"], reset_request.password)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM aggregation_logs")
    cursor.execute("DELETE FROM local_models")
    cursor.execute("DELETE FROM training_logs")
    cursor.execute("DELETE FROM global_model")
    cursor.execute("""
        INSERT INTO global_model (round_number, model_path, accuracy, loss, metrics_json)
        VALUES (?, ?, ?, ?, ?)
    """, (0, None, None, None, None))
    cursor.execute("""
        UPDATE clients
        SET last_trained_time = NULL,
            update_status = 'No Update',
            total_records_trained = 0,
            updated_at = CURRENT_TIMESTAMP
    """)

    conn.commit()
    conn.close()

    global_model_path = fl_service.get_global_model_path()
    scaler_path = fl_service.models_dir / "scaler.pkl"

    if global_model_path.exists():
        global_model_path.unlink()

    if scaler_path.exists():
        scaler_path.unlink()

    for client_dir in fl_service.models_dir.glob("client_*"):
        for model_file in client_dir.glob("*.pt"):
            model_file.unlink()

    log_audit(
        "admin",
        current_user["user_id"],
        "reset_global_model",
        "Reset global model, client local models, training logs, aggregation state, and client training totals",
        None
    )

    return {"status": "success", "message": "Global model reset successfully"}

@router.post("/initialize-global-model")
async def initialize_global_model(
    template_csv: str,
    admin_password: str,
    epochs: int = 30,
    batch_size: int = 64,
    lr: float = 0.001,
    current_user: dict = Depends(require_admin)
):
    """Initialize global model"""
    admin = authenticate_admin(current_user["username"], admin_password)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password"
        )

    result = fl_service.initialize_global_model(
        template_csv=template_csv,
        epochs=epochs,
        batch_size=batch_size,
        lr=lr
    )
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    log_audit(
        "admin",
        current_user["user_id"],
        "initialize_global_model",
        f"Initialized global model with accuracy: {result.get('accuracy', 0):.2%}",
        None
    )
    
    return result

@router.post("/aggregate", response_model=AggregationResponse)
async def aggregate_models(
    request: AggregationRequest,
    current_user: dict = Depends(require_admin)
):
    """Perform federated aggregation"""
    try:
        print(f"[AGGREGATION] Starting aggregation for client_ids: {request.client_ids}")
        print(f"[AGGREGATION] Current user: {current_user}")
        
        result = fl_service.aggregate_models(client_ids=request.client_ids)
        
        print(f"[AGGREGATION] Result status: {result['status']}")
        print(f"[AGGREGATION] Result: {result}")
        
        if result["status"] == "error":
            print(f"[AGGREGATION] Error occurred: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print("=" * 80)
        print("[AGGREGATION] EXCEPTION OCCURRED:")
        print(error_trace)
        print("=" * 80)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aggregation failed: {str(e)}"
        )
    
    # Get admin email
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM admin WHERE id = ?", (current_user["user_id"],))
    admin = cursor.fetchone()
    
    # Create in-app notifications for participating clients (email disabled)
    for client_name in result["clients_participated"]:
        cursor.execute("SELECT id, email FROM clients WHERE client_name = ?", (client_name,))
        client = cursor.fetchone()
        if client:
            # Create in-app notification only
            accuracy_text = f"Accuracy: {result.get('global_accuracy'):.2%}" if result.get('global_accuracy') is not None else "Accuracy: Pending evaluation"
            cursor.execute("""
                INSERT INTO client_notifications
                (client_id, title, message, notification_type)
                VALUES (?, ?, ?, ?)
            """, (
                client["id"],
                "Global Model Updated",
                f"Global model has been updated to Round {result['round_number']}. "
                f"{accuracy_text}. You can now download the latest model.",
                "success"
            ))
    
    cursor.execute("""
        INSERT INTO admin_notifications
        (title, message, notification_type)
        VALUES (?, ?, ?)
    """, (
        "Aggregation Completed",
        f"Round {result['round_number']} completed with {result['num_clients']} client(s): "
        f"{', '.join(result['clients_participated'])}.",
        "success"
    ))
    
    conn.commit()
    conn.close()
    
    log_audit(
        "admin",
        current_user["user_id"],
        "aggregate_models",
        f"Aggregated {result['num_clients']} clients in round {result['round_number']}",
        None
    )
    
    return AggregationResponse(
        status=result["status"],
        message=result["message"],
        round_number=result["round_number"],
        clients_participated=result["clients_participated"],
        previous_accuracy=result.get("previous_accuracy"),
        global_accuracy=result.get("global_accuracy"),
        accuracy_improvement=result.get("accuracy_improvement"),
        global_loss=result.get("global_loss")
    )

@router.get("/global-metrics", response_model=GlobalMetrics)
async def get_global_metrics(current_user: dict = Depends(require_admin)):
    """Get global model metrics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Latest global model
    cursor.execute("""
        SELECT round_number, accuracy, loss, created_at
        FROM global_model
        ORDER BY round_number DESC
        LIMIT 1
    """)
    global_model = cursor.fetchone()
    
    # Client counts
    cursor.execute("SELECT COUNT(*) as count FROM clients WHERE status = 'active'")
    total_clients = cursor.fetchone()["count"]
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM clients 
        WHERE status = 'active' 
        AND last_trained_time >= datetime('now', '-7 days')
    """)
    active_clients = cursor.fetchone()["count"]
    
    # Last aggregation
    cursor.execute("""
        SELECT created_at FROM aggregation_logs 
        ORDER BY created_at DESC LIMIT 1
    """)
    agg = cursor.fetchone()
    
    conn.close()
    
    return GlobalMetrics(
        round_number=global_model["round_number"] if global_model else 0,
        accuracy=global_model["accuracy"] if global_model else None,
        loss=global_model["loss"] if global_model else None,
        total_clients=total_clients,
        active_clients=active_clients,
        last_aggregation=agg["created_at"] if agg else None
    )

@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: int,
    current_user: dict = Depends(require_admin)
):
    """Permanently delete a client"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT client_name FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()

    if not client:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    cursor.execute("DELETE FROM client_notifications WHERE client_id = ?", (client_id,))
    cursor.execute("DELETE FROM client_datasets WHERE client_id = ?", (client_id,))
    cursor.execute("DELETE FROM predictions WHERE client_id = ?", (client_id,))
    cursor.execute("DELETE FROM local_models WHERE client_id = ?", (client_id,))
    cursor.execute("DELETE FROM training_logs WHERE client_id = ?", (client_id,))
    cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))

    conn.commit()
    conn.close()

    log_audit(
        "admin",
        current_user["user_id"],
        "delete_client",
        f"Deleted client: {client['client_name']} (ID: {client_id})",
        None
    )

    return {"message": "Client deleted successfully"}

@router.get("/notifications")
async def get_admin_notifications(current_user: dict = Depends(require_admin)):
    """Get admin notifications"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, message, notification_type, is_read, created_at
        FROM admin_notifications
        ORDER BY created_at DESC
        LIMIT 50
    """)

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
async def get_admin_unread_count(current_user: dict = Depends(require_admin)):
    """Get count of unread admin notifications"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) as count
        FROM admin_notifications
        WHERE is_read = 0
    """)

    result = cursor.fetchone()
    conn.close()

    return {"unread_count": result["count"]}

@router.post("/notifications/{notification_id}/mark-read")
async def mark_admin_notification_read(
    notification_id: int,
    current_user: dict = Depends(require_admin)
):
    """Mark an admin notification as read"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE admin_notifications
        SET is_read = 1
        WHERE id = ?
    """, (notification_id,))

    conn.commit()
    conn.close()

    return {"status": "success", "message": "Notification marked as read"}

@router.post("/notifications/mark-all-read")
async def mark_all_admin_notifications_read(current_user: dict = Depends(require_admin)):
    """Mark all admin notifications as read"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE admin_notifications
        SET is_read = 1
        WHERE is_read = 0
    """)

    conn.commit()
    conn.close()

    return {"status": "success", "message": "All notifications marked as read"}

@router.get("/aggregation-history")
async def get_aggregation_history(current_user: dict = Depends(require_admin)):
    """Get aggregation history with details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT
            al.id,
            al.round_number,
            al.clients_participated,
            al.num_clients,
            al.previous_accuracy,
            al.global_accuracy,
            al.accuracy_improvement,
            al.global_loss,
            al.aggregation_time,
            al.metrics_json,
            al.created_at
        FROM aggregation_logs al
        ORDER BY al.round_number DESC
        LIMIT 100
    """)
    
    history = []
    for row in cursor.fetchall():
        # Parse clients_participated (can be JSON array or comma-separated string)
        clients_list = []
        if row["clients_participated"]:
            try:
                # Try parsing as JSON first
                clients_list = json.loads(row["clients_participated"])
            except:
                # Fall back to comma-separated string
                clients_list = row["clients_participated"].split(",")
        
        # Parse metrics_json if available
        metrics = None
        if row["metrics_json"]:
            try:
                metrics = json.loads(row["metrics_json"])
            except:
                metrics = None
        
        # Use stored accuracy_improvement or calculate if not available
        accuracy_improvement = row["accuracy_improvement"]
        if accuracy_improvement is None and row["global_accuracy"] is not None and row["previous_accuracy"] is not None:
            accuracy_improvement = row["global_accuracy"] - row["previous_accuracy"]
        
        # Calculate improvement percentage
        accuracy_improvement_percentage = None
        if accuracy_improvement is not None and row["previous_accuracy"] is not None and row["previous_accuracy"] > 0:
            accuracy_improvement_percentage = (accuracy_improvement / row["previous_accuracy"]) * 100
        
        history.append({
            "id": row["id"],
            "round_number": row["round_number"],
            "clients_participated": clients_list,
            "num_clients": row["num_clients"],
            "previous_accuracy": row["previous_accuracy"],
            "global_accuracy": row["global_accuracy"],
            "accuracy_improvement": accuracy_improvement,
            "accuracy_improvement_percentage": accuracy_improvement_percentage,
            "global_loss": row["global_loss"],
            "aggregation_time": row["aggregation_time"],
            "metrics": metrics,
            "created_at": row["created_at"]
        })
    
    conn.close()
    return history

# Made with Bob
