# app.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.loop import run_trendjack_pipeline
from database.db import init_db, save_campaign, update_human_decision, get_all_campaigns
from utils.pdf_export import export_pdf

# ── Init DB on startup ───────────────────────────────────
init_db()

# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="TrendJack",
    page_icon="⚡",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────
st.title("⚡ TrendJack")
st.caption("AI-Powered Ad Campaign Generator")
st.divider()

# ── Tabs ─────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🚀 Generate Campaign", "📋 Campaign History"])

# ════════════════════════════════════════════════════════
# TAB 1 — GENERATE
# ════════════════════════════════════════════════════════
with tab1:

    st.subheader("Generate New Campaign")
    keyword = st.text_input("Enter a keyword or industry",
                             placeholder="e.g. skincare, electric cars, fitness")

    if st.button("⚡ Run TrendJack", type="primary"):

        if not keyword.strip():
            st.warning("Please enter a keyword first.")
        else:
            # ── Run Pipeline ─────────────────────────────
            with st.spinner("Running TrendJack pipeline..."):
                result = run_trendjack_pipeline(keyword.strip())

            # Save to DB
            campaign_id = save_campaign(result)

            # Store in session state for HITL
            st.session_state["result"]      = result
            st.session_state["campaign_id"] = campaign_id
            st.session_state["decision"]    = None

    # ── Show Result ──────────────────────────────────────
    if "result" in st.session_state and st.session_state["result"]:
        result      = st.session_state["result"]
        campaign_id = st.session_state["campaign_id"]
        ad          = result.get("ad_copy", {})
        val         = result.get("validation", {})
        trend       = result.get("trend", {})

        st.divider()

        # Trend Info
        st.markdown(f"**🔍 Trend:** {trend.get('title','')}")
        st.markdown(f"**🔗 Source:** {trend.get('url','')}")
        st.markdown(f"**🔄 Attempts:** {result.get('total_attempts', 1)}")
        st.divider()

        # Ad Copy
        st.subheader("📝 Generated Ad Copy")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📸 Instagram**")
            st.info(ad.get("instagram", ""))

        with col2:
            st.markdown("**🎵 TikTok**")
            st.info(ad.get("tiktok", ""))

        with col3:
            st.markdown("**💼 LinkedIn**")
            st.info(ad.get("linkedin", ""))

        st.divider()

        # Scores
        st.subheader("✅ Validation Scores")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Tone",           f"{val.get('tone_score',0)}/100")
        c2.metric("Brand Fit",      f"{val.get('brand_fit_score',0)}/100")
        c3.metric("Accuracy",       f"{val.get('accuracy_score',0)}/100")
        c4.metric("Trend Relevance",f"{val.get('trend_relevance',0)}/100")
        c5.metric("Overall",        f"{val.get('overall_score',0)}/100")

        # Reasoning
        with st.expander("🧠 AI Reasoning"):
            reasoning = val.get("reasoning", {})
            for key, text in reasoning.items():
                st.markdown(f"**{key.replace('_',' ').title()}:** {text}")

        st.divider()

        # ── HITL Decision ────────────────────────────────
        st.subheader("👤 Human Decision")

        if st.session_state.get("decision"):
            if st.session_state["decision"] == "approved":
                st.success("✅ Campaign APPROVED and exported!")
            else:
                st.error("❌ Campaign REJECTED.")
        else:
            notes = st.text_area("Notes (optional — required if rejecting)",
                                  placeholder="e.g. Tone too formal for TikTok...")

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("✅ Approve & Export PDF", type="primary"):
                    update_human_decision(campaign_id, "approved", notes)
                    pdf_path = export_pdf(campaign_id, result)
                    st.session_state["decision"] = "approved"
                    st.session_state["pdf_path"] = pdf_path
                    st.rerun()

            with col_b:
                if st.button("❌ Reject", type="secondary"):
                    if not notes.strip():
                        st.warning("Please add rejection notes before rejecting.")
                    else:
                        update_human_decision(campaign_id, "rejected", notes)
                        st.session_state["decision"] = "rejected"
                        st.rerun()

        # PDF Download
        if st.session_state.get("pdf_path"):
            with open(st.session_state["pdf_path"], "rb") as f:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=f,
                    file_name=os.path.basename(st.session_state["pdf_path"]),
                    mime="application/pdf"
                )

# ════════════════════════════════════════════════════════
# TAB 2 — HISTORY
# ════════════════════════════════════════════════════════
with tab2:
    st.subheader("Campaign History")

    campaigns = get_all_campaigns()

    if not campaigns:
        st.info("No campaigns yet. Generate your first one!")
    else:
        for c in campaigns:
            status_icon = (
                "✅" if c["human_decision"] == "approved" else
                "❌" if c["human_decision"] == "rejected" else
                "⏳"
            )
            with st.expander(
                f"{status_icon} [{c['id']}] {c['keyword'].upper()} — {c['created_at'][:16]}"
            ):
                st.markdown(f"**Trend:** {c['trend_title']}")
                st.markdown(f"**Attempts:** {c['total_attempts']}")
                st.markdown(f"**AI Passed:** {c['final_passed']}")
                st.markdown(f"**Human Decision:** {c['human_decision'] or 'Pending'}")
                if c["human_notes"]:
                    st.markdown(f"**Notes:** {c['human_notes']}")