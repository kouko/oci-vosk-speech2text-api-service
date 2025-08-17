"""
API Key Authentication module
"""
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os

# Load API keys from environment or config
VALID_API_KEYS = set()
if os.getenv("API_KEY"):
    VALID_API_KEYS.add(os.getenv("API_KEY"))

# Also load from config file if exists
config_file = os.getenv("API_KEYS_FILE", "/app/config/api_keys.txt")
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        for line in f:
            key = line.strip()
            if key:
                VALID_API_KEYS.add(key)

security = HTTPBearer(auto_error=False)

def get_api_key_from_header(request: Request) -> Optional[str]:
    """
    Extract API key from various header formats
    """
    # Try x-api-key header first
    api_key = request.headers.get("x-api-key")
    if api_key:
        return api_key
    
    # Try Authorization header with Bearer token
    authorization = request.headers.get("authorization")
    if authorization:
        if authorization.startswith("Bearer "):
            return authorization[7:]  # Remove "Bearer " prefix
        elif authorization.startswith("bearer "):
            return authorization[7:]  # Remove "bearer " prefix
    
    return None

def verify_api_key(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    Verify API key from request headers
    """
    # Get API key from various sources
    api_key = None
    
    # First try x-api-key header
    api_key = get_api_key_from_header(request)
    
    # If not found, try HTTPBearer credentials
    if not api_key and credentials:
        api_key = credentials.credentials
    
    # Validate API key
    if not api_key:
        raise HTTPException(
            status_code=401, 
            detail="API key is required. Use 'x-api-key' header or 'Authorization: Bearer <key>'"
        )
    
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return api_key