import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
from pathlib import Path
import os
import json

DATA_DIR = Path('../data')
all_data_path_list = list(DATA_DIR.glob('*/*/*.csv'))
CHECK_TIME = time(6,5)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
COUNTRY_FILE = os.path.join(BASE_DIR, "country_names.json")

print(DATA_DIR)
print(COUNTRY_FILE)

with open(COUNTRY_FILE, 'r') as f:
    country_names = json.load(f)

@st.cache_data()
def get_country_name(alpha_2):
    try:
        return country_names[alpha_2]
    except:
        return None

@st.cache_data()
def get_latest_data():
    today = datetime.now()
    if today.time() > CHECK_TIME:
        pattern = f"{today.strftime('%Y-%m-%d')}"
    else:
        yesterday = today - timedelta(days=1)
        pattern = f"{yesterday.strftime('%Y-%m-%d')}"

    df = pd.DataFrame()
    for data_path in all_data_path_list:
        if pattern in str(data_path):
            current_df = pd.read_csv(data_path)

            current_df['country_name'] = current_df['country'].apply(get_country_name)

            df = pd.concat((df, current_df), axis=0)

    df['published_at'] = pd.to_datetime(df['published_at'])
    df['fetched_at'] = pd.to_datetime(df['fetched_at'])
    df['engagement_score'] = (df['likes'] + df['comments']) /  df['views']

    return df
