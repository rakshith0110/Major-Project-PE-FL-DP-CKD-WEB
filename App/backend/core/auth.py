"""
Authentication and authorization utilities
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.core.database import get_db_connection, hash_password

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production-2024-federated-learning-ckd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def authenticate_admin(username: str, password: str) -> Optional[Dict]:
    """Authenticate admin user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute("""
        SELECT id, username, email FROM admin 
        WHERE username = ? AND password_hash = ?
    """, (username, password_hash))
    
    admin = cursor.fetchone()
    conn.close()
    
    if admin:
        return {
            "id": admin["id"],
            "username": admin["username"],
            "email": admin["email"],
            "user_type": "admin"
        }
    return None

def authenticate_client(client_name: str, password: str) -> Optional[Dict]:
    """Authenticate client user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute("""
        SELECT id, client_name, email, status FROM clients 
        WHERE client_name = ? AND login_password_hash = ? AND status = 'active'
    """, (client_name, password_hash))
    
    client = cursor.fetchone()
    conn.close()
    
    if client:
        return {
            "id": client["id"],
            "client_name": client["client_name"],
            "email": client["email"],
            "user_type": "client"
        }
    return None

def verify_training_password(client_id: int, training_password: str) -> bool:
    """Verify client's training password"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(training_password)
    cursor.execute("""
        SELECT id FROM clients 
        WHERE id = ? AND training_password_hash = ?
    """, (client_id, password_hash))
    
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current authenticated user from token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("user_id")
    user_type = payload.get("user_type")
    
    if user_id is None or user_type is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return {
        "user_id": user_id,
        "user_type": user_type,
        "username": payload.get("username")
    }

async def require_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Require admin role"""
    if current_user["user_type"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def require_client(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Require client role"""
    if current_user["user_type"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client access required"
        )
    return current_user

def log_audit(user_type: str, user_id: int, action: str, details: str, ip_address: Optional[str] = None):
    """Log audit trail"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO audit_logs (user_type, user_id, action, details, ip_address)
        VALUES (?, ?, ?, ?, ?)
    """, (user_type, user_id, action, details, ip_address))
    
    conn.commit()
    conn.close()

# Made with Bob
