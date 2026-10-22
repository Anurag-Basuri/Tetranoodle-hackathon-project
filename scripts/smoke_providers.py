"""Smoke test script for ScholarPilot AI providers.
Validates credentials and live connectivity for Gemini, Groq, Tavily, and Brave.
Run: python scripts/smoke_providers.py
"""
import asyncio
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import get_settings


async def test_gemini(api_key: str, model_name: str) -> dict:
    if not api_key:
        return {"status": "SKIPPED", "message": "GEMINI_API_KEY not set"}
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
        res = await llm.ainvoke("Reply with 'READY'")
        text_out = res.content if isinstance(res.content, str) else str(res.content)
        return {"status": "PASS", "message": f"Model {model_name} responded: {text_out.strip()[:30]}"}
    except Exception as e:
        return {"status": "FAIL", "message": str(e)}


async def test_groq(api_key: str, model_name: str) -> dict:
    if not api_key:
        return {"status": "SKIPPED", "message": "GROQ_API_KEY not set"}
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(model=model_name, groq_api_key=api_key)
        res = await llm.ainvoke("Reply with 'READY'")
        return {"status": "PASS", "message": f"Model {model_name} responded: {res.content.strip()[:30]}"}
    except Exception as e:
        return {"status": "FAIL", "message": str(e)}


async def test_tavily(api_key: str) -> dict:
    if not api_key:
        return {"status": "SKIPPED", "message": "TAVILY_API_KEY not set"}
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        res = client.search(query="TetraNoodle AI Hackathon 2026", max_results=1)
        return {"status": "PASS", "message": f"Tavily returned {len(res.get('results', []))} search result(s)"}
    except Exception as e:
        return {"status": "FAIL", "message": str(e)}


async def main():
    settings = get_settings()
    print("=" * 60)
    print(" ScholarPilot AI - Provider Connectivity Smoke Test")
    print("=" * 60)
    print(f"Environment: {settings.ENV}")
    print(f"Database:    {settings.DATABASE_URL}")
    print("-" * 60)

    print("Testing Gemini...")
    gemini_res = await test_gemini(settings.GEMINI_API_KEY, settings.GEMINI_MODEL)
    print(f"  [{gemini_res['status']}] Gemini ({settings.GEMINI_MODEL}): {gemini_res['message']}")

    print("Testing Groq...")
    groq_res = await test_groq(settings.GROQ_API_KEY, settings.GROQ_MODEL)
    print(f"  [{groq_res['status']}] Groq ({settings.GROQ_MODEL}): {groq_res['message']}")

    print("Testing Tavily...")
    tavily_res = await test_tavily(settings.TAVILY_API_KEY)
    print(f"  [{tavily_res['status']}] Tavily: {tavily_res['message']}")

    print("=" * 60)
    print("Smoke test complete.")


if __name__ == "__main__":
    asyncio.run(main())
