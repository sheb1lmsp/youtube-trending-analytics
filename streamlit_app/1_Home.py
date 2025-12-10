import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime
import json
from wordcloud import WordCloud

from utils import metrics, doughnut_data, dataloader, top_videos
from styles import load_css, apply_plotly_theme

# ----------------------------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="YouTube Trending Today",
    layout="wide",
    page_icon="🔥",
    initial_sidebar_state="expanded"
)

load_css()
apply_plotly_theme()

with open('country_names.json', 'r') as f:
    country_names = json.load(f)

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.markdown("""
    <div class="main-header">
        <h1>🔥 YouTube Trending Analytics Dashboard</h1>
        <p>Real-time Global Insights • Updated Daily</p>
    </div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
with st.spinner("🌍 Fetching today's trending videos..."):
    if 'latest_df' not in st.session_state:
        latest_df = dataloader.get_latest_data()
        st.session_state['latest_df'] = latest_df
    else:
        latest_df = st.session_state['latest_df']

# ----------------------------------------------------------------------------
# COUNTRY SELECTION
# ----------------------------------------------------------------------------
country = st.selectbox(
    "Select Country",
    options=country_names.values(),
    index=33
)

filtered_df = latest_df[latest_df['country_name'] == country]

# ----------------------------------------------------------------------------
# MAIN TABS
# ----------------------------------------------------------------------------
main_tabs = st.tabs([
    "🏠 Overview",
    "📈 Category & Language Analytics",
    "🎬 Top Trending Videos",
    "📊 Viewer Behavior Analysis",
    "📊 Content Attributes & Correlations",
    "📊 Duration & Tag Influence Analysis"
])

# =============================================================================
# TAB 1 — OVERVIEW
# =============================================================================
with main_tabs[0]:

    st.markdown('<div class="section-header"><h3>📊 Daily Performance Summary</h3></div>', unsafe_allow_html=True)
    metrics_data = metrics.get_daily_metrics(filtered_df)

    cols = st.columns(6)
    metrics_config = [
        ("🎬", "Total Videos", f"{metrics_data['total_videos']:,}"),
        ("👁️", "Total Views", f"{metrics_data['total_views']:,}"),
        ("👍", "Total Likes", f"{metrics_data['total_likes']:,}"),
        ("💬", "Total Comments", f"{metrics_data['total_comments']:,}"),
        ("⏱️", "Avg Duration", f"{metrics_data['average_duration']}s"),
        ("🔥", "Engagement Score", f"{100 * metrics_data['average_engagement_score']}%"),
    ]

    for col, (icon, label, value) in zip(cols, metrics_config):
        col.markdown(f"""
            <div class="metric-container">
                <div class="metric-icon">{icon}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)

    # Highlights Section -------------------------------------------------------
    st.markdown('<div class="section-header"><h3>🏆 Noteworthy Performers</h3></div>', unsafe_allow_html=True)

    tabs = st.tabs([
        "Most Viewed",
        "Most Liked",
        "Most Commented",
        "Highest Engagement",
        "Longest Video",
        "Top Creator"
    ])

    mv = metrics_data

    # Consistent box formatting used for all tabs
    def highlight_box(title, video_title, channel, metric_value, video_id):
        return f"""
            <div class="highlight-box">
                <div class="highlight-title">{title}</div>
                <h3>{video_title}</h3>
                <p><strong>Channel:</strong> {channel}</p>
                <h2>{metric_value}</h2>
                <a href="https://www.youtube.com/watch?v={video_id}" target="_blank">
                    <button class="watch-button">▶️ Watch Now</button>
                </a>
            </div>
        """

    with tabs[0]:
        st.markdown(highlight_box(
            "🏆 Most Viewed Video",
            mv['most_viewed_video_title'],
            mv['most_viewed_video_channel'],
            f"👁️ {mv['most_viewed_video_views']:,} views",
            mv['most_viewed_video_id']
        ), unsafe_allow_html=True)

    with tabs[1]:
        st.markdown(highlight_box(
            "👍 Most Liked Video",
            mv['most_liked_video_title'],
            mv['most_liked_video_channel'],
            f"👍 {mv['most_liked_video_likes']:,} likes",
            mv['most_liked_video_id']
        ), unsafe_allow_html=True)

    with tabs[2]:
        st.markdown(highlight_box(
            "💬 Most Commented Video",
            mv['most_commented_video_title'],
            mv['most_commented_video_channel'],
            f"💬 {mv['most_commented_video_comments']:,} comments",
            mv['most_commented_video_id']
        ), unsafe_allow_html=True)

    with tabs[3]:
        st.markdown(highlight_box(
            "🔥 Highest Engagement",
            mv['most_engaged_video_title'],
            mv['most_engaged_video_channel'],
            f"🔥 {round(mv['most_engaged_video_score'] * 100, 2)}%",
            mv['most_engaged_video_id']
        ), unsafe_allow_html=True)

    with tabs[4]:
        mins = mv['longest_trending_video_duration'] // 60
        secs = mv['longest_trending_video_duration'] % 60
        st.markdown(highlight_box(
            "⏱️ Longest Trending Video",
            mv['longest_trending_video_title'],
            mv['longest_trending_video_channel'],
            f"⏱️ {mins}m {secs}s",
            mv['longest_trending_video_id']
        ), unsafe_allow_html=True)

    with tabs[5]:
        st.markdown(f"""
            <div class="highlight-box">
                <div class="highlight-title">⭐ Top Creator by Trending Count</div>
                <h3>{mv['most_popular_creator_channel']}</h3>
                <h2>🎬 {mv['most_popular_creator_video_count']:,} videos</h2>
            </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 2 — CATEGORY & LANGUAGE ANALYTICS
# =============================================================================
with main_tabs[1]:

    st.markdown('<div class="section-header"><h3>📈 Category & Language Distribution</h3></div>', unsafe_allow_html=True)

    (category_stats, audio_language_stats, default_language_stats,
     definition_stats, caption_stats, license_stats) = doughnut_data.get_doughnut_data(filtered_df)

    metric_pie = st.radio(
        "",
        ["video_count", "avg_views", "avg_likes", "avg_comments", "avg_duration", "avg_engagement"],
        horizontal=True,
        label_visibility="collapsed",
        format_func=lambda x: {
            "video_count": "Total Videos",
            "avg_views": "Average Views",
            "avg_likes": "Average Likes",
            "avg_comments": "Average Comments",
            "avg_duration": "Average Duration",
            "avg_engagement": "Engagement Score",
        }[x]
    )

    # --- First Row (3 pies) ---
    cols = st.columns(3)

    pie_specs = [
        ("🎬 Category Performance", category_stats, "category_name"),
        ("🗣️ Default Video Language", default_language_stats, "default_language"),
        ("🎧 Audio Language Distribution", audio_language_stats, "audio_language")
    ]

    for col, (title, df, label_col) in zip(cols, pie_specs):
        with col:
            st.markdown(f"#### {title}")
            fig = go.Figure(data=[go.Pie(
                labels=df[label_col],
                values=df[metric_pie],
                hole=0.6
            )])
            fig.update_layout(height=420, margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)

    # --- Second Row (3 pies) ---
    cols = st.columns(3)

    pie_specs2 = [
        ("📺 Video Definition Quality", definition_stats, "definition"),
        ("📝 Caption Availability", caption_stats, "caption_available"),
        ("🔒 Licensed Content Breakdown", license_stats, "licensed_content")
    ]

    for col, (title, df, label_col) in zip(cols, pie_specs2):
        with col:
            st.markdown(f"#### {title}")
            fig = go.Figure(data=[go.Pie(
                labels=df[label_col],
                values=df[metric_pie],
                hole=0.6
            )])
            fig.update_layout(height=420, margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TAB 3 — TOP TRENDING VIDEOS
# =============================================================================
with main_tabs[2]:

    st.markdown('<div class="section-header"><h3>🎬 Trending Videos & Channels</h3></div>', unsafe_allow_html=True)

    cols = st.columns(2)

    with cols[0]:
        st.markdown("### Top Trending Videos")
        top_views, top_likes, top_comments, top_engagement = top_videos.get_top_videos(filtered_df)

        metric = st.radio(
            "",
            ["Top Views", "Top Likes", "Top Comments", "Top Engagement"],
            horizontal=True,
            label_visibility="collapsed"
        )

        metric_map = {
            "Top Views": top_views,
            "Top Likes": top_likes,
            "Top Comments": top_comments,
            "Top Engagement": top_engagement
        }

        st.dataframe(metric_map[metric], use_container_width=True, height=420)

    with cols[1]:
        st.markdown("### Leading Channels by Trending Presence")

        channel_stats = filtered_df.groupby("channel_title").agg({
            "video_id": "count",
            "views": "sum",
            "engagement_score": "mean"
        }).rename(columns={"video_id": "video_count"}).reset_index()

        top_channels = channel_stats.sort_values("video_count", ascending=False).head(10)

        fig = px.bar(
            top_channels, y="channel_title", x="video_count",
            orientation="h",
            title="Top Channels by Number of Trending Videos"
        )
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TAB 4 — VIEWER BEHAVIOR ANALYSIS
# =============================================================================
with main_tabs[3]:

    st.markdown('<div class="section-header"><h3>📊 Viewer Behavior Analysis</h3></div>', unsafe_allow_html=True)

    cols = st.columns(2)

    with cols[0]:
        st.markdown("### View–Like–Comment Relationship")
        fig = px.scatter(
            filtered_df, x="views", y="likes",
            size="comments", color="category_name",
            hover_data=["title", "channel_title"]
        )
        st.plotly_chart(fig, use_container_width=True)

    with cols[1]:
        st.markdown("### Engagement vs Video Duration")
        fig = px.scatter(
            filtered_df, x="duration", y="engagement_score",
            size="views", color="category_name",
            hover_data=["title", "channel_title"]
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Category Performance Variability")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Views Across Categories")
        fig = px.box(filtered_df, x="category_name", y="views")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Engagement Score Across Categories")
        fig = px.box(filtered_df, x="category_name", y="engagement_score")
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TAB 5 — CONTENT ATTRIBUTES & CORRELATIONS
# =============================================================================
with main_tabs[4]:

    st.markdown('<div class="section-header"><h3>📊 Content Attributes & Correlations</h3></div>', unsafe_allow_html=True)

    st.markdown("### Correlation Between Key Metrics")
    corr_cols = ["views", "likes", "comments", "duration", "tag_count", "engagement_score"]
    fig = px.imshow(filtered_df[corr_cols].corr(), text_auto=True, color_continuous_scale="Reds")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Distribution of Engagement Metrics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribution of Views")
        fig = px.histogram(filtered_df, x="views", nbins=30)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Distribution of Video Durations")
        fig = px.histogram(filtered_df, x="duration", nbins=30)
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TAB 6 — DURATION & TAG INFLUENCE ANALYSIS
# =============================================================================
with main_tabs[5]:

    st.markdown('<div class="section-header"><h3>📊 Duration & Tag Influence Analysis</h3></div>', unsafe_allow_html=True)

    cols = st.columns(2)

    with cols[0]:
        st.markdown("### Impact of Video Duration on Engagement Metrics")

        filtered_df["duration_bucket"] = pd.cut(
            filtered_df["duration"],
            bins=[0, 120, 300, 600, 1200, 99999],
            labels=["0–2 mins", "2–5 mins", "5–10 mins", "10–20 mins", "20+ mins"]
        )

        bucket_agg = filtered_df.groupby("duration_bucket").agg(
            avg_views=("views", "mean"),
            avg_engagement=("engagement_score", "mean")
        ).reset_index()

        fig = px.bar(
            bucket_agg, x="duration_bucket", y=["avg_views", "avg_engagement"],
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)

    with cols[1]:
        st.markdown("### Tag Usage vs Video Visibility")
        fig = px.scatter(
            filtered_df, x="tag_count", y="views",
            size="engagement_score", color="category_name"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Tag Cloud (Most Frequent Tags)")
    all_tags = " ".join(filtered_df["tags"].dropna().astype(str).tolist())
    if all_tags.strip():    
        wc = WordCloud(
            width=1200, height=500,
            background_color="black",
            colormap="Reds",
            margin=2
        ).generate(all_tags)
    
        st.image(wc.to_image(), use_container_width=True)
    else:
        st.info("No tags available for this category.")
    
