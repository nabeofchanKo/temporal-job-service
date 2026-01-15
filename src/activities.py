import asyncio
from dataclasses import dataclass
from temporalio import activity

# Define the data structure for activity input
# Must match the structure sent from the workflow
@dataclass
class JobInput:
    numbers: list[int]
    fail_first_attempt: bool

@activity.defn
async def do_work_activity(data: JobInput) -> dict:
    """
    Performs the core business logic.
    Calculates the sum of a list of numbers.
    Simulates a transient failure if requested to demonstrate retry mechanisms.
    """
    
    # Get metadata about the current activity execution (e.g., attempt count)
    info = activity.info()
    attempt = info.attempt

    print(f"--- Activity execution: Attempt #{attempt} ---")

    # Fault Tolerance Test:
    # If the 'fail_first_attempt' flag is True, raise an exception on the first try.
    # This forces Temporal to trigger the RetryPolicy.
    if data.fail_first_attempt and attempt == 1:
        print("🚨 Simulating failure per requirement (Fault Tolerance Test)!")
        raise RuntimeError("Simulated Failure on 1st attempt!")

    # Simulate processing latency (e.g., external API call or heavy computation)
    await asyncio.sleep(2) 
    
    # Core Logic: Calculate sum of the numbers
    total_sum = sum(data.numbers)
    print(f"✅ Job SUCCESS! Sum is {total_sum}")
    
    # Return structured result
    return {
        "status": "COMPLETED",
        "result": total_sum,
        "attempts_taken": attempt
    }