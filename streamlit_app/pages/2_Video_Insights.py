import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from wordcloud import WordCloud
from utils import dataloader
from styles import load_css, apply_plotly_theme

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Video Insights",
    layout="wide",
    page_icon="🎬"
)

load_css()
apply_plotly_theme()

# ----------------------------------------------------------------------------
# LOAD TODAY'S TRENDING DATA
# ----------------------------------------------------------------------------
with st.spinner("Loading today's trending videos..."):
    if 'latest_df' not in st.session_state:
        latest_df = dataloader.get_latest_data()
        st.session_state['latest_df'] = latest_df
    else:
        latest_df = st.session_state['latest_df']

country_names = latest_df['country_name'].unique().tolist()

# ----------------------------------------------------------------------------
# PAGE HEADER
# ----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🎬 Video Insights</h1>
    <p>Deep Dive into Any Trending Video</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# COUNTRY SELECTION
# ----------------------------------------------------------------------------
country = st.selectbox(
    "Select Country",
    options=country_names,
    index=33
)

filtered_df = latest_df[latest_df['country_name'] == country]

# ----------------------------------------------------------------------------
# VIDEO SELECTION
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>🎥 Select a Video</h3></div>', unsafe_allow_html=True)

video_titles = filtered_df["title"].fillna("Untitled Video").tolist()
selected_title = st.selectbox("Choose a video", video_titles, index=0)

video = filtered_df[filtered_df["title"] == selected_title].iloc[0]
trending_countries = ", ".join(latest_df[latest_df["title"] == selected_title]["country_name"].tolist())

# ----------------------------------------------------------------------------
# VIDEO OVERVIEW SECTION
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>📌 Video Overview</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 2.5])

with col1:
    st.image(video["thumbnail"], use_container_width=True)
    st.markdown(f"""
        <div class="highlight-box" style="margin-top: 1rem;">
            <div class="highlight-title">📺 Category</div>
            <h3>{video['category_name']}</h3>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <h2 style='margin-bottom:0.5rem;'>{video['title']}</h2>
        <p style='font-size:1.1rem; opacity:0.8;'>Channel: <b>{video['channel_title']}</b></p>
        <p>Published: <b>{video['published_at']}</b></p>
        <p>Country: <b>{video['country_name']}</b></p>
        <p>Trending In: <b>{trending_countries}</b></p>
        <p>Duration: <b>{video['duration']} seconds</b></p>
        <p>Tags Count: <b>{video['tag_count']}</b></p>
        <a href="https://www.youtube.com/watch?v={video['video_id']}" target="_blank">
            <button class="watch-button">▶️ Watch on YouTube</button>
        </a>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# PERFORMANCE METRICS
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>📊 Performance Metrics</h3></div>', unsafe_allow_html=True)

cols = st.columns(4)

metric_map = [
    ("👁️ Views", f"{video['views']:,}"),
    ("👍 Likes", f"{video['likes']:,}"),
    ("💬 Comments", f"{video['comments']:,}"),
    ("🔥 Engagement Score", f"{round(video['engagement_score']*100, 2)}%"),
]

for col, (label, val) in zip(cols, metric_map):
    col.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="margin-top:0.3rem;">{val}</div>
        </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# RATIO VISUALIZATIONS
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>📈 Engagement Breakdown</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    like_ratio = video["likes"] / max(video["views"], 1)
    comment_ratio = video["comments"] / max(video["views"], 1)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(like_ratio * 100, 2),
        title={'text': "Like Ratio (%)"},
        gauge={'axis': {'range': [0, 10]}}
    ))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(comment_ratio * 100, 2),
        title={'text': "Comment Ratio (%)"},
        gauge={'axis': {'range': [0, 1]}}
    ))
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# TAG ANALYSIS
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>🏷️ Tag Analysis</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 2.5])

with col1:
    st.markdown("### Tags Used")
    raw_tags = video["tags"]

    if isinstance(raw_tags, str):
        tag_list = raw_tags.split("|")
        for tag in tag_list[:20]:
            st.markdown(f"- {tag}")

with col2:
    st.markdown("### Tag Cloud")
    if isinstance(raw_tags, str):
        wc = WordCloud(
            width=1000, height=400,
            background_color="black",
            colormap="Reds",
            margin=2
        ).generate(" ".join(tag_list))
        st.image(wc.to_image(), use_container_width=True)

# ----------------------------------------------------------------------------
# METADATA SECTION
# ----------------------------------------------------------------------------
st.markdown('<div class="section-header"><h3>🧩 Metadata Insights</h3></div>', unsafe_allow_html=True)

cols = st.columns(3)

meta_items = [
    ("Default Language", video["default_language"]),
    ("Audio Language", video["audio_language"]),
    ("Definition", video["definition"]),
]

for col, (label, value) in zip(cols, meta_items):
    col.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="font-size:1.3rem; margin-top:0.5rem;">{value}</div>
        </div>
    """, unsafe_allow_html=True)
