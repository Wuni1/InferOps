"""
InferOps - Alerting Service

This service implements the logic for the proactive alerting mechanism, a component
of the Automated Failure Handling Module. It periodically checks node metrics against
predefined rules and generates alerts if thresholds are breached.
"""

import asyncio
from gateway.core import state
from gateway.config import settings

# --- Alerting Rules ---
# In a production system, these rules would be configurable and more complex,
# potentially allowing for dynamic rule creation and management via an API.
ALERT_RULES = {
    "gpu_temp_severe": {
        "threshold": 85,
        "level": "严重",
        "message": "GPU 温度过高",
        "cooldown": 300 # Cooldown in seconds to prevent alert spam
    },
    "mem_usage_severe": {
        "threshold": 95,
        "level": "严重",
        "message": "内存使用率极高",
        "cooldown": 300
    },
}

# Stores the last time an alert was fired for a specific rule on a specific node
# to implement the cooldown mechanism.
_alert_timestamps = {}

def check_for_alerts():
    """
    Checks all node statuses and generates or clears alerts based on predefined rules.
    This function is the core of the alerting logic.
    """
    with state.CACHE_LOCK, state.ALERTS_LOCK:
        active_alerts = []
        current_time = asyncio.get_event_loop().time()

        for node_id, status in state.NODE_STATUS_CACHE.items():
            if not status.get("online") or not status.get("metrics"):
                continue
            
            node_name = status.get("name", f"Node-{node_id}")
            metrics = status["metrics"]

            # Check GPU Temperature Alert
            gpu_temp = metrics.get("gpu", {}).get("temperature_celsius")
            rule = ALERT_RULES["gpu_temp_severe"]
            alert_key = f"gpu_temp_{node_id}"
            
            if gpu_temp and gpu_temp >= rule["threshold"]:
                last_fired = _alert_timestamps.get(alert_key, 0)
                if current_time - last_fired > rule["cooldown"]:
                    active_alerts.append({
                        "id": alert_key,
                        "level": rule["level"],
                        "message": f"{node_name} GPU温度达到 {gpu_temp}°C",
                        "timestamp": current_time
                    })
                    _alert_timestamps[alert_key] = current_time

            # Check Memory Usage Alert (can add more rules here)
            # ...

        # Update the global alerts list
        state.ALERTS_LIST = active_alerts

async def alert_checker_periodically():
    """
    A background task that periodically triggers the alert checking logic.
    """
    print("🚨 Alerting service started.")
    while True:
        # Wait for a slightly longer interval than health checks to ensure fresh data
        await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL * 2)
        try:
            check_for_alerts()
        except Exception as e:
            print(f"Error during alert check: {e}")
