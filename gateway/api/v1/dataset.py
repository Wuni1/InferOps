"""
InferOps - API v1: Dataset Processing

This router manages the batch processing of datasets. It showcases data parallelism
and the principles of the "Incremental Result Aggregation Module".
"""

import asyncio
import json
import time
import uuid
import random
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks

from gateway.core import state
from gateway.core.scheduler import get_best_node
from gateway.models.api_models import JobStatus
from gateway.config import settings

router = APIRouter()

async def run_dataset_processing_job(job_id: str, dataset: list):
    """
    A background task that manages the batch processing of a dataset.

    This function simulates:
    1.  **Data Parallelism**: Distributing individual data items to available nodes.
    2.  **Dynamic Scheduling**: Using `get_best_node` for each item to spread the load.
    3.  **Incremental Aggregation**: The results are collected as they are completed.
        A real implementation of the "Aggregator Hub" would start merging/post-processing
        results as soon as a certain threshold is met.
    """
    print(f"🚀 Starting dataset processing job {job_id} with {len(dataset)} items.")
    with state.JOBS_LOCK:
        job_info = state.DATASET_JOBS[job_id]
        job_info["status"] = "processing"

    # This loop simulates distributing data items and processing them.
    for i, item in enumerate(dataset):
        # For each item, find the best available node
        node = await get_best_node()
        if not node:
            print(f"⚠️ No available nodes for job {job_id}. Stopping processing.")
            break
        
        # Simulate the processing time on the node
        await asyncio.sleep(random.uniform(0.5, 2.0)) # Fake processing time
        
        with state.JOBS_LOCK:
            job_info["processed_items"] = i + 1
            # Store a fake result
            job_info["results"].append({"original": item, "output": f"Fake result for item {i+1}"})

            # --- Incremental Merging Simulation ---
            # This check simulates the trigger for the Aggregator Hub.
            # In a real system, this could publish an event or call another service
            # to begin post-processing the partially completed results.
            if job_info["processed_items"] >= job_info["total_items"] * settings.INCREMENTAL_MERGE_THRESHOLD:
                if not job_info.get("merge_triggered"):
                    print(f"✨ Job {job_id}: Incremental merge threshold reached. Aggregation can begin.")
                    job_info["merge_triggered"] = True

    with state.JOBS_LOCK:
        job_info["status"] = "completed"
        job_info["end_time"] = time.time()
    print(f"✅ Job {job_id} completed.")


@router.post("/dataset/upload", tags=["Dataset Processing"])
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    data_count: str = Form(None)
):
    """
    Receives a dataset file, creates a background processing job, and returns a job ID.
    """
    job_id = str(uuid.uuid4())
    content = await file.read()
    try:
        dataset = json.loads(content)
        if not isinstance(dataset, list):
            raise ValueError("JSON content must be an array of items.")
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {e}")

    # Allow user to select a subset of the data for processing
    if data_count and str(data_count).strip().isdigit():
        count = int(str(data_count).strip())
        if 0 < count <= len(dataset):
            dataset = dataset[:count]

    with state.JOBS_LOCK:
        state.DATASET_JOBS[job_id] = {
            "status": "queued",
            "total_items": len(dataset),
            "processed_items": 0,
            "start_time": time.time(),
            "end_time": None,
            "results": [],
        }

    # Add the processing task to run in the background
    background_tasks.add_task(run_dataset_processing_job, job_id, dataset)
    
    return {"job_id": job_id, "message": f"Job created with {len(dataset)} items."}

@router.get("/dataset/status/{job_id}", response_model=JobStatus, tags=["Dataset Processing"])
async def get_dataset_status(job_id: str):
    """
    Retrieves the current status and progress of a dataset processing job.
    """
    with state.JOBS_LOCK:
        job = state.DATASET_JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")
        # Return a copy to avoid modification outside the lock
        return job.copy()
