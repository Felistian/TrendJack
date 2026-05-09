# agents/researcher.py
from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

def research_trends(keyword: str, max_results: int = 5) -> list[dict]:
    """
    Search for trending topics using Tavily API.
    
    Args:
        keyword: Topic to search (e.g. "skincare", "electric cars")
        max_results: How many results to return (default 5)
    
    Returns:
        List of dicts with 'title', 'url', 'content' keys
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    response = client.search(
        query=f"trending {keyword} 2025 advertising marketing",
        search_depth="basic",
        max_results=max_results
    )

    trends = []
    for result in response.get("results", []):
        trends.append({
            "title": result.get("title", "No title"),
            "url": result.get("url", ""),
            "content": result.get("content", "")[:300]  # trim long text
        })

    return trends






# --- TEMP TEST — remove before integrating ---
if __name__ == "__main__":
    results = research_trends("skincare")
    for i, trend in enumerate(results, 1):
        print(f"\n--- Trend {i} ---")
        print(f"Title  : {trend['title']}")
        print(f"URL    : {trend['url']}")
        print(f"Snippet: {trend['content'][:100]}...")