
import pandas as pd
import streamlit as st
from collections import Counter
import re

st.set_page_config(page_title='Merch Analyzer', layout='wide')
st.title("🧠 Merch Analyzer Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon Merch CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    st.sidebar.header("🔍 Filter Options")
    keyword = st.sidebar.text_input("Keyword Filter")
    min_bsr = st.sidebar.number_input("Min BSR", value=0)
    max_bsr = st.sidebar.number_input("Max BSR", value=1_000_000)
    min_price = st.sidebar.number_input("Min Price", value=0.0)
    max_price = st.sidebar.number_input("Max Price", value=100.0)

    filtered_df = df.copy()
    if keyword:
        filtered_df = filtered_df[filtered_df['Title'].str.contains(keyword, case=False, na=False)]
    if 'BSR' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['BSR'] >= min_bsr) & (filtered_df['BSR'] <= max_bsr)]
    if 'Price' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['Price'] >= min_price) & (filtered_df['Price'] <= max_price)]

    st.subheader("📊 Filtered Product Listings (Sortable Table)")
    if 'ASIN' in filtered_df.columns:
        def get_image_url(asin):
            return f"https://m.media-amazon.com/images/I/{asin}.jpg"
        filtered_df['Image'] = filtered_df['ASIN'].apply(lambda x: f'<img src="{get_image_url(x)}" width="80">' if pd.notnull(x) else "")
        st.write("✅ Showing image previews from ASINs")
    else:
        filtered_df['Image'] = ""

    # Show HTML table with image previews
    st.write(
        filtered_df.to_html(escape=False, columns=['Image', 'Title', 'Brand', 'Price', 'BSR', 'Date'], index=False),
        unsafe_allow_html=True
    )

    if 'Title' in filtered_df.columns:
        st.subheader("🔑 Top Title Words")
        all_words = []
        for title in filtered_df['Title'].dropna():
            words = re.findall(r'\w+', title.lower())
            all_words.extend(words)
        word_freq = Counter(all_words)
        top_words = pd.DataFrame(word_freq.most_common(20), columns=['Word', 'Count'])
        st.bar_chart(top_words.set_index('Word'))

    if 'Brand' in filtered_df.columns:
        st.subheader("🏷️ Seller (Brand) Summary")
        seller_summary = filtered_df.groupby('Brand').agg(
            Count=('Title', 'count'),
            Avg_BSR=('BSR', 'mean'),
            Avg_Price=('Price', 'mean')
        ).sort_values('Count', ascending=False).reset_index()
        st.dataframe(seller_summary)
