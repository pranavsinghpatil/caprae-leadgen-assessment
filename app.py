# import streamlit as st

# uploaded = st.file_uploader("Upload raw_leads.csv", type="csv")
# if uploaded:
#     df = pd.read_csv(uploaded)
#     enriched = enrich(df)         # your function
#     scored = score(enriched)      # loads joblib model and predicts
#     st.dataframe(scored)          
#     ... 


# min_score = st.slider("Min Score", 0.0, 1.0, 0.75)
# st.download_button("Download Tier1 Leads", scored[scored.score>=min_score].to_csv(index=False), file_name="tier1.csv")


# st.bar_chart(scored['tier'].value_counts())
# st.pyplot(fig_hist)  # histogram of scores
# -----------------------
import streamlit as st, pandas as pd, joblib
from enrich import enrich
model = joblib.load('model.joblib')

def score(df):
    df['score'] = model.predict_proba(df[['company_age','emp_bracket','seniority']])[:,1]
    df['tier'] = pd.cut(df.score, bins=[0,0.6,0.8,1.0], labels=['Tier3','Tier2','Tier1'])
    return df

st.title("Predictive Lead Scoring")
uploaded = st.file_uploader("Upload raw_leads.csv", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
    enriched = enrich(df)
    scored = score(enriched)
    st.write("### Scored Leads", scored)
    min_score = st.slider("Min Score", 0.0, 1.0, 0.8)
    tier1 = scored[scored.score >= min_score]
    st.download_button("Download Tier1 Leads", tier1.to_csv(index=False), file_name="tier1.csv")
    st.bar_chart(scored['tier'].value_counts())
