import asyncio
import logging
from agent.executor import agent_app
from agent.memory import AgentMemory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyShadcn")

async def main():
    # Define Target Task State for React Hook Form on Shadcn Document URL
    initial_state = {
        "objective": (
            "Navigate to: https://ui.shadcn.com/docs/forms/react-hook-form. "
            "Locate the input field labeled 'Username' or matching the form controls, "
            "and fill it with the value 'Antigravity Agent'. "
            "Then, locate the Submit button and click it to submit."
        ),
        "history": [],
        "current_url": None,
        "screenshot_path": None,
        "attempts": 0,
        "status": "running",
        "next_tool": None,
        "next_tool_args": None
    }

    logger.info("Starting Shadcn react-hook-form verification run...")
    memory = AgentMemory()
    try:
        # Run autonomous LangGraph agent loop
        final_state = await agent_app.ainvoke(initial_state)
        
        logger.info(f"Execution finished with status: {final_state['status']}")
        logger.info(f"Total steps taken: {final_state['attempts']}")
        
        # Save run log via Memory Manager
        log_file = memory.save_run_log(
            objective=final_state["objective"], 
            history=final_state["history"], 
            filename="shadcn_memory.json"
        )
        logger.info(f"Saved run logs to: {log_file}")
        
        # Print summary output
        summary = memory.get_run_summary(final_state["history"])
        logger.info(f"Execution Summary: {summary}")
        
    except Exception as e:
        logger.error(f"Shadcn validation run failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
