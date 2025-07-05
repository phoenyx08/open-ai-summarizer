#!/usr/bin/env python3
"""
Mock external API server for testing the PDF summarization service
"""

import json
import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Mock External API",
    description="Mock API for testing PDF summarization service",
    version="1.0.0"
)

# Authentication
security = HTTPBearer()

# Expected token for testing
TEST_TOKEN = "test_external_token"

# Store received summaries for verification
received_summaries = []

class SummaryRequest(BaseModel):
    filename: str
    summary: str

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Bearer token authentication"""
    if credentials.credentials != TEST_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication token"
        )
    return credentials.credentials

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Mock External API is running"}

@app.post("/mock-api")
async def receive_summary(
    request: SummaryRequest,
    token: str = Depends(verify_token)
):
    """
    Mock endpoint to receive summaries from the PDF summarization service
    """
    logger.info(f"Received summary for file: {request.filename}")
    logger.info(f"Summary: {request.summary[:100]}...")
    
    # Store the summary for verification
    summary_data = {
        "filename": request.filename,
        "summary": request.summary,
        "timestamp": "2024-01-01T00:00:00Z"  # Mock timestamp
    }
    received_summaries.append(summary_data)
    
    return {
        "message": "Summary received successfully",
        "filename": request.filename,
        "status": "accepted"
    }

@app.get("/mock-api/summaries")
async def get_summaries():
    """
    Get all received summaries (for testing verification)
    """
    return {
        "summaries": received_summaries,
        "count": len(received_summaries)
    }

@app.delete("/mock-api/summaries")
async def clear_summaries():
    """
    Clear all received summaries (for test cleanup)
    """
    global received_summaries
    count = len(received_summaries)
    received_summaries.clear()
    return {
        "message": f"Cleared {count} summaries",
        "count": 0
    }

@app.post("/mock-api/error")
async def simulate_error():
    """
    Endpoint to simulate API errors for testing error handling
    """
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Simulated external API error"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")