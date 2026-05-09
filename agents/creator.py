# agents/creator.py
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

def create_ad_copy(trend: dict) -> dict:
    """
    Generate ad copy for 3 platforms using Gemini.

    Args:
        trend: dict with 'title' and 'content' keys (from researcher)

    Returns:
        dict with 'instagram', 'tiktok', 'linkedin' keys
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
You are a professional advertising copywriter.

Based on this trending topic:
Title: {trend['title']}
Context: {trend['content']}

Write ad copy for THREE platforms. Follow these rules strictly:

INSTAGRAM:
- 1 punchy opening line
- 2-3 short sentences max
- End with 3-5 relevant hashtags

TIKTOK:
- Start with a hook (question or bold statement)
- Casual, energetic, Gen-Z friendly tone
- Max 3 sentences
- End with a call-to-action

LINKEDIN:
- Professional tone
- 2-3 sentences about industry insight
- End with a thought-provoking question

Format your response EXACTLY like this:
INSTAGRAM: [copy here]
TIKTOK: [copy here]
LINKEDIN: [copy here]
"""

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        contents=prompt
    )

    raw_text = response.text
    return parse_ad_copy(raw_text)


def parse_ad_copy(raw_text: str) -> dict:
    """
    Parse Gemini's raw response into a structured dict.
    """
    result = {
        "instagram": "",
        "tiktok": "",
        "linkedin": ""
    }

    lines = raw_text.strip().split("\n")
    current_platform = None
    buffer = []

    for line in lines:
        line_upper = line.upper()

        if line_upper.startswith("INSTAGRAM:"):
            current_platform = "instagram"
            buffer = [line[len("INSTAGRAM:"):].strip()]
        elif line_upper.startswith("TIKTOK:"):
            if current_platform:
                result[current_platform] = " ".join(buffer).strip()
            current_platform = "tiktok"
            buffer = [line[len("TIKTOK:"):].strip()]
        elif line_upper.startswith("LINKEDIN:"):
            if current_platform:
                result[current_platform] = " ".join(buffer).strip()
            current_platform = "linkedin"
            buffer = [line[len("LINKEDIN:"):].strip()]
        elif current_platform:
            buffer.append(line.strip())

    if current_platform:
        result[current_platform] = " ".join(buffer).strip()

    return result




# --- TEMP TEST --- remove before integrating ---
if __name__ == "__main__":
    sample_trend = {
        "title": "Beauty ads in 2025 don't just promise radiant skin",
        "content": "Brands are shifting to science-backed claims and 3D visuals in skincare marketing."
    }

    print("Sending trend to Gemini...\n")
    ad_copy = create_ad_copy(sample_trend)

    print("=== INSTAGRAM ===")
    print(ad_copy["instagram"])
    print("\n=== TIKTOK ===")
    print(ad_copy["tiktok"])
    print("\n=== LINKEDIN ===")
    print(ad_copy["linkedin"])