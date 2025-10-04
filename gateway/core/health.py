"""
InferOps - Automated Failure Handling Module (Health Checks)

This module is a key part of the platform's resilience strategy. It continuously
monitors the health of all registered compute nodes to ensure high availability.
"""

import asyncio
import httpx
from gateway.config import settings
from gateway.core import state

# Create a reusable HTTP client for health checks
health_client = httpx.AsyncClient(timeout=settings.HEALTH_CHECK_INTERVAL - 1)

async def health_check_nodes_periodically():
    """
    A background task that runs periodically to check the health of all nodes.
    
    This function embodies the proactive monitoring aspect of the Failure Handling Module.
    It polls all registered servers for heartbeat signals. If a node is unresponsive
    or returns an error, it's marked as 'offline' and immediately removed from the
    scheduling pool, preventing tasks from being sent to a faulty node.
    """
    print("🩺 Health check service started.")
    while True:
        # Run checks for all nodes concurrently
        await asyncio.gather(*(fetch_single_node_status(node) for node in settings.NODES))
        # Wait for the next interval
        await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)

async def fetch_single_node_status(node_config: dict):
    """
    Asynchronously fetches the status of a single compute node.
    
    Args:
        node_config (dict): The configuration dictionary for the node to be checked.
    """
    node_id = node_config["id"]
    url = f"{node_config['monitor_base_url']}/status"
    
    try:
        response = await health_client.get(url)
        
        # If the node responds with a 200 OK status
        if response.status_code == 200:
            metrics = response.json()
            with state.CACHE_LOCK:
                # Update the cache with the latest metrics and mark the node as online
                state.NODE_STATUS_CACHE[node_id].update(online=True, metrics=metrics)
                # Cache the static CPU info if available
                if metrics.get("cpu_info"):
                    state.CPU_INFO_CACHE[node_id] = metrics.get("cpu_info")
        else:
            # If the node returns a non-200 status, it's considered offline
            with state.CACHE_LOCK:
                if state.NODE_STATUS_CACHE[node_id]["online"]:
                    print(f"⚠️ Node {node_id} is now offline. Status: {response.status_code}")
                state.NODE_STATUS_CACHE[node_id].update(online=False, metrics=None)
                
    except httpx.RequestError as e:
        # If there's a connection error (e.g., timeout, DNS failure), mark as offline
        with state.CACHE_LOCK:
            if state.NODE_STATUS_CACHE[node_id]["online"]:
                print(f"🚨 Node {node_id} connection failed: {e}. Marking as offline.")
            state.NODE_STATUS_CACHE[node_id].update(online=False, metrics=None)
