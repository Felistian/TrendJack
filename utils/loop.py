# utils/loop.py
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.researcher_trend import research_trends
from agents.creator import create_ad_copy
from agents.validator import validate_ad_copy
from dotenv import load_dotenv
import os

load_dotenv()

MAX_RETRIES = 3

def run_trendjack_pipeline(keyword: str) -> dict:
    """
    Full TrendJack pipeline:
    Researcher → Creator → Validator → (retry if failed)

    Args:
        keyword: Topic to research (e.g. "skincare", "electric cars")

    Returns:
        dict with full pipeline result including all attempts
    """

    print(f"\n{'='*50}")
    print(f"  TrendJack Pipeline Starting")
    print(f"  Keyword: {keyword}")
    print(f"{'='*50}\n")

    # ── STEP 1: RESEARCHER ──────────────────────────────
    print("[ Step 1 ] Researcher searching trends...")
    trends = research_trends(keyword)

    if not trends:
        return {
            "status": "error",
            "message": "Researcher returned no trends.",
            "keyword": keyword
        }

    # Pick the first trend
    selected_trend = trends[0]
    print(f"           Trend selected: {selected_trend['title'][:60]}...")

    # ── STEP 2: CREATOR + VALIDATOR LOOP ────────────────
    attempts = []
    feedback = None

    for attempt_num in range(1, MAX_RETRIES + 1):

        print(f"\n[ Step 2 ] Creator generating ad copy (Attempt {attempt_num}/{MAX_RETRIES})...")

        # Pass feedback from previous attempt if available
        trend_with_feedback = selected_trend.copy()
        if feedback:
            trend_with_feedback["feedback"] = feedback
            print(f"           Feedback from last attempt passed to Creator.")

        ad_copy = create_ad_copy(trend_with_feedback)
        print(f"           Ad copy generated ✓")

        print(f"\n[ Step 3 ] Validator scoring ad copy...")
        validation = validate_ad_copy(selected_trend, ad_copy)

        overall  = validation.get("overall_score", 0)
        passed   = validation.get("passed", False)
        feedback = validation.get("feedback", "")

        print(f"           Overall Score : {overall}/100")
        print(f"           Passed        : {passed}")

        # Store this attempt
        attempts.append({
            "attempt_number" : attempt_num,
            "ad_copy"        : ad_copy,
            "validation"     : validation
        })

        if passed:
            print(f"\n✅ Passed on attempt {attempt_num}!")
            break
        else:
            print(f"❌ Failed. Feedback: {feedback[:80]}...")
            if attempt_num < MAX_RETRIES:
                print(f"   Retrying with feedback...\n")
            else:
                print(f"\n⚠️  Max retries reached. Sending to human for review.")

    # ── STEP 4: RETURN FULL RESULT ───────────────────────
    final_attempt  = attempts[-1]
    final_copy     = final_attempt["ad_copy"]
    final_validation = final_attempt["validation"]

    return {
        "status"      : "success",
        "keyword"     : keyword,
        "trend"       : selected_trend,
        "ad_copy"     : final_copy,
        "validation"  : final_validation,
        "attempts"    : attempts,
        "total_attempts" : len(attempts),
        "final_passed"   : final_validation.get("passed", False)
    }


# --- TEMP TEST --- remove before integrating ---
if __name__ == "__main__":
    result = run_trendjack_pipeline("skincare")

    print(f"\n{'='*50}")
    print(f"  FINAL RESULT")
    print(f"{'='*50}")
    print(f"Keyword       : {result['keyword']}")
    print(f"Total Attempts: {result['total_attempts']}")
    print(f"Final Passed  : {result['final_passed']}")
    print(f"\n--- Final Ad Copy ---")
    print(f"INSTAGRAM : {result['ad_copy']['instagram']}")
    print(f"TIKTOK    : {result['ad_copy']['tiktok']}")
    print(f"LINKEDIN  : {result['ad_copy']['linkedin']}")
    print(f"\n--- Final Scores ---")
    v = result['validation']
    print(f"Tone            : {v['tone_score']}/100")
    print(f"Brand Fit       : {v['brand_fit_score']}/100")
    print(f"Accuracy        : {v['accuracy_score']}/100")
    print(f"Trend Relevance : {v['trend_relevance']}/100")
    print(f"Overall         : {v['overall_score']}/100")