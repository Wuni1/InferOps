"""
InferOps - Pydantic Data Models

This file defines the Pydantic models used for API request and response validation.
These models ensure that data flowing into and out of the API is well-structured
and adheres to the expected types, which is crucial for robustness and clarity.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# --- Chat Completion Models ---

class ChatMessage(BaseModel):
    """Represents a single message in a chat conversation."""
    role: str
    content: str

class ChatRequest(BaseModel):
    """Defines the structure for a chat completion request."""
    messages: List[ChatMessage]
    model: Optional[str] = None
    stream: bool = True

class NodeAssignedEvent(BaseModel):
    """A special event sent to the client to indicate which node is handling the request."""
    node_name: str


# --- Dataset Processing Models ---

class JobStatus(BaseModel):
    """Represents the detailed status of a batch processing job."""
    job_id: str
    status: str
    total_items: int
    processed_items: int
    start_time: float
    end_time: Optional[float] = None
    results: List[Dict[str, Any]]


# --- Node and System Status Models ---

class GPUInfo(BaseModel):
    """Detailed information about a single GPU."""
    available: bool
    name: Optional[str] = None
    utilization_percent: Optional[float] = None
    memory_total_mb: Optional[float] = None
    memory_used_mb: Optional[float] = None
    memory_usage_percent: Optional[float] = None
    temperature_celsius: Optional[float] = None

class MemoryInfo(BaseModel):
    """Information about system memory (RAM)."""
    total: int
    available: int
    percent: float
    used: int
    free: int

class NodeMetrics(BaseModel):
    """Comprehensive metrics for a single compute node."""
    locked: bool
    model_id: Optional[str] = None
    cpu_usage_percent: float
    memory: MemoryInfo
    gpu: GPUInfo
    cpu_info: Optional[str] = None

class NodeStatus(BaseModel):
    """The overall status of a node, including its metrics."""
    id: int
    name: str
    online: bool
    busy: bool
    metrics: Optional[NodeMetrics] = None
    cpu_model: Optional[str] = None

class Alert(BaseModel):
    """Represents a system alert."""
    id: str
    level: str # e.g., '严重', '警告'
    message: str
    timestamp: float
