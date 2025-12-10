# 📊 YouTube Trending Analytics

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://youtube-trending-analytics.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/sheb1lmsp/youtube-trending-analytics)](https://github.com/sheb1lmsp/youtube-trending-analytics/commits/main)

A complete analytics pipeline to **fetch, store, analyze, and visualize YouTube Trending Videos**, updated automatically every day using **GitHub Actions at 12:30 PM UTC**.

---

## 🚀 Overview

**YouTube Trending Analytics** is a data-driven project that continuously collects trending YouTube videos and generates insights through python scripts and a Streamlit dashboard.
Data is automatically fetched daily, cleaned, versioned, and stored—ideal for time-series research, trend discovery, and creator analytics.

---

## 🔥 Features

* ⏱ **Daily automated YouTube Trending fetch at 12:30 PM UTC** (GitHub Actions)
* 📥 Clean collection of trending video metadata
* 🧹 Preprocessing, transformations, helpers, and utilities
* 📊 Interactive [Streamlit dashboard](https://youtube-trending-analytics.streamlit.app/) showing **today’s insights**
* 🗂 Structured files for categories, countries, and mappings
* 🧩 Easily extensible for ML and long-term trending analysis

---

## 📁 Repository Structure

```
.
├── data/                     # Automatically updated daily trending snapshots
├── notebooks/                # Data pipeline scirpts and debugging
├── scripts/                  # Fetch, processing, utilities
│   └── main.py     # Script triggered by GitHub Actions
├── streamlit_app/            # Streamlit dashboard (Home.py)
    └── utils/                # Helper functions for dashboard and analysis
├── categories.json           # YouTube categories mapping
├── countries.json            # Supported country codes
├── requirements.txt          # Python dependencies
├── .github/
│   └── workflows/
│       └── daily.yml  # Scheduled daily workflow
└── README.md
```

---

## ⏱️ Automated Daily Fetching With GitHub Actions

The repository includes a cron-based GitHub Action that runs **every day at 12:30 PM UTC**, executes the fetch script, saves new data to the `data/` folder, and auto-commits it.

### 🔧 GitHub Actions Workflow (`daily.yml`)

```yaml
name: Fetch YouTube Trending (Daily)

on:
  schedule:
    - cron: "30 12 * * *"   # Runs daily at 12:30 PM UTC
  workflow_dispatch:

jobs:
  fetch-trending:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install Dependencies
        run: pip install -r requirements.txt

      - name: Run Fetch Script
        run: python scripts/main.py

      - name: Commit & Push Data
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Auto-update: Daily trending data"
```

---

## 🛠️ Getting Started

### 1️⃣ Installation

```bash
git clone https://github.com/sheb1lmsp/youtube-trending-analytics.git
cd youtube-trending-analytics
pip install -r requirements.txt
```

### 2️⃣ Run the Streamlit Dashboard

```bash
streamlit run streamlit_app/Home.py
```

### 3️⃣ Explore Notebooks

Open `.ipynb` files inside the `notebooks/` folder for visual exploration and insight generation.

---

## 🧾 Data Description

Daily trending snapshots include:

* `video_id`, `title`, `localized_title`
* `channel_title`, `channel_id`
* `published_at`, `fetched_at`
* `views`, `likes`, `comments`
* `category_id`, `category_name`
* `tags`, `tag_count`
* `thumbnail`, `description`, engagement stats

These snapshots allow:

* 📈 Time-series trending pattern analysis
* 🏷 Category-level performance comparison
* 🎬 Creator popularity studies
* 🧠 Feature engineering for ML
* 🌍 (Future) cross-country trend comparisons

---

## 📊 Streamlit Dashboard (Today’s Insights Only)

The dashboard includes:

* Key metrics
* Category analytics
* Channel-level insights
* Engagement/interaction analysis
* Word clouds
* Distribution charts
* Top-N videos
* Filters, drop-downs, and well-aligned columns

The entire dashboard is optimized for **today’s trending dataset only**.

---

## 🤝 Contributing

Contributions are welcome!
Feel free to open:

* Issues
* Pull Requests
* Enhancement suggestions

Please update `requirements.txt` if adding new dependencies.

---

## 📜 License

This project is licensed under the **MIT License**.
See the `LICENSE` file for full details.

---

## 🙏 Acknowledgments

* Inspired by YouTube trending analytics studies and public datasets
* Utilizes YouTube Data API metadata
* Thanks to the open-source community for tools & librar
