import streamlit as st
def render_result_visuals(result):
    st.caption(f"Provider: {result.get('provider','Unknown')} · Mode: {result.get('mode','unknown')}")
    if result.get("mode")=="fallback":st.info("Configure a Gemini API key to enable model-generated answers.")
    st.markdown("**Workflow stages**")
    st.bar_chart({"Stages completed":[1,1,1,1,1]})
