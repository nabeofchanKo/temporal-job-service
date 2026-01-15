from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activity definition and input type for type hinting
from src.activities import do_work_activity, JobInput

@workflow.defn
class MyJobWorkflow:
    @workflow.run
    async def run(self, input_data: JobInput) -> dict:
        """
        Orchestrates the job execution.
        Defines the RetryPolicy to handle transient failures automatically.
        Deterministic logic ensures the workflow can be replayed safely.
        """
        
        # Execute the activity with a defined RetryPolicy
        return await workflow.execute_activity(
            do_work_activity,
            input_data,
            start_to_close_timeout=timedelta(seconds=10), # Timeout for single attempt
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),    # Wait 1s before retry
                maximum_attempts=3,                       # Retry up to 3 times
                backoff_coefficient=2.0,                  # Exponential backoff
            ),
        )