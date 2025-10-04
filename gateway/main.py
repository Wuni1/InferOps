"""
InferOps - Main Application

This is the main entry point for the InferOps Gateway service.
It initializes the FastAPI application, includes all the API routers,
and starts the necessary background tasks for monitoring and alerting.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import asyncio

from gateway.config import settings
from gateway.core import state
from gateway.core.health import health_check_nodes_periodically
from gateway.services.alerting import alert_checker_periodically
from gateway.api.v1 import chat, status, dataset

# --- Application Initialization ---
def create_app() -> FastAPI:
    """Creates and configures the FastAPI application instance."""
    
    # Initialize the core application state from config
    state.initialize_state(settings.NODES)

    # Create FastAPI app
    app = FastAPI(
        title="InferOps Gateway",
        description="The central API gateway for the InferOps platform. It provides endpoints for chat completions, resource monitoring, and dataset processing.",
        version="1.0.0",
        openapi_tags=[
            {"name": "Chat", "description": "Endpoints for real-time LLM inference."},
            {"name": "Monitoring", "description": "Endpoints for monitoring cluster health and status."},
            {"name": "Dataset Processing", "description": "Endpoints for batch data processing."},
            {"name": "Admin", "description": "Administrative endpoints."},
        ]
    )

    # --- Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for simplicity
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- API Routers ---
    # Include all the version 1 API endpoints
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(status.router, prefix="/api/v1")
    app.include_router(dataset.router, prefix="/api/v1")

    # --- Static Files and Frontend ---
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    # Mount the static directory to serve frontend assets (js, css)
    app.mount("/static", StaticFiles(directory=frontend_dir, html=True), name="static_frontend")

    # Serve the main index.html for the root path
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def serve_frontend():
        """Serves the main single-page application (SPA) frontend."""
        index_path = frontend_dir / "index.html"
        if not index_path.exists():
            return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)
        return HTMLResponse(index_path.read_text())

    # --- Background Tasks ---
    @app.on_event("startup")
    async def startup_event():
        """
        On application startup, launch the background tasks for health checks and alerting.
        """
        print("🚀 InferOps Gateway starting up...")
        # Start the health check loop
        asyncio.create_task(health_check_nodes_periodically())
        # Start the alert checking loop
        asyncio.create_task(alert_checker_periodically())
        print("✅ Background services started.")

    return app

app = create_app()

# --- Main Execution ---
if __name__ == "__main__":
    # This block allows running the gateway directly for development
    uvicorn.run(
        "gateway.main:app",
        host=settings.GATEWAY_HOST,
        port=settings.GATEWAY_PORT,
        reload=True  # Enable auto-reload for easier development
    )
