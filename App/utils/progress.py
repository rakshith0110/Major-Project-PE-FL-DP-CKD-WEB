"""
Progress tracking utilities for long-running operations
"""
import asyncio
from typing import Dict, Optional
from datetime import datetime

class ProgressTracker:
    """Track progress of long-running operations"""
    
    def __init__(self):
        self._progress: Dict[str, Dict] = {}
    
    def start_operation(self, operation_id: str, description: str = ""):
        """Start tracking an operation"""
        self._progress[operation_id] = {
            "status": "running",
            "message": description or "Starting...",
            "percentage": 0,
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def update_progress(self, operation_id: str, message: str, percentage: int):
        """Update progress for an operation"""
        if operation_id in self._progress:
            self._progress[operation_id].update({
                "message": message,
                "percentage": min(100, max(0, percentage)),
                "updated_at": datetime.now().isoformat()
            })
    
    def complete_operation(self, operation_id: str, message: str = "Completed"):
        """Mark operation as complete"""
        if operation_id in self._progress:
            self._progress[operation_id].update({
                "status": "completed",
                "message": message,
                "percentage": 100,
                "updated_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            })
    
    def fail_operation(self, operation_id: str, error: str):
        """Mark operation as failed"""
        if operation_id in self._progress:
            self._progress[operation_id].update({
                "status": "failed",
                "message": f"Error: {error}",
                "updated_at": datetime.now().isoformat(),
                "failed_at": datetime.now().isoformat()
            })
    
    def get_progress(self, operation_id: str) -> Optional[Dict]:
        """Get progress for an operation"""
        return self._progress.get(operation_id)
    
    def cleanup_operation(self, operation_id: str):
        """Remove operation from tracking"""
        if operation_id in self._progress:
            del self._progress[operation_id]


# Global progress tracker instance
progress_tracker = ProgressTracker()

# Made with Bob