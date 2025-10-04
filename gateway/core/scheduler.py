"""
InferOps - Task Scheduling Module

This module implements the core logic for the dynamic task scheduling algorithm,
as described in the InferOps research paper. Its primary responsibility is to select
the most suitable compute node for a given task based on a combination of static
performance metrics and real-time dynamic load data.
"""

from typing import Optional, Dict, Any
from gateway.core import state
from gateway.config import settings

async def get_best_node(requested_model: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Implements the dynamic weighted scheduling algorithm of the Task Scheduling Module.
    
    This algorithm calculates a real-time composite score for each available (online and not locked)
    compute node. The score is a function of the node's static performance weight and its current
    dynamic load, including GPU utilization, memory usage, and temperature.

    The formula (simplified for this implementation) is:
        Score = StaticWeight / (DynamicLoadFactor + Epsilon)
    
    Where:
    - StaticWeight: A pre-assigned value representing the node's raw power (e.g., TFLOPS).
    - DynamicLoadFactor: A weighted average of current GPU load, memory load, and GPU temperature.
    - Epsilon: A small constant to prevent division by zero.

    The node with the highest score is selected as the "best" node for the incoming task.
    
    Args:
        requested_model (Optional[str]): If specified, the scheduler will only consider nodes
                                         that are currently running this specific model.

    Returns:
        Optional[Dict[str, Any]]: The configuration dictionary of the selected best node,
                                  or None if no suitable node is found.
    """
    best_node = None
    highest_score = -1

    with state.CACHE_LOCK:
        # Iterate through all configured nodes
        for node_config in settings.NODES:
            node_id = node_config["id"]
            status = state.NODE_STATUS_CACHE.get(node_id)

            # --- Filtering Conditions ---
            # 1. Node must be online.
            # 2. Node must have metrics available.
            # 3. Node must not be locked by another task.
            if not status or not status.get("online") or not status.get("metrics") or status["metrics"].get("locked"):
                continue

            # 4. If a specific model is requested, filter by model ID.
            if requested_model and status["metrics"].get("model_id") != requested_model:
                continue
            
            # --- Dynamic Composite Score Calculation ---
            metrics = status.get("metrics", {})
            
            # Extract dynamic metrics, with sane defaults for stability
            gpu_load = metrics.get("gpu", {}).get("utilization_percent", 100)
            mem_load = metrics.get("memory", {}).get("percent", 100)
            gpu_temp = metrics.get("gpu", {}).get("temperature_celsius", 80)

            # Calculate the dynamic load factor. The weights (0.6, 0.3, 0.1) can be tuned.
            # GPU utilization is the most heavily weighted factor.
            dynamic_load_factor = (gpu_load * 0.6) + (mem_load * 0.3) + (gpu_temp * 0.1)
            
            # Calculate the final score
            score = node_config.get("static_weight", 1.0) / (dynamic_load_factor + 1e-6)

            # --- Selection ---
            # If the current node's score is the highest so far, it becomes the new candidate.
            if score > highest_score:
                highest_score = score
                best_node = node_config
    
    return best_node
