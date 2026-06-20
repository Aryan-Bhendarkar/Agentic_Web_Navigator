import asyncio
from config.settings import settings
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Dict, Any

class AgentAction(BaseModel):
    thought: str = Field(description="Reasoning")
    tool: str = Field(description="Tool")
    args: Dict[str, Any] = Field(default_factory=dict, description="Arguments")

async def test_model(model_name: str):
    print(f"\n--- Testing model: {model_name} ---")
    llm = ChatOpenAI(
        model=model_name,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENROUTER_BASE_URL,
        temperature=0.0,
        max_tokens=1000
    )
    
    try:
        structured_llm = llm.with_structured_output(AgentAction)
        print("Invoking structured output...")
        result = await structured_llm.ainvoke("Just open the browser and let's start.")
        print(f"Success! Result: {result}")
        return True
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

async def main():
    models = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "openrouter/free",
        "google/gemini-2.5-flash:free"
    ]
    for model in models:
        success = await test_model(model)
        if success:
            print(f"\nRECOMMENDED MODEL FOUND: {model}")
            break

if __name__ == "__main__":
    asyncio.run(main())
