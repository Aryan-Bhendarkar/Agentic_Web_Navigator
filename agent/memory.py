import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from agent.state import ToolExecution
from config.settings import settings

logger = logging.getLogger(__name__)

#  Manages persistence of tool execution histories and generates summarized overviews of past steps.
class AgentMemory:

    def __init__(self) -> None:
        self.logs_dir = settings.get_absolute_logs_dir()

    # Serializes the complete list of executed actions, observations, and overall objective into a JSON log file.
    def save_run_log(self, objective: str, history: List[ToolExecution], filename: str = "run_memory.json") -> Path:
        filepath = self.logs_dir / filename
        logger.info(f"Saving agent run log to {filepath}...")

        data = {
            "objective": objective,
            "total_steps": len(history),
            "steps": [step.model_dump() for step in history]
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
           
            logger.info("Agent run log saved successfully.")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save agent run log to {filepath}: {e}", exc_info=True)
            raise

    # procedurally distills the list of past actions and their outcomes into a concise summary paragraph. Handy for LLM prompt context compaction.
    def get_run_summary(self, history: List[ToolExecution]) -> str:
        
        if not history:
            return "The agent has not executed any steps yet."

        completed_tools = []
        failed_tools = []

        for step in history:
            if "error" in step.observation.lower() or "failed" in step.observation.lower():
                failed_tools.append(f"{step.tool} ({list(step.args.keys())})")
            
            else:
                completed_tools.append(step.tool)

        summary_parts = []

        if completed_tools:
            summary_parts.append(f"Successfully completed actions: {', '.join(completed_tools)}.")
         
        if failed_tools:
            summary_parts.append(f"Encountered errors/failures during: {', '.join(failed_tools)}.")

        return " ".join(summary_parts)