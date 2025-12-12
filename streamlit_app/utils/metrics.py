import streamlit as st
import pandas as pd

@st.cache_data()
def get_daily_metrics(df):
    most_viewed_video = df.nlargest(1, 'views')
    most_liked_video = df.nlargest(1, 'likes')
    most_commented_video = df.nlargest(1, 'comments')
    most_engaged_video = df.nlargest(1, 'engagement_score')
    longest_trending_video = df.nlargest(1, 'duration')
    most_popular_creator = df['channel_title'].value_counts().index[0]

    result = {
        'total_videos' : len(df),
        'total_views' : int(df['views'].sum()),
        'total_likes' : int(df['likes'].sum()),
        'total_comments' : int(df['comments'].sum()),
        'average_duration' : round(df['duration'].mean(), 2),
        'average_engagement_score' : round(df['engagement_score'].mean(), 2),
        'most_viewed_video_id' : most_viewed_video['video_id'].item(),
        'most_viewed_video_title' : most_viewed_video['title'].item(),
        'most_viewed_video_channel' : most_viewed_video['channel_title'].item(),
        'most_viewed_video_views' : int(most_viewed_video['views'].item()),
        'most_liked_video_id' : most_liked_video['video_id'].item(),
        'most_liked_video_title' : most_liked_video['title'].item(),
        'most_liked_video_channel' : most_liked_video['channel_title'].item(),
        'most_liked_video_likes' : int(most_liked_video['likes'].item()),
        'most_commented_video_id' : most_commented_video['video_id'].item(),
        'most_commented_video_title' : most_commented_video['title'].item(),
        'most_commented_video_channel' : most_commented_video['channel_title'].item(),
        'most_commented_video_comments' : int(most_commented_video['comments'].item()),
        'most_engaged_video_id' : most_engaged_video['video_id'].item(),
        'most_engaged_video_title' : most_engaged_video['title'].item(),
        'most_engaged_video_channel' : most_engaged_video['channel_title'].item(),
        'most_engaged_video_score' : round(most_engaged_video['engagement_score'].item(), 2),
        'longest_trending_video_id' : longest_trending_video['video_id'].item(),
        'longest_trending_video_title' : longest_trending_video['title'].item(),
        'longest_trending_video_channel' : longest_trending_video['channel_title'].item(),
        'longest_trending_video_duration' : int(longest_trending_video['duration'].item()),
        'most_popular_creator_channel_id' : df[df['channel_title'] == most_popular_creator]['channel_id'].unique()[0],
        'most_popular_creator_channel' : most_popular_creator,
        'most_popular_creator_video_count' : len(df[df['channel_title'] == most_popular_creator]),
    }

    return result