import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns

# ----------------- Load Data -----------------
@st.cache_data
def load_data(path):
    try:
        df = pd.read_excel(path)
        return df
    except FileNotFoundError:
        st.error(f" File '{path}' not found.")
        return pd.DataFrame()

# ----------------- Visualization Functions -----------------
def plot_top_companies(df):
    top_companies = df['company'].value_counts().head(10)
    fig, ax = plt.subplots()
    top_companies.plot(kind='barh', ax=ax, color='skyblue')
    ax.set_title("Top 10 Hiring Companies")
    ax.invert_yaxis()
    st.pyplot(fig)

def plot_top_job_titles(df):
    top_titles = df['title'].value_counts().head(10)
    fig, ax = plt.subplots()
    top_titles.plot(kind='bar', ax=ax, color='orange')
    ax.set_title("Top 10 Job Titles")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def plot_wordcloud_skills(df):
    if 'skills_list' not in df.columns:
        st.warning(" 'skills_list' column not found.")
        return
    all_skills = df['skills_list'].explode().dropna().tolist()
    skills_text = ' '.join(all_skills)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(skills_text)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

def plot_jobs_by_location(df):
    if 'location' not in df.columns:
        st.warning(" 'location' column not found in data.")
        return
    top_locations = df['location'].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_locations.values, y=top_locations.index, ax=ax, palette='viridis')
    ax.set_title("Top Job Locations")
    st.pyplot(fig)

# ----------------- Main App -----------------
def main():
    st.set_page_config(layout="wide")
    st.title("Wuzzuf Job Listings Analysis")
    st.markdown("This dashboard visualizes job postings scraped from Wuzzuf and analyzed.")

    df = load_data("final2.xlsx")

    if df.empty:
        st.stop()

    # Metrics
    st.subheader(" Dataset Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Jobs", len(df))
    col2.metric("Companies", df['company'].nunique())
    col3.metric("Job Titles", df['title'].nunique())

    # Plots
    st.subheader(" Top Hiring Companies")
    plot_top_companies(df)

    st.subheader(" Top Job Titles")
    plot_top_job_titles(df)

    st.subheader(" Top Job Locations")
    plot_jobs_by_location(df)

    st.subheader(" Most Common Skills")
    plot_wordcloud_skills(df)

if __name__ == "__main__":
    main()
