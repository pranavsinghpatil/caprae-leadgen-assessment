import streamlit as st
import pandas as pd

st.title("LeadGen Enhancement Demo")

uploaded = st.file_uploader("Upload raw_leads.csv", type="csv")
if uploaded:
    df = pd.read_csv(uploaded)
    st.write("### Raw Data", df)
    # TODO: add deduplication / validation here
    df.drop_duplicates(["email"])
