#!/usr/bin/env python3
"""
Startup script for FastAPI backend
"""
import sys
import os

# Add the parent directory to Python path so we can import modules properly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Now we can import and run main
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    # Use environment PORT if provided (useful for deployment), default to 8080
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )