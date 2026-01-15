import asyncio
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from temporalio.client import Client

# Import workflow and data definitions
from src.workflows import MyJobWorkflow
from src.activities import JobInput

app = FastAPI()
temporal_client = None

# --- Pydantic Models for Request Validation ---
# These models ensure the API accepts the exact JSON structure 
# defined in the "Start a Job" requirement.

class JobInputData(BaseModel):
    # Default values provided for convenience in Swagger UI
    numbers: list[int] = [1, 2, 3, 4]

class JobOptions(BaseModel):
    fail_first_attempt: bool = True

class JobRequest(BaseModel):
    input: JobInputData
    options: JobOptions

# --------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """
    Initialize the Temporal Client when the FastAPI application starts.
    This establishes the connection to the Temporal server running in Docker.
    """
    global temporal_client
    # Connect to the local Temporal server
    temporal_client = await Client.connect("localhost:7233")

@app.post("/jobs")
async def start_job(request: JobRequest):
    """
    Endpoint to start a new background job.
    Maps the incoming JSON request to the Activity input format.
    """
    # Generate a unique ID for the workflow execution (using timestamp)
    job_id = f"job-{int(time.time())}"

    # Prepare input arguments for the Activity
    # Extracting data from the nested 'input' and 'options' fields
    input_args = JobInput(
        numbers=request.input.numbers,
        fail_first_attempt=request.options.fail_first_attempt
    )

    # Start the Temporal Workflow asynchronously
    handle = await temporal_client.start_workflow(
        MyJobWorkflow.run,
        input_args,
        id=job_id,
        task_queue="my-task-queue",
    )

    # Return the job ID and status immediately
    return {
        "job_id": handle.id, 
        "status": "STARTED",
        "message": "Workflow submitted successfully."
    }

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Query the status of a specific workflow.
    Returns a JSON response strictly matching the "Query Job Status" requirement.
    """
    try:
        # Get the handle for the workflow
        handle = temporal_client.get_workflow_handle(job_id)
        
        # Fetch current workflow description (status, history, etc.)
        desc = await handle.describe()
        
        # Map Temporal's internal integer status to a readable string
        status_map = {
            1: "RUNNING",
            2: "COMPLETED",
            3: "FAILED",
            4: "CANCELED",
            5: "TERMINATED",
            6: "CONTINUED_AS_NEW",
            7: "TIMED_OUT",
        }
        status_str = status_map.get(desc.status, "UNKNOWN")
        
        result_val = None
        error_val = None
        
        # If the workflow is completed, retrieve the final result
        if status_str == "COMPLETED":
            try:
                result_val = await handle.result()
            except Exception:
                result_val = "Could not fetch result"
        
        # If the workflow failed, indicate the error state
        if status_str == "FAILED":
            error_val = "Workflow execution failed (Check Worker logs for details)"

        # Construct the response object to match the required spec:
        # { job_id, status, progress, result, error }
        return {
            "job_id": job_id,
            "status": status_str,
            "progress": {
                "stage": "processing" if status_str == "RUNNING" else "finished",
                "info": "See Temporal UI for detailed attempt history"
            },
            "result": result_val,
            "error": error_val
        }

    except Exception as e:
        # Return 404 if job ID is invalid or server is unreachable
        raise HTTPException(status_code=404, detail=f"Job not found or error: {str(e)}")