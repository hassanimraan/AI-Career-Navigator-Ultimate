# 🧭 AI Career Navigator

A beginner-friendly AI career counselor MVP built with:

- Python
- Streamlit
- Gemini API
- ESCO occupation/skills knowledge
- Pydantic structured outputs
- PyMuPDF for PDF CVs
- python-docx for DOCX CVs
- Plotly for skill-gap visualization
- Streamlit session state

## MVP capabilities

1. Career profile collection
2. Optional PDF/DOCX CV extraction
3. Gemini-powered career assessment
4. ESCO occupation context
5. 3–5 career recommendations
6. Match scores and explanations
7. Strengths and skill gaps
8. Learning roadmap
9. Recommended portfolio projects
10. AI Career Counselor
11. Beginner / Intermediate / Expert explanation levels

## 1. Create and activate a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate
```

## 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure Gemini

Copy `.env.example` to `.env` and replace:

```text
GEMINI_API_KEY=your_key_here
```

Do not commit `.env`.

## 4. Run

```bash
streamlit run app.py
```

## Streamlit Cloud

1. Push the project to GitHub.
2. Create a Streamlit Community Cloud app.
3. Select the repository and `app.py`.
4. Add the same secrets under the app's Secrets settings:

```toml
GEMINI_API_KEY = "your_real_key"
GEMINI_MODEL = "gemini-2.5-flash"
ESCO_BASE_URL = "https://ec.europa.eu/esco/api"
```

## Notes

- ESCO is used as structured occupational context; the AI still performs the personalized reasoning.
- Match scores are guidance estimates, not employment predictions.
- CV text is processed in the app session and is not intentionally persisted by this MVP.


## Important deployment note

For Streamlit Community Cloud, the GitHub repository should contain the project files in a simple structure where `app.py` is the selected entrypoint. If you keep the `ai_career_navigator` folder as a subfolder, select `ai_career_navigator/app.py` as the Main file path when deploying.

The app now explicitly navigates when buttons are clicked. The AI Career Counselor also has a **Get Guidance** button: selecting Beginner/Intermediate/Expert changes the answer style, while the button actually asks Gemini for a result.

### Local troubleshooting

Run these commands from the folder containing `app.py`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If the app is already running, save the file and refresh the browser.

### Streamlit Community Cloud

After pushing a code change to GitHub, Community Cloud normally redeploys the app automatically. If it does not, open your app's Cloud logs and reboot it.

For secrets, open the app's **Settings → Secrets** and add:

```toml
GEMINI_API_KEY = "your_real_gemini_key"
GEMINI_MODEL = "gemini-2.5-flash"
ESCO_BASE_URL = "https://ec.europa.eu/esco/api"
```

Never commit your real API key to GitHub.
