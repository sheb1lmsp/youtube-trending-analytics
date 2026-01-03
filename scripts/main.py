import pandas as pd
import datetime
import os
import time
import json
from fetch_youtube_trend import get_trending_videos

# Load list of YouTube-supported countries
with open("../countries.json", 'r') as f:
    countries = json.load(f)

def run():
    """
    Main workflow:
    - Create folder structure for the current year
    - Fetch trending videos for every country
    - Save country-level CSV files
    """
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    year = today.split("-")[0]
    month = today.split("-")[1]
    BASE_DIR = os.path.abspath(".")
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")

    for country in countries:
        print(f"\nFetching trending videos for {country}...")

        try:
            df = get_trending_videos(country)

            # Skip empty results
            if df.empty:
                print(f"No trending data for {country}, skipping.")
                continue

            # Folder for the specific country and the date
            COUNTRY_DIR = os.path.join(DATA_DIR, f"country={country}", f"year={year}", f"month={month}")
            os.makedirs(COUNTRY_DIR, exist_ok=True)

            # Save daily file
            file_path = os.path.join(
                COUNTRY_DIR,
                f"trending_{country}_{today}.csv"
            )

            df.to_csv(file_path, index=False)
            print(f"Saved → {file_path}")

            time.sleep(0.3)  # Avoid API quota bursts

        except Exception as e:
            print(f"Error fetching {country}: {e}")

# Execute workflow when script is run
if __name__ == "__main__":
    run()
