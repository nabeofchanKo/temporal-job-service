import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

# Import our workflow and activity
from src.activities import do_work_activity
from src.workflows import MyJobWorkflow

async def main():
    print("⏳ Connecting to Temporal Server...")
    
    # Connect to the server
    client = await Client.connect("localhost:7233")
    print("✅ Connected to Server! (UI doesn't matter now)")

    # Run the worker
    worker = Worker(
        client,
        task_queue="my-task-queue",  # Queue name
        workflows=[MyJobWorkflow],
        activities=[do_work_activity]
    )

    print("👷 Worker started. Ready to accept jobs.")
    
    # Keep running until interrupted
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())