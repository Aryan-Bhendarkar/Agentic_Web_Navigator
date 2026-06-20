# CortexWeb Agent

An autonomous browser automation agent powered by Python, Playwright, LangGraph, and OpenRouter (Gemini Multimodal). The agent navigates websites, fills forms, handles coordinate-based clicking, and employs visual fallback strategies to bypass broken selector limitations.

---

## Features
- **LangGraph Orchestrator**: Loop planning architecture.
- **4-Level Element Detection**: Semantic DOM, CSS, XPath, and Multimodal Vision Fallback.
- **Structured LLM Actions**: Actions validated using Pydantic schemas.
- **Run Summary Logs**: Execution summaries serialized to `logs/run_memory.json` on finish.
- **Visual Failure Logging**: Automatic screenshot capture of page states on action timeouts.
- **Interactive Control Center**: Real-time FastAPI + HTML5/CSS3 glassmorphic monitor dashboard.

---

## Installation & Setup

1. **Clone & Setup Virtual Environment**:
   ```bash
   python -m venv venv
   ./venv/Scripts/activate  # Windows
   source venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   DEFAULT_LLM_MODEL=google/gemini-2.5-flash
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

---

## Running the Agent & Tests

### Web Control Center Dashboard
* Run the API & Frontend server:
  ```bash
  python -m uvicorn app:app --reload --port 8000
  ```
* Open `http://localhost:8000` to interact with the dashboard, view live logs, and browse step screenshots.

### CLI Execution
* Run the autonomous target task against Shadcn react-hook-form:
  ```bash
  python -m scratch.verify_shadcn
  ```
* Run the pytest suite:
  ```bash
  pytest tests/
  ```

### Docker Execution
* Build the docker container:
  ```bash
  docker build -t cortexweb-agent .
  ```
* Run unit tests inside Docker:
  ```bash
  docker run --rm cortexweb-agent
  ```
* Run the agent inside Docker (mounting logs and screenshots):
  ```bash
  docker run --rm --env-file .env -v ${PWD}/logs:/app/logs -v ${PWD}/screenshots:/app/screenshots cortexweb-agent python -m scratch.test_agent
  ```
