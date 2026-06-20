import sys
import asyncio
import threading
import queue

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import json
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from agent.executor import agent_app
from config.settings import settings
import tools.browser_tools as browser_tools_module

# Configure logging
logger = logging.getLogger("CortexWebAPI")

app = FastAPI(title="CortexWeb Agent API")

# Ensure directories exist
settings.get_absolute_screenshots_dir()
settings.get_absolute_logs_dir()
Path("static").mkdir(exist_ok=True)

# Mount screenshots directory to serve them to the web page
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

@app.post("/api/run")
async def run_agent(request: Request):
    data = await request.json()
    objective = data.get("objective", "")

    # Reset browser singleton so each /api/run gets a fresh browser session
    browser_tools_module._controller = None
    browser_tools_module._actions = None
    browser_tools_module._detector = None

    # Initial state initialization
    initial_state = {
        "objective": objective,
        "history": [],
        "current_url": None,
        "screenshot_path": None,
        "attempts": 0,
        "status": "running",
        "next_tool": None,
        "next_tool_args": None,
        "thought": None
    }

    event_queue = queue.Queue()

    def run_agent_thread():
        # Force a ProactorEventLoop in this background thread on Windows
        if sys.platform == 'win32':
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run():
            try:
                # Stream the compiled LangGraph execution loops
                async for update in agent_app.astream(initial_state, stream_mode="updates"):
                    node_name = list(update.keys())[0]
                    node_data = update[node_name]

                    payload = {
                        "node": node_name,
                        "data": {}
                    }

                    # Format custom Pydantic list objects to standard JSON dict lists
                    if "history" in node_data:
                        history = node_data["history"]
                        if history:
                            payload["data"]["history"] = [step.model_dump() for step in history]
                            last_step = history[-1]
                            payload["data"]["last_step"] = {
                                "tool": last_step.tool,
                                "args": last_step.args,
                                "observation": last_step.observation
                            }

                    # Forward thought from planner node
                    if "thought" in node_data and node_data["thought"] is not None:
                        payload["data"]["thought"] = node_data["thought"]

                    # Map other details
                    for field in ["current_url", "screenshot_path", "attempts", "next_tool", "next_tool_args", "status"]:
                        if field in node_data:
                            payload["data"][field] = node_data[field]
                            if field == "screenshot_path" and node_data[field]:
                                p = Path(node_data[field])
                                payload["data"]["screenshot_url"] = f"/screenshots/{p.name}"

                    event_queue.put(("event", payload))

            except Exception as e:
                logger.error(f"SSE generator encountered an error: {e}", exc_info=True)
                event_queue.put(("error", str(e)))
            finally:
                # Always attempt to clean up the browser when streaming ends
                try:
                    ctrl = browser_tools_module._controller
                    if ctrl and ctrl.playwright:
                        await ctrl.close()
                        logger.info("Browser session cleaned up after SSE stream ended in thread.")
                except Exception as cleanup_err:
                    logger.warning(f"Browser cleanup after stream failed in thread: {cleanup_err}")
                
                # Signal completion
                event_queue.put(("done", None))

        loop.run_until_complete(run())
        loop.close()

    # Start thread
    threading.Thread(target=run_agent_thread, daemon=True).start()

    async def event_generator():
        while True:
            try:
                msg_type, val = event_queue.get_nowait()
                if msg_type == "event":
                    yield f"data: {json.dumps(val)}\n\n"
                elif msg_type == "error":
                    error_payload = {"node": "system", "data": {"status": "failed", "error": val}}
                    yield f"data: {json.dumps(error_payload)}\n\n"
                elif msg_type == "done":
                    break
            except queue.Empty:
                await asyncio.sleep(0.05)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )

# Mount static folder for frontend (index.html is served automatically at root)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
