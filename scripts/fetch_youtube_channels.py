from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE = build("youtube", "v3", developerKey=API_KEY)


def get_trending_channels(channel_ids):
    """
    Fetch channel details for one or multiple channels.

    Parameters:
        channel_ids (str or list): single channel_id or list of channel_ids (max 50 per request)

    Returns:
        pd.DataFrame: channel info including snippet, statistics, branding, status
    """
    request = YOUTUBE.channels().list(
        part="snippet,statistics,brandingSettings,status,topicDetails",
        id=",".join(channel_ids)
    )
    response = request.execute()

    rows = []
    for ch in response.get("items", []):
        snippet = ch.get("snippet", {})
        stats = ch.get("statistics", {})
        branding = ch.get("brandingSettings", {}).get("image", {})
        status = ch.get("status", {})

        topic_details = ch.get("topicDetails", {})
        topic_ids = topic_details.get("topicIds", [])
        topic_categories = topic_details.get("topicCategories", []) # Wikipedia URLs
        cleaned_topics = [t.split('/')[-1] for t in topic_categories]

        rows.append({
            # Basic IDs
            "channel_id": ch.get("id"),
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "published_at": snippet.get("publishedAt"),
            "thumbnails": snippet.get("thumbnails", {}).get("high", {}).get("url"),
            "custom_url": snippet.get("customUrl"),
            "default_language": snippet.get("defaultLanguage"),
            "country": snippet.get("country"),

            # Statistics
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),

            # Branding
            "banner_url": branding.get("bannerExternalUrl"),
            "keywords": ch.get("brandingSettings", {}).get("channel", {}).get("keywords"),
            "topics": ", ".join(cleaned_topics),

            # Status
            "made_for_kids": status.get("madeForKids", False),
            "privacy_status": status.get("privacyStatus"),
        })

    df = pd.DataFrame(rows)

    return df
