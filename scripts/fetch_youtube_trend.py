from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv
import json
import os
from datetime import datetime, timezone
from convert_duration import duration_to_seconds

# Load API Key
load_dotenv()

API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE = build("youtube", "v3", developerKey=API_KEY)

# Load category mapping
with open("../categories.json", "r") as f:
    cat_map = json.load(f)

def get_trending_videos(region):
    """
    Fetch top 50 trending videos for a given region.

    Parameters:
        region (str): Country code (e.g., 'IN', 'US')

    Returns:
        pd.DataFrame: Cleaned table of trending videos and metadata
    """
    request = YOUTUBE.videos().list(
        part="snippet,statistics,contentDetails",
        chart="mostPopular",
        regionCode=region,
        maxResults=50
    )
    response = request.execute()

    rows = []
    for v in response.get("items", []):
        snippet = v["snippet"]
        stats = v.get("statistics", {})
        content = v.get("contentDetails", {})
        status = v.get("status", {})
        cid = snippet.get("categoryId")

        rows.append({
            "video_id": v["id"],
            "country": region,
            "fetched_at": datetime.now(timezone.utc).isoformat(),

            # Snippet
            "published_at": snippet.get("publishedAt"),
            "title": snippet.get("title"),
            "localized_title": snippet.get("localized", {}).get("title"),
            "channel_title": snippet.get("channelTitle"),
            "channel_id": snippet.get("channelId"),
            "category_id": cid,
            "category_name": cat_map.get(cid, "Unknown"),
            "tags": ", ".join(snippet.get("tags", [])),
            "tag_count": len(snippet.get("tags", [])),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
            "default_language": snippet.get("defaultLanguage"),
            "audio_language": snippet.get("defaultAudioLanguage"),
            "is_live": snippet.get("liveBroadcastContent") == "live",

            # Content details
            "duration": duration_to_seconds(content.get("duration")),
            "duration_raw": content.get("duration"),
            "definition": content.get("definition"),
            "caption_available": content.get("caption") == "true",
            "licensed_content": content.get("licensedContent", False),
            "embeddable": status.get("embeddable", False),
            "made_for_kids": status.get("madeForKids", False),

            # Stats
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
        })


    df = pd.DataFrame(rows)

    return df
