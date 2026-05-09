from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient
from groq import Groq
import os

# load keys from .env file
load_dotenv()

print("Testing all API connections...\n")

# test Gemini
try:
    gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = gemini.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        contents="Say hello in one word"
    )
    print(f"Gemini OK: {response.text.strip()}")
except Exception as e:
    print(f"Gemini FAILED: {e}")

# test Tavily
try:
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    results = tavily.search(query="trending topics 2025", max_results=os.getenv("TAVILY_MAX_RESULTS", "5"))
    print(f"Tavily OK: found {len(results['results'])} result(s)")
except Exception as e:
    print(f"Tavily FAILED: {e}")

# test Groq
try:
    groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = groq.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-750b-versatile"),
        messages=[{"role": "user", "content": "Say hello in one word"}],
        max_tokens=10
    )
    print(f"Groq OK: {response.choices[0].message.content.strip()}")
except Exception as e:
    print(f"Groq FAILED: {e}")

print("\nDay 1 complete if all 3 show OK!")