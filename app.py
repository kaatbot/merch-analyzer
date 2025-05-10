
import pandas as pd
import streamlit as st
import datetime as dt
from collections import Counter
import re

st.title("🧠 Merch Analyzer Dashboard (MVP)")

uploaded_file = st.file_uploader("Upload your Amazon Merch CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded!")

    with st.expander("📄 Raw Data Preview"):
        st.dataframe(df.head())

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    st.sidebar.header("🔍 Filter Options")
    keyword = st.sidebar.text_input("Filter by Keyword")
    min_bsr = st.sidebar.number_input("Min BSR", value=0)
    max_bsr = st.sidebar.number_input("Max BSR", value=1_000_000)
    min_price = st.sidebar.number_input("Min Price", value=0.0)
    max_price = st.sidebar.number_input("Max Price", value=100.0)

    filtered_df = df.copy()
    if keyword:
        filtered_df = filtered_df[filtered_df['Title'].str.contains(keyword, case=False, na=False)]
    if 'BSR' in df.columns:
        filtered_df = filtered_df[(df['BSR'] >= min_bsr) & (df['BSR'] <= max_bsr)]
    if 'Price' in df.columns:
        filtered_df = filtered_df[(df['Price'] >= min_price) & (df['Price'] <= max_price)]

    st.subheader("📊 Filtered Results")
    st.dataframe(filtered_df)

    if 'BSR' in filtered_df.columns:
        st.subheader("📈 BSR Distribution")
        st.bar_chart(filtered_df['BSR'].value_counts().sort_index())

    if 'Title' in filtered_df.columns:
        st.subheader("🔑 Top Title Words")
        all_words = []
        for title in filtered_df['Title'].dropna():
            words = re.findall(r'\w+', title.lower())
            all_words.extend(words)
        word_freq = Counter(all_words)
        top_words = pd.DataFrame(word_freq.most_common(20), columns=['Word', 'Count'])
        st.bar_chart(top_words.set_index('Word'))
