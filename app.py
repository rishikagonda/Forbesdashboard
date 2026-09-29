import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Forbes 2026 Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
    .main { background: #f7f8fc; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
    .hero {
        padding: 1.2rem 1.4rem;
        border-radius: 18px;
        background: linear-gradient(90deg, #111827, #312e81);
        color: white;
        margin-bottom: 1rem;
    }
    .hero h1 { margin: 0; font-size: 2.15rem; }
    .hero p { margin: .35rem 0 0; opacity: .9; }
    .kpi {
        background: white;
        border: 1px solid #e8eaf0;
        border-radius: 16px;
        padding: 1rem 1.1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,.04);
    }
    .kpi-label { color: #6b7280; font-size: .88rem; }
    .kpi-value { color: #111827; font-size: 1.65rem; font-weight: 700; }
    .section-title { font-size: 1.15rem; font-weight: 700; margin: .7rem 0; }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e8eaf0;
        padding: 12px;
        border-radius: 14px;
    }
</style>
""", unsafe_allow_html=True)


# ---------- Data ----------
@st.cache_data
def load_default_data():
    path = "data/forbes_2026_sample.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=["title", "category", "person", "date", "url", "description"])


def normalize_columns(df):
    """Map common column names into a small standard schema without deleting original columns."""
    out = df.copy()
    rename = {}
    aliases = {
        "title": ["title", "article_title", "name", "headline"],
        "category": ["category", "categories", "section", "topic"],
        "person": ["person", "author", "person_name", "name_of_person"],
        "date": ["date", "published_date", "publication_date", "published"],
        "url": ["url", "link", "article_url"],
        "description": ["description", "summary", "excerpt", "content"],
        "type": ["type", "content_type", "format"],
    }
    lower = {str(c).strip().lower(): c for c in out.columns}
    for standard, names in aliases.items():
        for n in names:
            if n in lower:
                rename[lower[n]] = standard
                break
    out = out.rename(columns=rename)

    for c in ["title", "category", "person", "url", "description", "type"]:
        if c not in out.columns:
            out[c] = ""

    if "date" not in out.columns:
        out["date"] = pd.NaT
    out["date"] = pd.to_datetime(out["date"], errors="coerce")

    for c in ["title", "category", "person", "url", "description", "type"]:
        out[c] = out[c].fillna("").astype(str)

    return out


df = normalize_columns(load_default_data())

# ---------- Header ----------
st.markdown("""
<div class="hero">
    <h1>📊 Forbes 2026 Insights</h1>
    <p>Interactive content analytics dashboard with search, filters, visualizations and AI Q&A.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("🔎 Dashboard Filters")

    uploaded = st.file_uploader(
        "Upload your Forbes CSV",
        type=["csv"],
        help="Upload a CSV exported by your scraper. The app also accepts common column names."
    )
    if uploaded is not None:
        df = normalize_columns(pd.read_csv(uploaded))

    search = st.text_input("Search", placeholder="Search articles, people, topics...")

    categories = sorted([x for x in df["category"].dropna().unique() if x])
    selected_categories = st.multiselect("Category", categories)

    types = sorted([x for x in df["type"].dropna().unique() if x])
    selected_types = st.multiselect("Content type", types)

    if df["date"].notna().any():
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        date_range = st.date_input(
            "Publication date",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    else:
        date_range = None

# ---------- Filtering ----------
filtered = df.copy()

if selected_categories:
    filtered = filtered[filtered["category"].isin(selected_categories)]

if selected_types:
    filtered = filtered[filtered["type"].isin(selected_types)]

if search:
    mask = (
        filtered["title"].str.contains(search, case=False, na=False)
        | filtered["person"].str.contains(search, case=False, na=False)
        | filtered["category"].str.contains(search, case=False, na=False)
        | filtered["description"].str.contains(search, case=False, na=False)
    )
    filtered = filtered[mask]

if date_range and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[
        filtered["date"].isna()
        | ((filtered["date"] >= start) & (filtered["date"] <= end + pd.Timedelta(days=1)))
    ]

# ---------- KPIs ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Records", f"{len(filtered):,}")
c2.metric("Categories", f"{filtered['category'].replace('', pd.NA).nunique():,}")
c3.metric("People", f"{filtered['person'].replace('', pd.NA).nunique():,}")
c4.metric("Search Results", f"{len(filtered):,}")

st.divider()

if filtered.empty:
    st.info("No records match the current filters. Upload your scraper CSV or change the filters.")
else:
    # ---------- Charts ----------
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-title">📊 Content by Category</div>', unsafe_allow_html=True)
        cat = filtered["category"].replace("", "Unknown").value_counts().reset_index()
        cat.columns = ["category", "count"]
        fig = px.bar(cat.head(15), x="category", y="count", text="count")
        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Records",
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<div class="section-title">📈 Content Over Time</div>', unsafe_allow_html=True)
        dated = filtered.dropna(subset=["date"]).copy()
        if not dated.empty:
            trend = dated.assign(day=dated["date"].dt.date).groupby("day").size().reset_index(name="count")
            fig2 = px.line(trend, x="day", y="count", markers=True)
            fig2.update_layout(
                xaxis_title="Date",
                yaxis_title="Records",
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Add a valid date column to display the time trend.")

    left2, right2 = st.columns(2)

    with left2:
        st.markdown('<div class="section-title">🏆 Top People</div>', unsafe_allow_html=True)
        people = filtered["person"].replace("", pd.NA).dropna().value_counts().head(10).reset_index()
        people.columns = ["person", "count"]
        if not people.empty:
            fig3 = px.bar(people, x="count", y="person", orientation="h", text="count")
            fig3.update_layout(margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No person/author data found.")

    with right2:
        st.markdown('<div class="section-title">📰 Content Type</div>', unsafe_allow_html=True)
        if filtered["type"].replace("", pd.NA).notna().any():
            typ = filtered["type"].replace("", "Unknown").value_counts().reset_index()
            typ.columns = ["type", "count"]
            fig4 = px.pie(typ, names="type", values="count", hole=.45)
            fig4.update_layout(margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No content-type column found.")

    # ---------- Results ----------
    st.markdown('<div class="section-title">📋 Forbes Content</div>', unsafe_allow_html=True)
    display_cols = ["title", "category", "person", "date", "type", "url"]
    display = filtered[display_cols].copy()
    display["date"] = display["date"].dt.strftime("%Y-%m-%d")
    display.columns = ["Title", "Category", "Person", "Date", "Type", "URL"]
    st.dataframe(display, use_container_width=True, hide_index=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered data",
        data=csv,
        file_name="forbes_2026_filtered.csv",
        mime="text/csv",
    )

# ---------- AI Q&A ----------
st.divider()
st.markdown("## 🤖 Ask the Forbes Data")

question = st.text_input(
    "Ask a question about the currently loaded data",
    placeholder="Example: Which categories have the most articles?"
)

if question:
    # First provide a deterministic answer for common analytical questions.
    q = question.lower()
    answer = None

    if "most" in q and "categor" in q:
        counts = filtered["category"].replace("", "Unknown").value_counts().head(5)
        answer = "Top categories:\n\n" + "\n".join(
            [f"- {k}: {v}" for k, v in counts.items()]
        )

    elif "how many" in q or "number of" in q or "total" in q:
        answer = f"There are **{len(filtered):,} records** in the current filtered dataset."

    # Optional Gemini answer for broader natural-language questions.
    if answer is None:
        api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        if api_key:
            try:
                from google import genai

                client = genai.Client(api_key=api_key)
                context = filtered[
                    ["title", "category", "person", "date", "type", "description"]
                ].head(80).to_csv(index=False)

                prompt = f"""
You are an analytics assistant for a Forbes 2026 content dashboard.
Answer the user's question using only the dataset context below.
If the data does not support the answer, say so clearly.
Keep the response concise.

Question:
{question}

Dataset context:
{context}
"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                answer = response.text
            except Exception as e:
                answer = (
                    "Gemini could not be called. Check your Streamlit secret "
                    "`GEMINI_API_KEY`. Error: " + str(e)
                )
        else:
            answer = (
                "For broader AI questions, add `GEMINI_API_KEY` under "
                "Streamlit Cloud → Settings → Secrets. Basic dashboard questions "
                "still work without an API key."
            )

    st.markdown("### Answer")
    st.write(answer)

st.caption("Built with Streamlit • Pandas • Plotly • Optional Gemini")
