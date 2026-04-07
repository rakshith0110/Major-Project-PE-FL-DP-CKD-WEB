"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from App.configs.config import settings
from App.database.database import init_db
from App.backend import auth_routes, client_routes, admin_routes, prediction_routes

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Privacy-Enhanced Federated Learning for Chronic Kidney Disease (CKD) Prediction",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create default admin user"""
    init_db()
    
    # Create default admin user if not exists
    from App.database.database import SessionLocal
    from App.database.models import User
    from App.utils.auth import get_password_hash
    
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@flckd.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin user created (username: admin, password: admin123)")
    finally:
        db.close()
    
    # Ensure required directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.SERVER_DIR, exist_ok=True)
    print("✅ Application initialized successfully")


# Include routers
app.include_router(auth_routes.router)
app.include_router(client_routes.router)
app.include_router(admin_routes.router)
app.include_router(prediction_routes.router)

# Mount static files for frontend
if os.path.exists("App/frontend/dist"):
    app.mount("/static", StaticFiles(directory="App/frontend/dist"), name="static")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse("App/frontend/dist/index.html")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Root endpoint
@app.get("/api")
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to FL-DP Healthcare CKD Prediction API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "App.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

# Made with Bob
