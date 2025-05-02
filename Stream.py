import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from streamlit_extras.card import card
import base64
import plotly.express as px


@st.cache_data
def load_data(path):
    try:
        df = pd.read_excel(path)
        return df
    except FileNotFoundError:
        st.error(f"File '{path}' not found.")
        return pd.DataFrame()


def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    background_style = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
    """
    st.markdown(background_style, unsafe_allow_html=True)


def apply_custom_style():
    st.markdown("""
        <style>
    
        .element-container:has(.stPlotlyChart), .element-container:has(.stImage), .element-container:has(.stPyplot) {
            background: transparent !important;
            padding: 0 !important;
            box-shadow: none !important;
        }

        
        .yellow-box {
            background-color: #fff8cc;
            padding: 10px 15px;
            border-radius: 12px;
            margin-bottom: 10px;
            font-weight: bold;
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
            display: inline-block;
        }

        .metric-container {
            background-color: #fff8cc;
            padding: 8px;
            border-radius: 10px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

#Visualization Functions

def plot_top_companies(df):
    top_companies = df['company'].value_counts().head(10)
    fig, ax = plt.subplots()
    top_companies.plot(kind='barh', ax=ax, color='skyblue')
    ax.set_title("Top 10 Hiring Companies")
    ax.invert_yaxis()
    st.pyplot(fig)

def plot_top_job_titles(df):
    top_titles = df['job_title'].value_counts().head(10)
    fig, ax = plt.subplots()
    top_titles.plot(kind='bar', ax=ax, color='orange')
    ax.set_title("Top 10 Job Titles")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def plot_wordcloud_skills(df):
    if 'skills' not in df.columns:
        st.warning("'skills' column not found.")
        return
    all_skills = df['skills'].explode().dropna().tolist()
    skills_text = ' '.join(all_skills)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(skills_text)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

def plot_jobs_by_city(df):
    if 'city' not in df.columns:
        st.warning("'city' column not found in data.")
        return
    top_cities = df['city'].value_counts().head(10).sort_values()
    city_df = pd.DataFrame({'city': top_cities.index, 'count': top_cities.values})
    fig, ax = plt.subplots()
    sns.barplot(data=city_df, y='city', x='count', hue='city', palette='viridis', ax=ax, legend=False)
    ax.set_title("Top Job Locations")
    st.pyplot(fig)
    
def plot_choropleth_country_jobs(df):
    country_job_counts = df.groupby('country')['job_title'].count().reset_index()
    fig = px.choropleth(country_job_counts,
                        locations="country",
                        locationmode="country names",
                        color="job_title",
                        hover_name="country",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        labels={"job_title": "Number of Job Titles"},
                        title="Job Title Distribution by Country")
    fig.update_geos(showcoastlines=True, coastlinecolor="Black", projection_type="mercator")
    fig.update_layout(geo=dict(showframe=False, showcoastlines=True))
    st.plotly_chart(fig, use_container_width=True)

def plot_stacked_job_types(df):
    if 'job_title' not in df.columns or 'job_type' not in df.columns:
        st.warning("Columns 'job_title' or 'job_type' not found.")
        return
    
    # Count of job types per job title
    grouped = df.groupby(['job_title', 'job_type']).size().unstack(fill_value=0)
    
    
    top_jobs = df['job_title'].value_counts().head(30).index
    grouped = grouped.loc[grouped.index.isin(top_jobs)]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    grouped.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title("Job Types by Job Title")
    ax.set_xlabel("Job Title")
    ax.set_ylabel("Number of Jobs")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)


def plot_job_type_distribution(df):
    if 'job_type' not in df.columns:
        st.warning("'job_type' column not found.")
        return
    job_type_counts = df['job_type'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    job_type_counts.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title("Chances of Finding Each Job Type")
    ax.set_xlabel("Job Type")
    ax.set_ylabel("Count of Jobs")
    plt.xticks(rotation=45)
    st.pyplot(fig)


def plot_company_heatmap(df):
    job_counts = df['company'].value_counts().head(20).to_frame(name='Job Count')
    fig, ax = plt.subplots(figsize=(6, 10))
    sns.heatmap(job_counts, annot=True, fmt="d", cmap="YlGnBu", cbar=True, ax=ax)
    ax.set_title("Top 20 Companies by Number of Job Listings")
    ax.set_xlabel("Job Count")
    ax.set_ylabel("Company")
    st.pyplot(fig)

def plot_experience_distribution(df):
    df["experience"] = df["experience"].replace("N/A", "Not Mentioned")
    experience_counts = df["experience"].value_counts().nlargest(10).sort_values()
    fig, ax = plt.subplots(figsize=(8, 6))
    experience_counts.plot(kind='barh', ax=ax, color='skyblue', edgecolor='black', width=0.75)
    for i, (index, value) in enumerate(experience_counts.items()):
        ax.text(value + max(experience_counts)*0.01, i, f'{value:,}', va='center', ha='left', fontsize=10)
    ax.set_title("Top 10 Experience Distribution", fontsize=14, pad=15)
    ax.set_xlabel("Count", fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xlim([0, max(experience_counts) * 1.15])
    st.pyplot(fig)

def plot_top_skills(df):
    if 'skills' not in df.columns:
        st.warning("'skills' column not found.")
        return
    all_skills = df['skills'].explode().dropna()
    top_skills = all_skills.value_counts().head(10)
    skills_df = pd.DataFrame(top_skills).reset_index()
    skills_df.columns = ['Skill', 'Count']
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(skills_df['Skill'][::-1], skills_df['Count'][::-1], color='m')
    ax.set_title("Top 10 Skills")
    ax.set_xlabel("Number of Job Listings")
    st.pyplot(fig)

  

#Main App
def main():
    st.set_page_config(layout="wide", page_title="Wuzzuf Dashboard", page_icon="📊", initial_sidebar_state="collapsed")
    
    set_background("background.jpg")
    apply_custom_style()

    st.markdown("<div class='yellow-box'>📊 Wuzzuf Job Listings Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='yellow-box'>Explore Wuzzuf job listings through visual insights and search filters.</div>", unsafe_allow_html=True)

    df = load_data("final2.xlsx")
    if df.empty:
        st.stop()

    #Search
    st.markdown("<div class='yellow-box'>🔍 Search Jobs</div>", unsafe_allow_html=True)
    col_icon, col_input = st.columns([1, 9])
    with col_icon:
        st.markdown("<h3 style='margin-top: 8px;'>🔎</h3>", unsafe_allow_html=True)
    with col_input:
        search_query = st.text_input(
            label="Search bar (hidden for visual users)",
            placeholder="Type a keyword (e.g., job title, company, or city)...",
            label_visibility="collapsed"
        )

    if search_query:
        filtered_df = df[
            df['job_title'].str.contains(search_query, case=False, na=False) |
            df['company'].str.contains(search_query, case=False, na=False) |
            df['city'].str.contains(search_query, case=False, na=False)
        ]
        st.success(f"Found {len(filtered_df)} results for: **{search_query}**")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        filtered_df = df
        
    
    st.markdown("<div class='yellow-box'>🧮 Filter by Columns</div>", unsafe_allow_html=True)
    filter_cols = st.multiselect("Select columns to filter by:", options=[col for col in df.columns if df[col].nunique() < 50])

    for col in filter_cols:
        unique_vals = df[col].dropna().unique()
        selected_vals = st.multiselect(f"Filter '{col}' by:", options=sorted(unique_vals))
        if selected_vals:
            filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]



    
    st.markdown("<div class='yellow-box'>📈 Dataset Overview</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-container'>Total Jobs<br><strong>{len(filtered_df)}</strong></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-container'>Companies<br><strong>{filtered_df['company'].nunique()}</strong></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-container'>Job Titles<br><strong>{filtered_df['job_title'].nunique()}</strong></div>", unsafe_allow_html=True)

    
    st.markdown("<div class='yellow-box'>📊 Explore Visual Insights</div>", unsafe_allow_html=True)
    card_cols = st.columns(2)
    with card_cols[0]:
        if card(title="Top Hiring Companies", text="See top companies hiring", image="", url="#TopHiring"):
            st.markdown("<div class='yellow-box' id='TopHiring'>Top Hiring Companies</div>", unsafe_allow_html=True)
            plot_top_companies(filtered_df)
    with card_cols[1]:
        if card(title="Top Job Titles", text="Explore most common job titles", image="", url="#TopTitles"):
            st.markdown("<div class='yellow-box' id='TopTitles'>Top Job Titles</div>", unsafe_allow_html=True)
            plot_top_job_titles(filtered_df)

    card_cols2 = st.columns(2)
    with card_cols2[0]:
        if card(title="Top Job Locations", text="Check popular job cities", image="", url="#TopCities"):
            st.markdown("<div class='yellow-box' id='TopCities'>Top Job Locations</div>", unsafe_allow_html=True)
            plot_jobs_by_city(filtered_df)
    with card_cols2[1]:
        if card(title="Common Skills", text="View most required skills", image="", url="#Skills"):
            st.markdown("<div class='yellow-box' id='Skills'>Most Common Skills</div>", unsafe_allow_html=True)
            plot_wordcloud_skills(filtered_df)
    card_cols3 = st.columns(2)
    with card_cols3[0]:
       if card(title="Jobs by Country", text="See distribution of job titles by country", image="", url="#Choropleth"):
        st.markdown("<div class='yellow-box' id='Choropleth'>Job Title Distribution by Country</div>", unsafe_allow_html=True)
        plot_choropleth_country_jobs(filtered_df)

    with card_cols3[1]:
       if card(title="Job Types per Title", text="Explore how job types vary per job title", image="", url="#StackedJobs"):
        st.markdown("<div class='yellow-box' id='StackedJobs'>Job Types by Job Title</div>", unsafe_allow_html=True)
        plot_stacked_job_types(filtered_df)

    card_cols4 = st.columns(2)
    with card_cols4[0]:
       if card(title="Job Type Distribution", text="Understand distribution across job types", image="", url="#TypeDistribution"):
        st.markdown("<div class='yellow-box' id='TypeDistribution'>Chances of Finding Each Job Type</div>", unsafe_allow_html=True)
        plot_job_type_distribution(filtered_df)

    with card_cols4[1]:
       if card(title="Hiring Heatmap", text="Top 20 companies by job listings", image="", url="#HeatmapCompanies"):
        st.markdown("<div class='yellow-box' id='HeatmapCompanies'>Top 20 Companies Heatmap</div>", unsafe_allow_html=True)
        plot_company_heatmap(filtered_df)

    card_cols5 = st.columns(2)
    with card_cols5[0]:
      if card(title="Experience Levels", text="See the most requested experience levels", image="", url="#Experience"):
        st.markdown("<div class='yellow-box' id='Experience'>Top Experience Levels</div>", unsafe_allow_html=True)
        plot_experience_distribution(filtered_df)

    with card_cols5[1]:
     if card(title="Top Skills", text="Explore most in-demand skills", image="", url="#TopSkills"):
        st.markdown("<div class='yellow-box' id='TopSkills'>Top 10 Skills</div>", unsafe_allow_html=True)
        plot_top_skills(filtered_df)

if __name__ == "__main__":
    main()

