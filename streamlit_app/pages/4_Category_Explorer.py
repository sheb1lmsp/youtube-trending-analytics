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
    page_title="Category Explorer",
    layout="wide",
    page_icon="📚"
)

load_css()
apply_plotly_theme()

# ----------------------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------------------
with st.spinner("Loading today's trending videos..."):
    latest_df = dataloader.get_latest_data()
    
# ----------------------------------------------------------------------------
# PAGE HEADER
# ----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>📚 Category Explorer</h1>
    <p>Explore How Each Category Performed Today Across All Countries</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# CATEGORY SELECTION
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>🎬 Select Category</h3></div>', unsafe_allow_html=True)

all_categories = sorted(latest_df["category_name"].dropna().unique())

selected_category = st.selectbox(
    "Choose a category to analyze",
    all_categories,
    index=all_categories.index("Entertainment")
)

cat_df = latest_df[latest_df["category_name"] == selected_category]
unique_df = cat_df[~cat_df['video_id'].duplicated()]

# ----------------------------------------------------------------------------
# CATEGORY SUMMARY
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>📊 Category Summary</h3></div>', unsafe_allow_html=True)

cols = st.columns(4)

summary_map = [
    ("🎬", "Total Videos", f"{len(unique_df):,}"),
    ("👁️", "Total Views", f"{unique_df['views'].sum():,}"),
    ("🔥", "Average Engagement", f"{100 * unique_df['engagement_score'].mean():.2f}%"),
    ("⏱️", "Average Duration", f"{unique_df['duration'].mean():.0f}"),
]

for col, (icon, label, value) in zip(cols, summary_map):
    col.markdown(f"""
        <div class="metric-container">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="margin-top:0.3rem;">{value}</div>
        </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# TOP VIDEOS IN CATEGORY
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>🏆 Top Videos in This Category</h3></div>', unsafe_allow_html=True)

top_metric = st.radio(
    "",
    ["Top Views", "Top Likes", "Top Comments", "Top Engagement"],
    horizontal=True,
    label_visibility="collapsed"
)

metric_map = {
    "Top Views": "views",
    "Top Likes": "likes",
    "Top Comments": "comments",
    "Top Engagement": "engagement_score",
}

metric_col = metric_map[top_metric]

top_vids = unique_df.sort_values(metric_col, ascending=False)[
    ["title", "channel_title", "views", "likes", "comments", "engagement_score", "video_id"]
].head(10)

top_vids["Video URL"] = top_vids['video_id'].apply(lambda x : f"https://www.youtube.com/watch?v={x}")
top_vids.columns = ['Title', 'Channel', 'Views', 'Likes', 'Comments', 'Engagement Score', 'Video ID', 'Video URL']

st.dataframe(top_vids.drop('Video ID', axis=1).set_index(pd.Series(range(1,11))), use_container_width=True, height=400)

# ----------------------------------------------------------------------------
# CATEGORY PERFORMANCE ACROSS COUNTRIES
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>🌍 Performance Across Countries</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Average Views per Country")
    fig = px.bar(
        cat_df.groupby("country_name")["views"].mean().reset_index(),
        x="country_name",
        y="views",
        labels={"country_name" : "Country", "views" : "Views"}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Average Engagement per Country")
    fig = px.bar(
        cat_df.groupby("country_name")["engagement_score"].mean().reset_index(),
        x="country_name",
        y="engagement_score",
        labels={"country_name" : "Country", "engagement_score" : "Engagement Score"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# DISTRIBUTIONS WITHIN CATEGORY
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>📦 Category Internal Distributions</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Views Distribution")
    fig = px.histogram(unique_df, x="views", nbins=30)
    fig.update_layout(xaxis_title = "Views", yaxis_title = "Count")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Duration Distribution")
    fig = px.histogram(unique_df, x="duration", nbins=30)
    fig.update_layout(xaxis_title = "Duration", yaxis_title = "Count")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# CREATOR ANALYSIS FOR THIS CATEGORY
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>⭐ Top Creators in This Category</h3></div>', unsafe_allow_html=True)

creator_stats = (
    unique_df.groupby("channel_title")
    .agg(
        video_count=("video_id", "count"),
        avg_views=("views", "mean"),
        avg_engagement=("engagement_score", "mean"),
    )
    .reset_index()
)

top_creators = creator_stats.sort_values("video_count", ascending=False).head(10)

fig = px.bar(
    top_creators.sort_values("video_count", ascending=True),
    y="channel_title",
    x="video_count",
    orientation="h",
    title="Most Active Creators in This Category",
    labels={"video_count" : "Number of Videos", "channel_title" : "Channel"}
)
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# TAG CLOUD FOR THIS CATEGORY
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>🏷️ Tag Cloud for This Category</h3></div>', unsafe_allow_html=True)

all_tags = " ".join(unique_df["tags"].fillna("").astype(str).tolist())

if all_tags.strip():
    from wordcloud import WordCloud

    wc = WordCloud(
        width=1200, height=500,
        background_color="black",
        colormap="Reds",
        margin=2
    ).generate(all_tags)

    st.image(wc.to_image(), use_container_width=True)
else:
    st.info("No tags available for this category.")
