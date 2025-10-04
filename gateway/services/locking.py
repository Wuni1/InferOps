"""
InferOps - Node Locking Service

This service provides a simple mechanism for reserving a compute node for a specific task.
Locking a node prevents the scheduler from assigning new tasks to it while it is busy
processing a request. This is a fundamental part of resource management in the cluster.
"""

import httpx
from typing import Dict, Any

# Use a dedicated client for locking operations
lock_client = httpx.AsyncClient(timeout=5.0)

async def lock_node(node_config: Dict[str, Any]) -> bool:
    """
    Sends a lock request to the specified node's monitor agent.

    Args:
        node_config (Dict[str, Any]): The configuration of the node to lock.

    Returns:
        bool: True if the node was successfully locked, False otherwise.
    """
    try:
        response = await lock_client.post(f"{node_config['monitor_base_url']}/lock")
        return response.status_code == 200
    except httpx.RequestError as e:
        print(f"Error locking node {node_config['id']}: {e}")
        return False

async def unlock_node(node_config: Dict[str, Any]) -> bool:
    """
    Sends an unlock request to the specified node's monitor agent.

    Args:
        node_config (Dict[str, Any]): The configuration of the node to unlock.

    Returns:
        bool: True if the node was successfully unlocked, False otherwise.
    """
    try:
        response = await lock_client.post(f"{node_config['monitor_base_url']}/unlock")
        if response.status_code == 200:
            return True
        print(f"Failed to unlock node {node_config['id']}: Status {response.status_code}")
        return False
    except httpx.RequestError as e:
        print(f"Error unlocking node {node_config['id']}: {e}")
        return False
