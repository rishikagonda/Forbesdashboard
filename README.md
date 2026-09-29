# Forbes 2026 Insights — Streamlit Dashboard

A professional Streamlit dashboard inspired by the reference layout: KPI cards, filters, charts, searchable content, downloadable results, and optional Gemini Q&A.

## Folder structure

```text
forbes_streamlit_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── forbes_2026_sample.csv
```

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually:

`http://localhost:8501`

## Your real Forbes data

Replace `data/forbes_2026_sample.csv` with your scraper's CSV, or upload a CSV from the sidebar.

The app recognizes common column names such as:
- title / article_title / headline
- category / categories / section
- person / author
- date / published_date
- url / link
- description / summary
- type / content_type

## Gemini API key

Do NOT put the API key in the Python file or GitHub.

For local testing, you can set an environment variable:

Windows PowerShell:
```powershell
$env:GEMINI_API_KEY="YOUR_KEY"
streamlit run app.py
```

For Streamlit Community Cloud:

1. Deploy the app.
2. Open the app's settings.
3. Open **Secrets**.
4. Add:

```toml
GEMINI_API_KEY = "YOUR_KEY"
```

5. Save/reboot the app.

## GitHub

From the project folder:

```bash
git init
git add .
git commit -m "Added Forbes Streamlit dashboard"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## Streamlit Community Cloud

1. Sign in with GitHub.
2. Create a new app.
3. Select your repository.
4. Branch: `main`
5. Main file: `app.py`
6. Click Deploy.

The app will receive a public Streamlit URL.

## Important

Do not commit:
- API keys
- `.env`
- `.streamlit/secrets.toml`
- virtual environments
