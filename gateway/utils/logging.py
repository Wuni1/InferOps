"""
InferOps - Logging Configuration

This module sets up structured logging for the gateway application.
Using structured logs (e.g., in JSON format) makes it much easier to
parse, search, and analyze logs in a production environment with tools
like the ELK stack (Elasticsearch, Logstash, Kibana) or Splunk.
"""

import logging
import sys

def setup_logging():
    """
    Configures the root logger for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
    
    # You could add a JSON formatter here for production logging
    # from pythonjsonlogger import jsonlogger
    # formatter = jsonlogger.JsonFormatter()
    # logHandler.setFormatter(formatter)

    print("📝 Logging configured.")

# In a real app, you would call setup_logging() in main.py
# For this pseudo-implementation, the existence of the file is sufficient.
