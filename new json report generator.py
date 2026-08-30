import json
import streamlit as st
import os

def render_threat_report(json_file_path: str, image_file_path: str):
    """Reads the JSON report and renders a stylized dashboard in Streamlit."""
    
    if not os.path.exists(json_file_path):
        st.error(f"Report file not found: {json_file_path}")
        return

    with open(json_file_path, "r", encoding="utf-8") as f:
        report_data = json.load(f)

    status = report_data.get("status", "failed")
    ai_analysis = report_data.get("ai_analysis", "")

    if status == "failed":
        st.error("API Outage: All our servers are busy please try again later in 10 minutes.")
        return

    # --- Render the Dashboard ---
    st.markdown("<hr style='height: 3px; background-color: #b32121; margin: 25px 0;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-family: Orbitron, sans-serif;'>Threat Intelligence Verdict</h2>", unsafe_allow_html=True)
    st.write("") # Spacer

    col_img, col_report = st.columns([1, 1.5])

    # Left Column: Visual Evidence
    with col_img:
        st.subheader("Visual Telemetry")
        if os.path.exists(image_file_path):
            st.image(image_file_path, caption="Sandbox Snapshot", use_container_width=True)
        else:
            st.warning("Evidence image not found on disk.")

    # Right Column: AI Analysis breakdown
    with col_report:
        # Check if the site was flagged as completely clean
        if "clean and safe to use" in ai_analysis.lower():
            st.success("✅ **STATUS: CLEAN & SAFE**\n\nThe visual heuristics engine found no structural deceptive elements or credential harvesting indicators.")
        elif "high risk" in ai_analysis.lower() or "critical" in ai_analysis.lower():
            st.error("🚨 **STATUS: CRITICAL THREAT DETECTED**\n\nImmediate mitigation recommended.")
        else:
            st.warning("⚠️ **STATUS: SUSPICIOUS / AD-HEAVY**\n\nProceed with caution.")

        # Put the raw AI breakdown inside a stylized container
        st.markdown("### Forensic Breakdown")
        
        # We wrap the AI's 3-point list in a clean info box
        st.info(ai_analysis)

        # Optional: Add an interactive expander for raw JSON data for debugging
        with st.expander("View Raw JSON Telemetry"):
            st.json(report_data)