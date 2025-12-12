#!/usr/bin/env python3
"""
Simple echo agent for testing Automagik Omni.
Echoes back every message it receives with channel information.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("echo-agent")

app = FastAPI(title="Echo Agent", version="1.0.0")

# Request/Response Models
class UserData(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[str] = None
    user_data: Optional[Dict[str, Any]] = None

class AgentRequest(BaseModel):
    user_id: str
    session_id: str
    session_name: str
    message: str
    message_type: str = "text"
    session_origin: str = "whatsapp"
    user: Optional[UserData] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    text: str

# Endpoints
@app.post("/api/agent/chat", response_model=AgentResponse)
async def chat(request: AgentRequest):
    """
    Echo endpoint that responds to messages.
    
    Receives a message and returns it echoed back with metadata about the request.
    """
    logger.info(f"Received request from user: {request.user_id}")
    logger.info(f"Message: {request.message}")
    logger.info(f"Session: {request.session_name}")
    logger.info(f"Origin: {request.session_origin}")
    
    # Log full request for debugging
    logger.debug(f"Full request: {json.dumps(request.model_dump(), indent=2, default=str)}")
    
    # Create echo response
    echo_text = f"[Echo from {request.session_origin}] {request.message}"
    
    logger.info(f"Responding with: {echo_text}")
    
    return AgentResponse(text=echo_text)

@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {"status": "healthy", "service": "echo-agent"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "echo-agent",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /api/agent/chat",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Echo Agent on 0.0.0.0:8886")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8886,
        reload=False,
        log_level="info"
    )
