"""
InferOps - API v1: System Status & Monitoring

This router provides endpoints for monitoring the overall health and status
of the InferOps cluster. It exposes cached data collected by the background
health and monitoring services.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Set

from gateway.core import state
from gateway.models.api_models import NodeStatus, Alert
from gateway.services.locking import unlock_node
from gateway.config import settings

router = APIRouter()

@router.get("/status/all", response_model=List[NodeStatus], tags=["Monitoring"])
async def get_all_statuses():
    """
    Retrieves the latest cached status for all configured nodes.
    This endpoint is the primary data source for the frontend dashboard.
    """
    with state.CACHE_LOCK:
        # Create a deep copy to avoid race conditions while iterating
        statuses = [status.copy() for status in state.NODE_STATUS_CACHE.values()]
        
        # Enrich the status with the cached CPU model information
        for status in statuses:
            if status["online"] and status["metrics"]:
                status["cpu_model"] = state.CPU_INFO_CACHE.get(status["id"], "Unknown Processor")
    return statuses

@router.get("/alerts", response_model=List[Alert], tags=["Monitoring"])
async def get_alerts():
    """
    Retrieves the current list of active system alerts.
    """
    with state.ALERTS_LOCK:
        return state.ALERTS_LIST.copy()

@router.get("/models", response_model=List[str], tags=["Monitoring"])
async def get_available_models() -> List[str]:
    """
    Aggregates the list of unique LLM models currently running across all online nodes.
    This allows the frontend to offer a dynamic model selection menu.
    """
    models: Set[str] = set()
    with state.CACHE_LOCK:
        for status in state.NODE_STATUS_CACHE.values():
            if status.get("online") and status.get("metrics") and status["metrics"].get("model_id"):
                models.add(status["metrics"]["model_id"])
    return sorted(list(models))

@router.post("/unlock/all", tags=["Admin"])
async def unlock_all_nodes():
    """
    An administrative endpoint to force-unlock all configured nodes.
    This is a safety measure to recover nodes that might get stuck in a 'locked'
    state due to an unexpected error or client disconnection.
    """
    unlocked_nodes = []
    failed_nodes = []
    for node_config in settings.NODES:
        success = await unlock_node(node_config)
        if success:
            unlocked_nodes.append(node_config["id"])
        else:
            failed_nodes.append(node_config["id"])
            
    if not failed_nodes:
        return {"message": "All nodes have been sent an unlock command.", "unlocked": unlocked_nodes}
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to unlock some nodes.",
                "unlocked": unlocked_nodes,
                "failed": failed_nodes
            }
        )
