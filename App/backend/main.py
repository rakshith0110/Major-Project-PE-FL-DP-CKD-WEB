"""
Main FastAPI application for Federated Learning CKD System
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import uvicorn

from backend.api import admin_routes, client_routes
from backend.core.database import init_database

# Initialize database
init_database()

# Create FastAPI app
app = FastAPI(
    title="Federated Learning CKD System",
    description="Privacy-Enhanced Federated Learning for Chronic Kidney Disease",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_routes.router)
app.include_router(client_routes.router)

# Mount static files
static_path = Path(__file__).parent.parent / "frontend" / "static"
templates_path = Path(__file__).parent.parent / "frontend" / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - Landing page"""
    index_file = templates_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Federated Learning CKD System</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                background: white;
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 600px;
            }
            h1 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 2.5em;
            }
            p {
                color: #666;
                font-size: 1.2em;
                margin-bottom: 30px;
            }
            .buttons {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }
            .btn {
                padding: 15px 40px;
                font-size: 1.1em;
                border: none;
                border-radius: 50px;
                cursor: pointer;
                text-decoration: none;
                transition: all 0.3s;
                font-weight: bold;
            }
            .btn-admin {
                background: #667eea;
                color: white;
            }
            .btn-admin:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }
            .btn-client {
                background: #764ba2;
                color: white;
            }
            .btn-client:hover {
                background: #63408a;
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(118, 75, 162, 0.4);
            }
            .features {
                margin-top: 40px;
                text-align: left;
            }
            .feature {
                margin: 15px 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 10px;
            }
            .feature strong {
                color: #667eea;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 Federated Learning CKD System</h1>
            <p>Privacy-Enhanced Chronic Kidney Disease Prediction</p>
            
            <div class="buttons">
                <a href="/admin" class="btn btn-admin">👑 Admin Login</a>
                <a href="/client" class="btn btn-client">🏥 Client Login</a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <strong>✔ Privacy Preserved:</strong> No raw data sharing between hospitals
                </div>
                <div class="feature">
                    <strong>✔ Differential Privacy:</strong> Protected model weights with DP
                </div>
                <div class="feature">
                    <strong>✔ Federated Learning:</strong> Collaborative training without data centralization
                </div>
                <div class="feature">
                    <strong>✔ Secure Authentication:</strong> Dual password system for enhanced security
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """Admin login page"""
    admin_file = templates_path / "admin.html"
    if admin_file.exists():
        return FileResponse(str(admin_file))
    return HTMLResponse("<h1>Admin Dashboard</h1><p>Frontend under construction</p>")

@app.get("/client", response_class=HTMLResponse)
async def client_page():
    """Client login page"""
    client_file = templates_path / "client.html"
    if client_file.exists():
        return FileResponse(str(client_file))
    return HTMLResponse("<h1>Client Dashboard</h1><p>Frontend under construction</p>")

@app.get("/help", response_class=HTMLResponse)
async def help_page():
    """Help and user guide page"""
    help_file = templates_path / "help.html"
    if help_file.exists():
        return FileResponse(str(help_file))
    return HTMLResponse("<h1>Help & Guide</h1><p>User guide under construction</p>")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Federated Learning CKD System",
        "version": "1.0.0"
    }

@app.get("/api/info")
async def api_info():
    """API information"""
    return {
        "title": "Federated Learning CKD API",
        "version": "1.0.0",
        "description": "Privacy-Enhanced Federated Learning for Chronic Kidney Disease",
        "endpoints": {
            "admin": "/api/admin/*",
            "client": "/api/client/*"
        },
        "features": [
            "Dual authentication system",
            "Differential privacy protection",
            "Federated aggregation (FedAvg)",
            "Real-time training and prediction",
            "Email notifications",
            "Comprehensive audit logs"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

# Made with Bob
