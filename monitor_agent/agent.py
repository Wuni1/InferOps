# InferOps - Monitor Agent
# This lightweight agent is deployed on each compute node in the InferOps cluster.
# It is a core part of the Resource Monitoring Module.
#
# Responsibilities:
# 1. Collects real-time hardware status using psutil (for CPU/memory) and pynvml (for NVIDIA GPU),
#    acting as a lightweight node exporter as described in the paper.
# 2. Provides a standard API endpoint (/status) for the central Gateway to query these metrics.
# 3. Implements lock/unlock mechanisms, allowing the Task Scheduling and Failure Handling modules
#    to control the node's availability in the cluster.

import psutil
import uvicorn
import threading
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pynvml import *
from decouple import config
import platform

app = FastAPI(
    title="InferOps Monitor Agent",
    description="Collects and exposes hardware metrics for a single compute node.",
    version="1.0.0"
)

# --- State Management ---
# Using a thread-safe lock for state changes, particularly for the 'locked' status.
# This ensures that the node's availability is handled atomically.
NODE_LOCKED = False
lock = threading.Lock()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Core Metric Collection Logic ---

# Check for NVIDIA GPU availability on startup.
# This mimics the functionality of DCGM mentioned in the paper for GPU telemetry.
GPU_AVAILABLE = False
try:
    nvmlInit()
    GPU_AVAILABLE = True
except NVMLError as e:
    print(f"Warning: NVIDIA GPU not found or driver error: {e}. GPU metrics will be unavailable.")

def get_current_model_id():
    """
    Placeholder function to get the ID of the model currently loaded by the LLM service (e.g., Ollama).
    In a real implementation, this would query the LLM service endpoint.
    """
    try:
        # This is a fake query to simulate fetching the model from Ollama.
        # response = httpx.get("http://localhost:11434/api/tags")
        # models = response.json()
        # return models['models'][0]['name'] if models['models'] else "ollama/llama3"
        return "ollama/llama3-8b-instruct:latest" # Returning a static fake value
    except Exception:
        return "unknown"

def get_cpu_info():
    """
    Collects detailed CPU information.
    This is part of the metrics collection layer of the Resource Monitoring Module.
    """
    return platform.processor()

@app.get("/status")
def get_system_status():
    """
    The primary endpoint for the Gateway's Resource Monitoring Module to poll.
    Returns a comprehensive snapshot of the node's current hardware status.
    """
    # CPU metrics
    cpu_usage = psutil.cpu_percent(interval=1)

    # Memory metrics
    memory = psutil.virtual_memory()

    status = {
        "locked": NODE_LOCKED,
        "model_id": get_current_model_id(),
        "cpu_usage_percent": cpu_usage,
        "cpu_model": get_cpu_info(),
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2)
        },
        "gpu": None,
    }

    if GPU_AVAILABLE:
        try:
            # Assumes a single GPU (index 0) for simplicity.
            handle = nvmlDeviceGetHandleByIndex(0)
            
            utilization = nvmlDeviceGetUtilizationRates(handle)
            mem_info = nvmlDeviceGetMemoryInfo(handle)
            temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            power_watts = nvmlDeviceGetPowerUsage(handle) / 1000.0

            status["gpu"] = {
                "available": True,
                "utilization_percent": utilization.gpu,
                "memory_utilization_percent": utilization.memory,
                "memory_total_gb": round(mem_info.total / (1024**3), 2),
                "memory_used_gb": round(mem_info.used / (1024**3), 2),
                "memory_free_gb": round(mem_info.free / (1024**3), 2),
                "memory_usage_percent": round((mem_info.used / mem_info.total) * 100, 2),
                "temperature_celsius": temperature,
                "power_watts": round(power_watts, 2),
            }
        except NVMLError as e:
             status["gpu"] = {"available": False, "error": str(e)}
    else:
        status["gpu"] = {"available": False, "error": "NVIDIA driver not initialized or GPU not found."}
        
    return status

# --- Lock Control API for Task Scheduler ---
@app.post("/lock")
def lock_node():
    """
    Locks the node, making it unavailable for new task assignments.
    This is called by the Gateway's Task Scheduler immediately before assigning a task.
    """
    global NODE_LOCKED
    with lock:
        if NODE_LOCKED:
            # If already locked, return a conflict error. This helps the scheduler handle race conditions.
            raise HTTPException(status_code=409, detail="Node is already locked.")
        NODE_LOCKED = True
    return {"status": "success", "message": "Node locked for InferOps task."}

@app.post("/unlock")
def unlock_node():
    """
    Unlocks the node, returning it to the pool of available resources.
    This is called by the Gateway after a task is completed or has failed.
    """
    global NODE_LOCKED
    with lock:
        NODE_LOCKED = False
    return {"status": "success", "message": "Node unlocked."}

# --- Main Execution ---
if __name__ == "__main__":
    # Runs the agent service. In a production environment, this would be managed by a process manager like systemd.
    port = config('PORT', default=8001, cast=int)
    uvicorn.run(app, host="0.0.0.0", port=port) 