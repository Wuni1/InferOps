"""
InferOps - Centralized Configuration

This file centralizes all the configuration settings for the InferOps Gateway.
By using a dedicated configuration file, we can easily manage different environments
(e.g., development, staging, production) and avoid hardcoding values directly in the code.
"""
from decouple import config

class Settings:
    """
    Main configuration class for the InferOps Gateway.
    It reads environment variables but provides sensible defaults.
    """
    # --- Application Settings ---
    GATEWAY_HOST: str = config("GATEWAY_HOST", default="0.0.0.0")
    GATEWAY_PORT: int = config("GATEWAY_PORT", default=8000, cast=int)
    
    # --- Monitoring and Health Checks ---
    HEALTH_CHECK_INTERVAL: int = config("HEALTH_CHECK_INTERVAL", default=5, cast=int) # seconds
    REQUEST_TIMEOUT: int = config("REQUEST_TIMEOUT", default=120, cast=int) # seconds

    # --- Node Configuration ---
    # In a real-world scenario, this would be loaded from a dynamic configuration source
    # like a database, a YAML file, or a service discovery mechanism (e.g., Consul).
    NODES: list = [
        {
            "id": 1, 
            "name": "节点 1 (RTX 4090)",
            "monitor_base_url": "http://100.76.208.127:8001",
            "llm_url": "http://100.76.208.127:11434/api/chat", # Ollama endpoint
            "static_weight": 10.0,  # Represents static performance factors like TFLOPS.
        },
        {
            "id": 2, 
            "name": "节点 2 (RTX 3080)",
            "monitor_base_url": "http://100.118.49.57:8001",
            "llm_url": "http://100.118.49.57:11434/api/chat", # Ollama endpoint
            "static_weight": 7.5,
        },
        {
            "id": 3, 
            "name": "节点 3 (GTX 1080Ti)",
            "monitor_base_url": "http://100.99.253.87:8001",
            "llm_url": "http://100.99.253.87:11434/api/chat", # Ollama endpoint
            "static_weight": 5.0,
        },
    ]

    # --- Batch Processing & Aggregation ---
    # Threshold for the incremental merging strategy in the Result Aggregation Module.
    # The aggregation process begins once this percentage of results is available.
    INCREMENTAL_MERGE_THRESHOLD: float = config("INCREMENTAL_MERGE_THRESHOLD", default=0.5, cast=float)

    # --- External Services ---
    PROMETHEUS_URL: str = config("PROMETHEUS_URL", default="http://localhost:9090")


# Instantiate the settings object to be imported by other modules
settings = Settings()
