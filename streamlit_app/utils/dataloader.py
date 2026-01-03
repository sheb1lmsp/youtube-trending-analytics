import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from pathlib import Path
import os
import json

BASE_DIR = os.path.abspath('.')
DATA_DIR = Path(os.path.join(BASE_DIR, 'data'))

COUNTRY_FILE = os.path.join(BASE_DIR, "streamlit_app","country_names.json")

CHECK_TIME = time(6,10)

with open(COUNTRY_FILE, 'r') as f:
    country_names = json.load(f)

@st.cache_data()
def get_country_name(alpha_2):
    try:
        return country_names[alpha_2]
    except:
        return None

@st.cache_data(ttl=3600)
def get_latest_data():
    today = datetime.now(ZoneInfo("Asia/Kolkata"))
    if today.time() > CHECK_TIME:
        pattern = f"{today.strftime('%Y-%m-%d')}"
    else:
        yesterday = today - timedelta(days=1)
        pattern = f"{yesterday.strftime('%Y-%m-%d')}"

    df = pd.DataFrame()
    all_data_path_list = list(DATA_DIR.glob(f"*/*/*/*{pattern}.csv"))
    for data_path in all_data_path_list:
        current_df = pd.read_csv(data_path)

        current_df['country_name'] = current_df['country'].apply(get_country_name)

        df = pd.concat((df, current_df), axis=0)

    df['published_at'] = pd.to_datetime(df['published_at'])
    df['fetched_at'] = pd.to_datetime(df['fetched_at'])
    df['engagement_score'] = (df['likes'] + df['comments']) /  df['views']

    return df
