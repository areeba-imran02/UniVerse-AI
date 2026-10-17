# UniVerse AI — Streamlit

Streamlit-first workspace with signup/login, salted PBKDF2 password hashes, protected dashboard rendering, per-account SQLite project history, study utilities, and optional Gemini AI.

## Run locally
Python 3.10+ recommended:
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Gemini
Set `GEMINI_API_KEY` in your environment, or Streamlit Community Cloud → App settings → Secrets:
```toml
GEMINI_API_KEY = "your-real-key"
```
Never commit a real key or `.env` file.

## Deploy
Upload the contents of this folder to your GitHub repository root, select it in Streamlit Community Cloud, set Main file path to `app.py`, add the secret if you want AI responses, then deploy.

## Production limitations — read before public launch
This is a functional starter, not a hardened enterprise identity service. Streamlit session state is used for signed-in UI flow; use a dedicated identity provider for robust signed/rotating server-side sessions, MFA, rate limits and CSRF protections. The password reset form currently changes a password after an email address is entered but does not prove email ownership. **Do not expose it publicly as-is**; replace with an emailed, one-time, expiring reset token or managed identity provider. SQLite is for a small single-instance starter; Streamlit Community Cloud local disk may not be durable. For production, use persistent hosted PostgreSQL and managed authentication. Medical education mode is for learning simulation, not real-patient diagnosis or treatment.
