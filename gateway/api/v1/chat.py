"""
InferOps - API v1: Chat Completions

This router handles all real-time chat completion requests. It serves as the primary
entry point for user interaction with the LLMs on the compute nodes.
"""

import json
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from gateway.models.api_models import ChatRequest
from gateway.core.scheduler import get_best_node
from gateway.services.locking import lock_node, unlock_node
from gateway.config import settings

router = APIRouter()

# A dedicated, long-timeout client for streaming LLM responses
streaming_client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)

@router.post("/chat/completions", tags=["Chat"])
async def chat_proxy(request: ChatRequest):
    """
    This endpoint is the core of the real-time inference pipeline. It demonstrates:
    1.  **Task Scheduling**: Selects the best available node using the dynamic scheduler.
    2.  **Resource Locking**: Reserves the chosen node to prevent conflicts.
    3.  **Failure Handling (Re-routing)**: If the initial node choice fails, it attempts to find another.
    4.  **Streaming Response**: Streams the LLM's response back to the client token by token.
    """
    # --- 1. Task Scheduling ---
    # Attempt to find the best node, optionally filtering by the requested model.
    selected_node_config = await get_best_node(request.model)
    
    # --- 2. Resource Locking & Failure Handling (Re-routing) ---
    if not selected_node_config or not await lock_node(selected_node_config):
        # If no node is found or locking fails, try again without model preference.
        # This is a simple re-routing strategy.
        print("Initial node selection failed or could not be locked. Retrying without model preference...")
        selected_node_config = await get_best_node()
        if not selected_node_config or not await lock_node(selected_node_config):
            raise HTTPException(status_code=503, detail="All suitable nodes are busy or unavailable.")

    async def stream_generator():
        """
        A generator function that streams the response from the backend LLM.
        It includes crucial logic for failure handling and ensuring the node is unlocked.
        """
        unlocked = False
        try:
            # --- Custom Event: Inform client which node was chosen ---
            node_name = selected_node_config["name"]
            event_data = json.dumps({"node_name": node_name})
            yield f"event: node_assigned\ndata: {event_data}\n\n"

            # --- 3. Stream the request to the selected node ---
            async with streaming_client.stream(
                "POST",
                selected_node_config["llm_url"],
                json=request.dict(exclude={"model"}), # Exclude model as it's for our scheduler
                timeout=settings.REQUEST_TIMEOUT
            ) as response:
                # Raise an exception for non-200 responses to trigger failure handling
                response.raise_for_status()

                # Stream the response chunk by chunk
                async for chunk in response.aiter_bytes():
                    yield chunk
                    # A simple way to detect the end of a stream from Ollama
                    if b'"done":true' in chunk and not unlocked:
                        await unlock_node(selected_node_config)
                        unlocked = True
        
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # --- 4. Failure Handling (During Stream) ---
            # This block catches connection errors or non-200 responses.
            print(f"🚨 Stream failed from node {selected_node_config['id']}: {e}. Task reassignment would be triggered here.")
            # In a real system, the gateway would capture the conversation history 
            # and resubmit the task to a different node. Here, we just inform the client.
            error_message = json.dumps({"error": "The compute node failed during the request."})
            yield f"data: {error_message}\n\n"
        
        finally:
            # --- Final Unlock ---
            # This 'finally' block is a critical part of the failure handling module.
            # It ensures that the node is ALWAYS unlocked, even if the client disconnects
            # or an unexpected error occurs.
            if not unlocked:
                print(f"Force-unlocking node {selected_node_config['id']} due to stream interruption or error.")
                await unlock_node(selected_node_config)

    return StreamingResponse(stream_generator(), media_type="text/event-stream")
