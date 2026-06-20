# CortexWeb: Autonomous Web Navigation Agent

CortexWeb is an autonomous browser automation agent built using Python, Playwright, and LangGraph. It enables large language models (LLMs) to navigate web interfaces, interact with complex forms, recover from selector timeouts, and fall back to computer vision for coordinate-based actions when traditional DOM elements are unreachable.

Includes a live glassmorphic dashboard built on FastAPI (SSE streaming) to monitor the agent's planner thoughts, logs, and viewport screenshots in real time.

---

## Technical Highlights & Engineering Challenges Solved

### 1. Multi-Threaded Event Loop Isolation (Windows Compatibility)
* **Challenge**: On Windows, Playwright requires a `ProactorEventLoop` to manage browser subprocesses. However, Uvicorn's hot-reload mode forces Python to use the `SelectorEventLoop` to watch files, which crashes Playwright with a `NotImplementedError` upon browser startup.
* **Solution**: Implemented a decoupled multithreaded architecture in `app.py`. The web server receives requests and launches the LangGraph agent in a dedicated background thread running its own `ProactorEventLoop`. Events are piped back to the main thread's Server-Sent Events (SSE) generator via a thread-safe `queue.Queue`.

### 2. Self-Correcting Structured Outputs
* **Challenge**: Multimodal LLMs occasionally output schemas that violate Pydantic validation rules, causing the agent to halt mid-execution.
* **Solution**: Developed a 3-step structured retry loop within `AgentPlanner`. On a validation error, the planner catches the exception, appends the parser error to the message history, and retries. This corrective feedback loop allows the model to immediately repair its own JSON responses.

### 3. 4-Level Resilient Element Detection
* **Challenge**: Modern dynamic frontend frameworks (React, Vue) often obfuscate selectors or render dynamic DOM nodes that cause standard automated clicks to fail.
* **Solution**: Created a layered element resolution pipeline:
  1. **Semantic Search**: Checks accessibility labels, placeholders, and ARIA attributes.
  2. **Direct Selectors**: Queries fallback CSS patterns.
  3. **XPath Matches**: Attempts generic hierarchy checks.
  4. **Multimodal Visual Detection**: Captures a page screenshot, queries the LLM with vision support (Gemini 2.5 Flash) to locate the element's approximate coordinate center `(x, y)`, and executes a physical mouse click.

---

## Core Stack
* **Orchestration**: LangGraph (StateGraph machine loop)
* **Automation**: Playwright (Async Python API)
* **Model Routing**: OpenRouter (Google Gemini 2.5 Flash)
* **Server & Frontend**: FastAPI, Server-Sent Events (SSE), HTML5/Vanilla CSS3

---

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure Environment**:
   Create a `.env` file in the root:
   ```env
   DEFAULT_LLM_MODEL=google/gemini-2.5-flash
   OPENROUTER_API_KEY=your_key_here
   ```

3. **Run the Dashboard**:
   ```bash
   python -m uvicorn app:app --reload --port 8000
   ```
   Open `http://localhost:8000` to select objectives and launch the agent.
