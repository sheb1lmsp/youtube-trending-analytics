import pandas as pd
import datetime
import os
import time
import json
import numpy as np

# Import existing functions
from fetch_youtube_trend import get_trending_videos
from fetch_youtube_channels import get_trending_channels

# Load list of YouTube-supported countries
with open("../countries.json", 'r') as f:
    countries = json.load(f)

def run():
    """
    Main workflow:
    - Create folder structure for the current year
    - Fetch trending videos for every country
    - Save country-level CSV files
    - Update Master Channel List
    """
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    year = today.split("-")[0]
    month = today.split("-")[1]

    # Robust path handling
    BASE_DIR = os.path.dirname(os.path.abspath('.'))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")

    # To store unique channel ids found TODAY
    today_channel_ids = np.array([], dtype=str)

    # --- STEP 1: FETCH VIDEOS ---
    for country in countries:
        print(f"\nFetching trending videos for {country}...")

        try:
            df = get_trending_videos(country)

            # Skip empty results
            if df.empty:
                print(f"No trending data for {country}, skipping.")
                continue

            # Folder for the specific country and the date
            COUNTRY_DIR = os.path.join(DATA_DIR, "videos", f"country={country}", f"year={year}", f"month={month}")
            os.makedirs(COUNTRY_DIR, exist_ok=True)

            # Save daily file
            file_path = os.path.join(COUNTRY_DIR, f"trending_{country}_{today}.csv")
            df.to_csv(file_path, index=False)
            print(f"Saved → {file_path}")

            # Collect unique channels from this batch
            if 'channel_id' in df.columns:
                unique_channels_current = df['channel_id'].dropna().astype(str).unique()
                today_channel_ids = np.union1d(today_channel_ids, unique_channels_current)

            time.sleep(0.5)  # Avoid API quota bursts

        except Exception as e:
            print(f"Error fetching {country}: {e}")

    # --- STEP 2: UPDATE MASTER CHANNEL LIST ---
    channels_dir = os.path.join(DATA_DIR, "channels")
    os.makedirs(channels_dir, exist_ok=True)
    channels_path = os.path.join(channels_dir, "trending_channels.csv")

    # Handle First Run (File doesn't exist yet)
    if os.path.exists(channels_path):
        channels_df = pd.read_csv(channels_path)
        existing_ids = channels_df['channel_id'].astype(str).unique()
    else:
        print("\nMaster channel file not found. Creating new one.")
        channels_df = pd.DataFrame(columns=['channel_id'])
        existing_ids = np.array([], dtype=str)

    # Calculate which channels are actually NEW
    # np.setdiff1d returns elements in 'today_channel_ids' that are NOT in 'existing_ids'
    new_channels_to_fetch = np.setdiff1d(today_channel_ids, existing_ids)

    print(f"\nTotal channels found today: {len(today_channel_ids)}")
    print(f"New channels to fetch: {len(new_channels_to_fetch)}")

    if len(new_channels_to_fetch) == 0:
        print("No new channels to fetch. Exiting.")
        return

    # Batch fetch new channels
    new_channel_dfs = []

    # Convert numpy array to python list for safety
    fetch_list = new_channels_to_fetch.tolist()

    for i in range(0, len(fetch_list), 50):
        batch = fetch_list[i:i+50]
        try:
            print(f"Fetching channel batch {i} to {i+len(batch)}...")
            temp_df = get_trending_channels(batch)

            if not temp_df.empty:
                new_channel_dfs.append(temp_df)

            time.sleep(0.5) # Be nice to the API

        except Exception as e:
            print(f"Channel fetch failed for batch {i}: {e}")

    # Save Updates
    if new_channel_dfs:
        new_data_df = pd.concat(new_channel_dfs, ignore_index=True)

        # Combine old data + new data
        updated_channels_df = pd.concat([channels_df, new_data_df], ignore_index=True)

        # Save back to CSV
        updated_channels_df.to_csv(channels_path, index=False)
        print(f"✅ Updated master channel list. Total channels: {len(updated_channels_df)}")
    else:
        print("❌ Warning: New channels were identified but fetch returned no data.")

if __name__ == "__main__":
    run()
