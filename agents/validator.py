# agents/validator.py
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

def validate_ad_copy(trend: dict, ad_copy: dict) -> dict:
    """
    Validate ad copy using Groq/Llama.

    Args:
        trend   : dict with 'title', 'content' (from researcher)
        ad_copy : dict with 'instagram', 'tiktok', 'linkedin' (from creator)

    Returns:
        dict with 'scores', 'reasoning', 'passed', 'feedback'
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
You are a strict advertising quality validator.

ORIGINAL TREND:
Title: {trend['title']}
Context: {trend['content']}

AD COPY TO VALIDATE:
Instagram: {ad_copy['instagram']}
TikTok: {ad_copy['tiktok']}
LinkedIn: {ad_copy['linkedin']}

Evaluate the ad copy on these 4 criteria. Score each from 0-100.

CRITERIA:
1. tone_score       - Is the writing style right for each platform's audience?
2. brand_fit_score  - Does the copy feel consistent and professional?
3. accuracy_score   - Are there any false claims or hallucinations?
4. trend_relevance  - Does the copy naturally connect to the trend?

PASSING THRESHOLD: 70 for each criterion.

Respond ONLY with valid JSON. No explanation outside the JSON.

{{
  "tone_score": <0-100>,
  "brand_fit_score": <0-100>,
  "accuracy_score": <0-100>,
  "trend_relevance": <0-100>,
  "overall_score": <average of the 4>,
  "passed": <true if all scores >= 70, else false>,
  "reasoning": {{
    "tone": "<one sentence explanation>",
    "brand_fit": "<one sentence explanation>",
    "accuracy": "<one sentence explanation>",
    "trend_relevance": "<one sentence explanation>"
  }},
  "feedback": "<If passed is false: specific instructions on what to improve. If passed is true: write OK>"
}}
"""

    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw_text = response.choices[0].message.content
    return parse_validation(raw_text)


def parse_validation(raw_text: str) -> dict:
    """
    Parse Groq's JSON response safely.
    """
    try:
        # Strip markdown code fences if present
        clean = raw_text.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except json.JSONDecodeError:
        return {
            "tone_score": 0,
            "brand_fit_score": 0,
            "accuracy_score": 0,
            "trend_relevance": 0,
            "overall_score": 0,
            "passed": False,
            "reasoning": {
                "tone": "Parse error",
                "brand_fit": "Parse error",
                "accuracy": "Parse error",
                "trend_relevance": "Parse error"
            },
            "feedback": f"Validator parsing failed. Raw response: {raw_text[:200]}"
        }


# --- TEMP TEST --- remove before integrating ---
if __name__ == "__main__":
    sample_trend = {
        "title": "Beauty ads in 2025 don't just promise radiant skin",
        "content": "Brands are shifting to science-backed claims and 3D visuals in skincare marketing."
    }

    sample_copy = {
        "instagram": "Skincare, decoded. We're trading empty promises for clinical data. #SkincareSciencee #BeautyTech",
        "tiktok": "Forget the filters — we're entering our science era. Ready to see what's actually inside your jar?",
        "linkedin": "The beauty industry is undergoing a paradigm shift toward radical transparency. How will your brand prove its value?"
    }

    print("Sending to Groq for validation...\n")
    result = validate_ad_copy(sample_trend, sample_copy)

    print(f"Tone Score      : {result['tone_score']}/100")
    print(f"Brand Fit Score : {result['brand_fit_score']}/100")
    print(f"Accuracy Score  : {result['accuracy_score']}/100")
    print(f"Trend Relevance : {result['trend_relevance']}/100")
    print(f"Overall Score   : {result['overall_score']}/100")
    print(f"Passed          : {result['passed']}")
    print(f"\n--- Reasoning ---")
    for key, val in result['reasoning'].items():
        print(f"{key:16}: {val}")
    print(f"\n--- Feedback ---")
    print(result['feedback'])