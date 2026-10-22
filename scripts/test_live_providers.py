import asyncio
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from pydantic import BaseModel
from app.config import get_settings
from app.providers.llm_gemini import GeminiLLMProvider
from app.providers.llm_groq import GroqLLMProvider
from app.providers.search_tavily import TavilySearchProvider
from app.providers.router import call_with_fallback

class TestSummary(BaseModel):
    status: str
    headline: str

async def main():
    settings = get_settings()
    print("Testing live provider integration through router...")

    gemini = GeminiLLMProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
    groq = GroqLLMProvider(api_key=settings.GROQ_API_KEY, model_name=settings.GROQ_MODEL)

    # 1. Test Router structured output with fallback capability
    messages = [{"role": "user", "content": "Respond with status 'active' and headline 'ScholarPilot Operational'"}]
    res = await call_with_fallback(
        [gemini, groq],
        lambda p: p.generate(task="live_test", messages=messages, schema=TestSummary),
    )
    print(f"Router LLM Success! Provider used: {res.provider}, Result: {res.value}")

    # 2. Test Tavily search integration
    tavily = TavilySearchProvider(api_key=settings.TAVILY_API_KEY)
    hits = await tavily.search("TU Munich computer science master scholarship", max_results=2)
    print(f"Tavily Search Success! Returned {len(hits)} hits:")
    for h in hits:
        print(f"  - [{h.provider}] {h.title}: {h.url}")

if __name__ == "__main__":
    asyncio.run(main())
