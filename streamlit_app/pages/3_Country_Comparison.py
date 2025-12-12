import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils import dataloader
from styles import load_css, apply_plotly_theme

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Country Comparison",
    layout="wide",
    page_icon="🌍"
)

load_css()
apply_plotly_theme()

# ----------------------------------------------------------------------------
# LOAD TODAY'S DATA
# ----------------------------------------------------------------------------
with st.spinner("Loading today's trending videos..."):
    latest_df = dataloader.get_latest_data()

country_names = sorted(latest_df["country_name"].unique())

# ----------------------------------------------------------------------------
# PAGE HEADER
# ----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🌍 Country Comparison</h1>
    <p>Compare Trending Trends Across Countries for Today</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# COUNTRY SELECTION
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>🔎 Select Countries</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    countries = st.multiselect(
        "Choose one or more countries to compare",
        country_names,
        default=['India', 'United States', 'Australia']
    )

with col2:
    metric_to_compare = st.selectbox(
        "Choose comparison metric",
        [
            "views", "likes", "comments",
            "engagement_score", "duration", "tag_count"
        ],
        format_func = lambda x : {
            "views" : "Total Views",
            "likes" : "Total Likes",
            "comments" : "Total Comments",
            "engagement_score" : "Average Engagement Score",
            "duration" : "Average Duration",
            "tag_count" : "Total Tags"
        }[x]
    )

if not countries:
    st.warning("Please select at least one country.")
    st.stop()

filtered = latest_df[latest_df["country_name"].isin(countries)]

# ----------------------------------------------------------------------------
# AGGREGATED METRICS
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>📊 Summary Metrics by Country</h3></div>', unsafe_allow_html=True)

agg = filtered.groupby("country_name").agg(
    total_videos=("video_id", "count"),
    views=("views", "sum"),
    likes=("likes", "sum"),
    comments=("comments", "sum"),
    engagement_score=("engagement_score", "mean"),
    duration=("duration", "mean"),
    tag_count=("tag_count", "sum"),
).reset_index()

agg = agg.sort_values(metric_to_compare, ascending=False)
agg.columns = ['Country', 'Total Videos', 'Total Views', 'Total Likes', 'Total Comments', 'Average Engagement', 'Average Duration', 'Total Tags']

# Show the table
st.dataframe(
    agg.set_index(pd.Series(range(1, len(countries) + 1))), 
    use_container_width=True, 
    height=420
)

# ----------------------------------------------------------------------------
# COUNTRY COMPARISON VISUALIZATIONS
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>📈 Metric Comparison</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### Average {metric_to_compare.capitalize()}")

    fig = px.bar(
        filtered.groupby("country_name")[metric_to_compare].mean().reset_index(),
        x="country_name",
        y=metric_to_compare,
        labels={"country_name" : "Country", metric_to_compare : metric_to_compare.title()},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown(f"### Total {metric_to_compare.capitalize()}")

    fig = px.bar(
        filtered.groupby("country_name")[metric_to_compare].sum().reset_index(),
        x="country_name",
        y=metric_to_compare,
        labels={"country_name" : "Country", metric_to_compare : metric_to_compare.title()},
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# CATEGORY DISTRIBUTION PER COUNTRY
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>🎬 Category Distribution Across Countries</h3></div>', unsafe_allow_html=True)

fig = px.histogram(
    filtered,
    x="category_name",
    color="country_name",
    barmode="group",
)

fig.update_layout(xaxis_title="Category", yaxis_title="Count")
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# TOP VIDEO PER COUNTRY
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>🏆 Top Video Per Country</h3></div>', unsafe_allow_html=True)

cols = st.columns(len(countries))

for col, country in zip(cols, countries):
    top_vid = (
        latest_df[latest_df["country_name"] == country]
        .sort_values("views", ascending=False)
        .iloc[0]
    )

    with col:
        st.markdown(f"""
        <div class="highlight-box" style="padding:1.2rem; margin-bottom:1rem;">
            <div class="highlight-title"><strong>{country}</strong></div>
            <h3 style="font-size:1rem;">{top_vid['title']}</h3>
            <p><strong>Channel:</strong> {top_vid['channel_title']}</p>
            <p style="margin-top:0.5rem;"><strong>Views:</strong> {top_vid['views']:,}</p>
            <a href="https://www.youtube.com/watch?v={top_vid['video_id']}" target="_blank">
                <button class="watch-button" style="margin-top:0.4rem;">▶️ Watch</button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# CATEGORY PERFORMANCE BREAKDOWN
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>📚 Category Performance Comparison</h3></div>', unsafe_allow_html=True)

fig = px.box(
    filtered,
    x="category_name",
    y="views",
    color="country_name",
    labels={"category_name" : "Category", "views" : "Views"}
)

st.plotly_chart(fig, use_container_width=True)
