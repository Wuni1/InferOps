"""
InferOps - Core Application State

This module manages the shared, in-memory state of the InferOps cluster.
It includes caches for node statuses, job information, and active alerts.

In a production, multi-instance deployment of the gateway, this in-memory storage
would be replaced by a distributed caching solution like Redis or an in-memory data grid
to ensure state consistency across all gateway instances.
"""

import threading
from typing import Dict, Any, List

# --- Node State Cache ---
# Caches the latest status received from each monitor agent.
# Key: node_id (int)
# Value: A dictionary containing the node's status, metrics, and online status.
NODE_STATUS_CACHE: Dict[int, Dict[str, Any]] = {
    # This will be populated at runtime based on the configuration.
}
# A lock to ensure thread-safe access to the NODE_STATUS_CACHE.
CACHE_LOCK = threading.Lock()


# --- CPU Info Cache ---
# Caches static CPU information to avoid sending it with every status update.
# Key: node_id (int)
# Value: CPU model string.
CPU_INFO_CACHE: Dict[int, str] = {}


# --- Dataset Processing Jobs ---
# Stores the state and results of ongoing and completed batch processing jobs.
# Key: job_id (str)
# Value: A dictionary containing job metadata, progress, and results.
DATASET_JOBS: Dict[str, Dict[str, Any]] = {}
# A lock for thread-safe operations on the DATASET_JOBS dictionary.
JOBS_LOCK = threading.Lock()


# --- Alerting System State ---
# A list that holds currently active alerts for the entire cluster.
ALERTS_LIST: List[Dict[str, Any]] = []
# A lock to protect concurrent access to the ALERTS_LIST.
ALERTS_LOCK = threading.Lock()

def initialize_state(nodes_config: List[Dict[str, Any]]):
    """
    Initializes the state caches based on the node configuration.
    This function is called once at application startup.
    """
    global NODE_STATUS_CACHE
    with CACHE_LOCK:
        for node in nodes_config:
            if node["id"] not in NODE_STATUS_CACHE:
                NODE_STATUS_CACHE[node["id"]] = {
                    "id": node["id"],
                    "name": node["name"],
                    "online": False,
                    "busy": False,
                    "metrics": None
                }
    print("✅ Core application state initialized.")

