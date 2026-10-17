import os
def run_agent_task(prompt,discipline,task_type,attachment_text=""):
    stages=[{"name":"1 · Intake & classification","summary":f"Classified the request as {task_type} within {discipline}."},{"name":"2 · Planning","summary":"Structured the request into an answer plan."},{"name":"3 · Specialist response","summary":"Prepared a response using the configured provider or a transparent fallback."},{"name":"4 · Review","summary":"Checked relevance, clarity and obvious inconsistencies."},{"name":"5 · Reporting","summary":"Formatted the response for project history."}]
    key=os.getenv("GEMINI_API_KEY","").strip()
    try:
        import streamlit as st
        if not key:key=str(st.secrets.get("GEMINI_API_KEY","")).strip()
    except Exception:pass
    if key:
        try:
            from google import genai
            client=genai.Client(api_key=key)
            extra=f"\\n\\nSupporting file text:\\n{attachment_text[:20000]}" if attachment_text else ""
            content=f"""You are UniVerse AI, a careful educational and productivity assistant.
Discipline: {discipline}
Task type: {task_type}
User request: {prompt}{extra}
Answer the exact request clearly with useful detail. Do not invent facts; state uncertainty. For medical education, provide learning simulation only, not diagnosis or treatment for a real patient. If code is requested, format it as a code block."""
            response=client.models.generate_content(model="gemini-3.8-flash",contents=content)
            answer=getattr(response,"text",None) or "The model returned an empty response. Please retry."
            return {"answer":answer,"provider":"Gemini 2.5 Flash","mode":"model","discipline":discipline,"task_type":task_type,"stages":stages,"limitations":[]}
        except Exception as e:
            return {"answer":"The AI provider request failed. Check your API key, model access, network and quota. No AI-generated answer is being presented as successful.","provider":"Gemini","mode":"error","discipline":discipline,"task_type":task_type,"stages":stages,"limitations":["Provider error: "+str(e)[:220]]}
    answer=f"""## Task received

**Discipline:** {discipline}  
**Task type:** {task_type}

You submitted:

> {prompt.strip()}

"""
    if attachment_text:answer+="\\n### Supporting file preview\\n\\n"+attachment_text[:3000]
    answer+="\\n\\n### Enable AI responses\\nConfigure `GEMINI_API_KEY` in Streamlit Community Cloud → App settings → Secrets. This is a local fallback; no language model was called."
    return {"answer":answer,"provider":"None configured","mode":"fallback","discipline":discipline,"task_type":task_type,"stages":stages,"limitations":["No AI provider key configured; this is not an AI-generated answer."]}
