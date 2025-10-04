"""
InferOps - API Dependencies

This module can be used to define common dependencies for FastAPI endpoints,
such as authentication, database sessions, or rate limiting.
"""

from fastapi import Header, HTTPException

async def get_api_key(x_api_key: str = Header(None)):
    """
    A placeholder dependency to demonstrate API key authentication.
    In a real application, this would validate the key against a database.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header is missing.")
    if x_api_key != "fake-super-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API Key.")
    return x_api_key
