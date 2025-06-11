
import streamlit as st, pandas as pd, joblib
from enrich import enrich
model = joblib.load('model.joblib')

def score(df):
    df['score'] = model.predict_proba(df[['company_age','emp_bracket','seniority']])[:,1]
    df['tier'] = pd.cut(df.score, bins=[0,0.6,0.8,1.0], labels=['Tier3','Tier2','Tier1'])
    return df

st.set_page_config(page_title="Predictive Lead Scoring", layout="wide")
st.title("🔮 Predictive Lead Scoring")
st.markdown("""
Welcome! This tool lets you upload a raw leads CSV, enriches it with company and contact intelligence, and scores your leads for sales prioritization.

**How to use:**
1. Click below to upload your `raw_leads.csv` file (must have columns: website, emp_count, title).
2. Wait for enrichment and scoring (may take a minute for large files).
3. Explore the results, filter by score, and download your best leads.
""")

uploaded = st.sidebar.file_uploader("📤 Upload raw_leads.csv", type="csv")

if uploaded:
    try:
        df = pd.read_csv(uploaded)
        st.write("#### Preview of Uploaded Data", df.head())
        progress_bar = st.progress(0)
        status_text = st.empty()
        import time
        start_time = time.time()
        def progress_callback(percent, message):
            progress_bar.progress(percent)
            elapsed = int(time.time() - start_time)
            status_text.info(f"{message} | {percent}% done | Elapsed: {elapsed}s")
        enriched = enrich(df, progress_callback=progress_callback)
        progress_bar.progress(100)
        status_text.success(f"Enrichment complete! Processed {len(enriched)} leads in {int(time.time()-start_time)}s.")
        st.success(f"Enriched {len(enriched)} leads!")
        scored = score(enriched)
        st.write("#### Scored Leads Table", scored.head(20))
        st.markdown(f"**Total leads:** {len(scored)} | **Tier1:** {sum(scored['tier']=='Tier1')} | **Tier2:** {sum(scored['tier']=='Tier2')} | **Tier3:** {sum(scored['tier']=='Tier3')}")
        min_score = st.slider("🔎 Min Score to Filter Tier1", 0.0, 1.0, 0.8, step=0.01)
        tier1 = scored[scored.score >= min_score]
        st.write(f"### Tier1 Leads (score ≥ {min_score})", tier1)
        st.download_button("⬇️ Download Tier1 Leads", tier1.to_csv(index=False), file_name="tier1.csv")
        st.write("#### Tier Distribution")
        st.bar_chart(scored['tier'].value_counts())
        st.sidebar.write(f"Tier1 leads: {scored['tier'].value_counts().get('Tier1', 0)}")
        st.sidebar.write(f"Tier2 leads: {scored['tier'].value_counts().get('Tier2', 0)}")
        st.sidebar.write(f"Tier3 leads: {scored['tier'].value_counts().get('Tier3', 0)}")

        st.write("#### Score Distribution")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.hist(scored['score'], bins=10, color='#4F8DFD', edgecolor='black')
        ax.set_title('Score Distribution')
        ax.set_xlabel('Score')
        ax.set_ylabel('Lead Count')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("Please upload a CSV file to begin.")
