# Jav: Deep Learning for Equitable Matatu Routing in Nairobi's Informal Transit Networks

> **Jav** (shengh for *Matatu*) is a deep learning project exploring how AI can make Nairobi’s informal public transit system more **efficient**, **predictable**, and **equitable**.  
> It focuses on **ETA prediction**, **congestion mapping**, and **route performance ranking** using open transport data.

## Overview

In Nairobi, matatus serve as the dominant form of public transport, used by approximately 48–58% of daily commuters, or an estimated 1.5–3.5 million people. Despite their central role in city mobility, the system remains largely informal and uncoordinated, leading to frequent congestion, unreliable travel times, and inequitable service distribution across neighborhoods.

**Jav** seeks to leverage **deep learning + geospatial analytics** to predict travel times (ETAs) and highlight underserved routes, improving both commuter experience and policy planning.

* **Focus**: ETA forecasting (target MAE <5 mins), congestion mapping, and route performance ranking.
* **Stack**: PyTorch/TensorFlow (DL), FastAPI (API), GeoPandas (geospatial data), and OSMnx (routing), Supabase/Postgres (DB).
* **Goal**: Reduce commuter uncertainty, time savings and identify underserved routes for more equitable urban mobility.

## Problem Statement

Nairobi’s 135+ matatu routes lack standardized schedules or predictive travel time data.  
A 10 km trip can take over **78 minutes**, especially during peak congestion in low-income areas like **Kibera** or **Pipeline**.  

While commercial transit apps exist, none integrate **machine learning-based ETA forecasts** using live data (traffic, weather, route topology) or **equity metrics** for underserved regions.

## Objectives

* Develop **LSTM-based ETA models** 
* Combine GTFS data with traffic and weather features for context-aware predictions. 
* Model and rank routes by reliability, coverage, and congestion likelihood. 
* Establish **equity-aware metrics** (e.g., low-coverage route weighting). 
* Benchmark performance against baselines (ARIMA, Prophet). 
* Prototype a **FastAPI backend** for predictions and route ranking (future integration).

## File Structure

```
.
├── data
│   ├── raw/                        # Raw downloads (GTFS, CSVs, PBF)
│   └── processed/                  # Cleaned tensors/CSVs (e.g., seqs.parquet)
│
├── notebooks/                      # Jupyter notebooks for EDA, training
│   ├── 01_gtfs_eda.ipynb           # Parse GTFS & explore stop sequences
│   ├── 02_feature_engineering.ipynb# Merge traffic & weather features
│   └── 03_model_lstm.ipynb         # LSTM training + evaluation
│
├── scripts/
│   ├── fetch_gtfs.py               # Download Digital Matatus GTFS
│   ├── preprocess_data.py          # Clean & prepare route/traffic/weather
│   └── train_model.py              # Script-based model training
│
├── server/                         # Placeholder for FastAPI backend (later phase)
│   └── app/
│       └── main.py                 # (Future) endpoints /routes, /predict
│
├── docs/
│   ├── proposal.md                 # White paper
│   ├── architecture.md             # Methodology, system design
│   └── results.md                  # Performance metrics, bias audit
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Data Sources

| Source | Description | Format |
|--------|--------------|---------|
| [Digital Matatus GTFS](https://digitalmatatus.com/data) | Route, stop, and shape data | GTFS (TXT) |
| [WorldMove website](https://fi.ee.tsinghua.edu.cn/worldmove/data) | large-scale synthetic mobility dataset | ASSORTED |
| [OpenWeatherMap API](https://openweathermap.org/history) | Weather features | JSON |
| [OpenStreetMap (Geofabrik Kenya)](https://download.geofabrik.de/africa/kenya.html) | Road network topology | PBF |

## Methodology

1. **Data Integration:**

   * Parse GTFS into stop sequences (GeoPandas).
   * Merge with traffic and weather as contextual features.

2. **Feature Engineering:**

   * Encode time-of-day, weekday/weekend, rainfall probability, and average speed.
   * Create stop-level tensors: `[lat, lon, speed, rain_prob, time_slot, seq_id]`.

3. **Modeling:**

   * Train **LSTM** for sequential ETA prediction (`input_dim=7`, `seq_len=15`).
   * Compare with ARIMA and Prophet baselines.
   * Evaluate with MAE, RMSE, and temporal stability tests.

4. **Equity Audit:**

   * Compute route service coverage ratios (population / vehicle frequency).
   * Adjust route scores to reduce bias toward high-income areas.

### Setup

```bash
git clone git@github.com:atlonglastkibet/jav-nairobi.git
cd jav-nairobi
pip install -r requirements.txt
jupyter notebook
```

## License

MIT License – see [LICENSE](LICENSE).

## Acknowledgments

* Digital Matatus & University of Nairobi GTFS Project
* WorldMove datasets
* OpenWeatherMap & OSM for open APIs