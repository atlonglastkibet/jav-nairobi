# Jav: Deep Learning for Equitable Matatu Routing in Nairobi's Informal Transit Networks

> **Jav** (shengh for *Matatu*) is a deep learning project exploring how AI can make Nairobi’s informal public transit system more **efficient**, **predictable**, and **equitable**.  
> It focuses on **ETA prediction**, **congestion mapping**, and **route performance ranking** using open transport data.

## Overview

In Nairobi, matatus serve as the dominant form of public transport, used by approximately 48–58% of daily commuters, or an estimated 1.5–3.5 million people. Despite their central role in city mobility, the system remains largely informal and uncoordinated, leading to frequent congestion, unreliable travel times, and inequitable service distribution across neighborhoods.

Equity is the core differentiator between Jav and every other ETA or transit app.
Where others optimize purely for efficiency (fastest routes, least congestion), Jav optimizes for fairness; ensuring that matatu routes serving low-income or under-served neighborhoods are not algorithmically penalized or overlooked.

**Jav** seeks to leverage **deep learning + geospatial analytics** to predict travel times (ETAs) and highlight underserved routes, improving both commuter experience and policy planning.

* **Focus**: ETA forecasting (target MAE <5 mins), congestion mapping, and route performance ranking.
* **Stack**: PyTorch/TensorFlow (DL), FastAPI (API), GeoPandas (geospatial data), and OSMnx (routing), Supabase/Postgres (DB).
* **Goal**: Reduce commuter uncertainty, time savings and identify underserved routes for more equitable urban mobility.

## Problem Statement

Nairobi’s 135+ matatu routes lack standardized schedules or predictive travel time data.  
A 10 km trip can take over **78 minutes**, especially during peak congestion in low-income areas like **Kibera** or **Pipeline**.  

While commercial transit apps exist, none integrate **machine learning-based ETA forecasts** using live data (traffic, weather, route topology) or **equity metrics** for underserved regions.

## Objectives

1. To evaluate transit equity across Nairobi (GTFS).
2. To develop and train predictive models (GNN)
3. To rank routes based on coverage, ETA and congestion
## File Structure

```
.
├── client              # Frontend (React) placeholder
│   ├── components
│   ├── pages
│   └── public
│
├── data
│   ├── folium/                  # Saved folium maps (interactive HTML)
│   ├── model/                   # Trained models, checkpoints, embeddings
│   ├── plots/                   # Static PNG/JPEG figures
│   ├── processed/               # Cleaned datasets
│   ├── pydeck/                  # PyDeck / Deck.gl visualizations
│   ├── raw/                     # Raw GTFS, PBF, and API downloads
│   ├── training_data/           # Datasets prepared for model training
│   └── training_output/         # Logs, metrics, artifacts from training runs
│
├── docs
│   ├── architecture.md          # System design, pipeline architecture
│   ├── gini_coeffecient.md      # Equity analysis methods
│   ├── literature review/       # Academic + industry references
│   ├── proposal.md              # Project proposal / white paper
│   ├── results.md               # Model results + evaluation
│   └── stop_features_test_data.csv
│
├── notebooks
│   ├── 01_gtfs_data.ipynb                     # Load + explore GTFS stops, routes, shapes
│   ├── 02_worldmove_data.ipynb                # Load + explore WorldMove mobility/ETA data
│   ├── 03b_spatial_clustering.ipynb           # Cluster stops based on spatial features
│   ├── 03_equity_analysis(spatial).ipynb      # Spatial equity: access, Gini, underserved areas
│   ├── 04b_temporal_clustering.ipynb          # Temporal clustering using traffic / peak-hour patterns
│   ├── 04_equity_analysis(temporal).ipynb     # Temporal equity: time-of-day service fairness
│   ├── 06_calendar(spatial+temporal).ipynb    # Merge spatial + temporal features into a unified calendar
│   ├── 07_worldmove_traffic+ETA.ipynb         # Relationship between traffic and ETA; early models
│   ├── 08_stop-level_feature_engineering.ipynb# Build stop-level features from all data sources
│   ├── 09_stop-level_feature_cleaning.ipynb   # Clean, scale, and validate stop-level feature matrix
│   ├── 10_gnn_training.ipynb                  # Train GNN on transit network + stop features
│   ├── 11_route_extensions.ipynb              # Route variants, scoring, ranking, folium maps
│   ├── cache/                                 # Cached artifacts for faster notebook execution
│   └── lib/                                   # Notebook helper utilities
│
├── scripts
│   ├── fetch_gtfs.py
│   ├── premium_viz_minimal.py
│   └── __pycache__/
│
├── server
│   └── app/                     # Backend (FastAPI) placeholder
│
├── utils
│   ├── __init__.py
│   ├── __pycache__/
│   └── viz_utils.py             # folium viz util function for notebook 11
│
├── README.md
├── requirements.txt
└── .gitignore

```

## Data Sources

| Source | Description | Format |
|--------|--------------|---------|
| [Digital Matatus GTFS](https://digitalmatatus.com/data) | Route, stop, and shape data | GTFS (TXT) |
| [WorldMove website](https://fi.ee.tsinghua.edu.cn/worldmove/data) | Large-scale synthetic mobility dataset | ASSORTED |
| [OpenWeatherMap API](https://openweathermap.org/history) | Weather features | JSON |
| [OpenStreetMap (Geofabrik Kenya)](https://download.geofabrik.de/africa/kenya.html) | Road network topology | PBF |

## Methodology

### **Objective 1: Equity-Aware Transit Evaluation**

**Foundation:** Quantify spatial and temporal inequities in Nairobi's transit system to identify underserved areas requiring intervention.

#### A. Spatial Equity — Static Coverage Analysis

Measures **geographic access** by computing the proportion of each ward's area (and population) within 500m walking distance of matatu stops.

**Mathematical Formulation:**

Let:
- $S = \{s_1, s_2, ..., s_n\}$ be the set of $n$ transit stops
- $W = \{w_1, w_2, ..., w_m\}$ be the set of $m$ wards
- $P_j$ be the population of ward $w_j$
- $A_j$ be the total area of ward $w_j$

**Step 1: Buffer Generation**

For each stop $s_i$ with coordinates $(lat_i, lon_i)$, create a circular buffer:

$$B_i = \{(x, y) : d((x,y), (lat_i, lon_i)) \leq 500m\}$$

where $d(\cdot, \cdot)$ is the Euclidean distance in projected coordinates (UTM Zone 37S).

**Step 2: Coverage Union**

Compute the union of all buffers to create the total service coverage area:

$$C_{total} = \bigcup_{i=1}^{n} B_i$$

**Step 3: Ward Intersection**

For each ward $w_j$, calculate the intersection area with coverage:

$$A_{covered,j} = \text{Area}(w_j \cap C_{total})$$

**Step 4: Coverage Ratio**

Calculate the proportion of ward area covered:

$$r_{coverage,j} = \frac{A_{covered,j}}{A_j}$$

where $0 \leq r_{coverage,j} \leq 1$

**Step 5: Population Served**

Estimate population with transit access (assuming uniform population distribution):

$$P_{served,j} = P_j \times r_{coverage,j}$$

**Step 6: Access Percentage**

Calculate percentage of population with transit access:

$$\text{pct\_access}_j = \frac{P_{served,j}}{P_j} \times 100 = r_{coverage,j} \times 100$$

**Step 7: Gini Coefficient for Spatial Inequality**

Measure equity using the Gini coefficient across all wards:

$$G_{spatial} = \frac{\sum_{j=1}^{m} \sum_{k=1}^{m} |\text{pct\_access}_j - \text{pct\_access}_k|}{2m^2 \bar{\mu}}$$

where $\bar{\mu} = \frac{1}{m}\sum_{j=1}^{m} \text{pct\_access}_j$ is the mean access percentage.

Alternatively, using the standard Gini formulation with sorted values:

$$G_{spatial} = \frac{2\sum_{j=1}^{m} j \cdot \text{pct\_access}_j^{sorted}}{m \sum_{j=1}^{m} \text{pct\_access}_j} - \frac{m+1}{m}$$

where $\text{pct\_access}_j^{sorted}$ represents access percentages sorted in ascending order.

**Interpretation:**
- $G_{spatial} = 0$: Perfect equality (all wards have same access)
- $G_{spatial} = 1$: Maximum inequality (one ward has all access)
- Target: $G_{spatial} < 0.3$ (acceptable equity)

**Outputs:**  
- Ward-level scorecard ranking by coverage (0.15% to 100%)
- Folium choropleth visualizing access inequality
- Identification of 37 underserved wards (<70% coverage) as target areas

**Key Finding:** 28 wards are well-served (≥90% coverage), while 17 are severely underserved (<50% coverage).

---

#### B. Temporal Equity — Dynamic Service Availability

Extends spatial coverage into **time-varying access** using GTFS schedules to compute hourly service levels per ward.

**Mathematical Formulation:**

Let:
- $H = \{0, 1, 2, ..., 23\}$ be the set of hours in a day
- $T_{i,h}$ be the number of trips at stop $s_i$ during hour $h$
- $S_j = \{s_i : s_i \in w_j\}$ be the set of stops in ward $w_j$

**Step 1: Hourly Trip Aggregation**

For each ward $w_j$ and hour $h$, sum all trips:

$$T_{j,h} = \sum_{s_i \in S_j} T_{i,h}$$

**Step 2: Per-Capita Service Intensity**

Normalize by ward population:

$$\sigma_{j,h} = \frac{T_{j,h}}{P_j}$$

This represents trips per person per hour in ward $j$ at time $h$.

**Step 3: Service Density (trips per 1000 people)**

$$\sigma_{j,h}^{1000} = \sigma_{j,h} \times 1000 = \frac{1000 \cdot T_{j,h}}{P_j}$$

**Step 4: Daily Service Profile**

For each ward, create a 24-hour service vector:

$$\vec{\sigma}_j = [\sigma_{j,0}, \sigma_{j,1}, ..., \sigma_{j,23}]$$

**Step 5: Temporal Gini Coefficient**

Measure within-ward temporal inequality:

$$G_{temporal,j} = \frac{\sum_{h=1}^{24} \sum_{h'=1}^{24} |\sigma_{j,h} - \sigma_{j,h'}|}{2 \cdot 24^2 \cdot \bar{\sigma}_j}$$

where $\bar{\sigma}_j = \frac{1}{24}\sum_{h=0}^{23} \sigma_{j,h}$ is the mean service intensity for ward $j$.

**Step 6: Coefficient of Variation**

Alternative temporal equity metric using coefficient of variation:

$$CV_j = \frac{\sqrt{\frac{1}{24}\sum_{h=0}^{23}(\sigma_{j,h} - \bar{\sigma}_j)^2}}{\bar{\sigma}_j}$$

Higher $CV_j$ indicates more variable (less equitable) service throughout the day.

**Step 7: Peak-to-Off-Peak Ratio**

Define peak hours $H_{peak} = \{6,7,8,9,17,18,19,20\}$ and calculate:

$$\rho_j = \frac{\bar{\sigma}_{j,peak}}{\bar{\sigma}_{j,offpeak}}$$

where:

$$\bar{\sigma}_{j,peak} = \frac{1}{|H_{peak}|}\sum_{h \in H_{peak}} \sigma_{j,h}$$

$$\bar{\sigma}_{j,offpeak} = \frac{1}{24-|H_{peak}|}\sum_{h \notin H_{peak}} \sigma_{j,h}$$

**Step 8: Overall Temporal Equity Score**

Aggregate across all wards:

$$G_{temporal}^{overall} = \frac{1}{m}\sum_{j=1}^{m} G_{temporal,j}$$

**Interpretation:**
- $G_{temporal,j} \approx 0$: Consistent service throughout the day
- $G_{temporal,j} \approx 1$: Service concentrated in few hours
- $\rho_j > 3$: Significant peak concentration (poor temporal equity)

**Outputs:**  
- Hourly service heatmaps showing peak vs off-peak disparities
- Temporal scorecards identifying wards with inconsistent service
- Integration of $\sigma_{j,h}$ into ward features for downstream modeling

**Key Finding:** Service concentrates during 6-9 AM and 5-8 PM peaks ($\rho_j > 4$ for most wards), with minimal off-peak coverage in underserved areas.

### **Objective 2: Graph Neural Network for Stop Placement Optimization**

**Core Engine:** Learn optimal stop placement patterns from well-served benchmark areas and predict suitable locations in underserved regions.

#### A. Traffic & Congestion Proxy Derivation (WorldMove Data)

Since real-time traffic data is unavailable, we derive **traffic proxies** and **ETA estimates** from the WorldMove synthetic mobility dataset.

**Steps:**

1. **Load WorldMove trajectories** (104,538 agents, 1.05M trips):
```python
   trips_df = pl.read_parquet('worldmove_trips.parquet')
```

2. **Compute cell-level traffic metrics** by aggregating hourly:
```python
   cell_traffic = trips_df.group_by(['origin_cell', 'hour']).agg([
       pl.col('speed_kmh').mean().alias('avg_speed_kmh'),
       pl.col('agent_id').n_unique().alias('trip_count'),
       (pl.col('congestion_level').is_in(['congested', 'heavily_congested']).sum() / 
        pl.col('congestion_level').count() * 100).alias('congestion_pct')
   ])
```

3. **Classify congestion levels** based on speed thresholds:
```python
   congestion_level = pl.when(speed < 10).then('heavily_congested')
                        .when(speed < 20).then('congested')
                        .when(speed < 30).then('moderate')
                        .otherwise('free_flow')
```

4. **Estimate route ETAs** by summing segment travel times:
```python
   def calculate_route_eta(route_id, hour):
       stops = get_route_stops(route_id)
       total_eta = 0
       for seg in stop_pairs(stops):
           cell_speed = get_cell_speed(seg.midpoint, hour)
           distance = haversine(seg.from_stop, seg.to_stop)
           total_eta += (distance / cell_speed) * 60  # minutes
       return total_eta
```

**Outputs:**  
- `model2_traffic.csv`: Cell-level hourly traffic (170 cells, 24 hours)
- Route-level ETA estimates for all GTFS routes
- Temporal variability metrics (`demand_cv`, `peak_to_offpeak_ratio`)
#### B. Stop-Level Feature Engineering

Extract 36 features per stop location (existing + candidates) combining road network, demographics, service patterns, and traffic.

**Feature Categories:**

1. **Road Network** (via OSMNx):
   - `nearest_node_degree`: Intersection connectivity
   - `is_intersection`: Boolean (degree ≥ 3)
   - `road_type`: OSM highway classification
   - `distance_to_major_road`: Meters to primary/secondary road

2. **Stop Spacing**:
   - `distance_to_nearest_stop`, `distance_to_2nd_nearest`, `distance_to_3rd_nearest`
   - `stop_density_1km`: Stops per km²
   - `spacing_regularity`: Std dev of 3-nearest distances

3. **Population/Demand**:
   - `pop_within_500m`, `pop_within_1km`: People in catchment
   - `pop_density_500m`: Density estimate
   - `poverty_rate_weighted_pop`: Equity-weighted population

4. **Service Patterns** (from GTFS):
   - `route_count_serving`: Routes at this stop
   - `trips_per_day`, `trips_per_hour_peak`, `trips_per_hour_offpeak`
   - `avg_headway_minutes`: Time between vehicles
   - `service_span_hours`: Operating hours

5. **Traffic/Congestion** (from WorldMove):
   - `avg_speed_daily`, `avg_speed_peak`, `avg_speed_offpeak`
   - `congestion_pct_daily`, `congestion_pct_peak`
   - `trip_count_daily`, `trip_count_peak`
   - `demand_variability_cv`: Coefficient of variation

6. **Ward Context**:
   - `ward_pct_access`: Current coverage
   - `ward_population`, `ward_pop_density`, `ward_poverty_rate`
   - `is_benchmark_ward`: Coverage ≥70%
   - `ward_service_per_capita`: Trips per 1000 people

7. **Spatial Features**:
   - `distance_to_cbd`: Distance to Nairobi CBD (-1.2864, 36.8172)
   - `distance_to_ward_centroid`

8. **Derived/Engineered**:
   - `coverage_efficiency_nearby`: Ward access / stops in ward
   - `demand_supply_ratio`: Population / trips per day
   - `network_accessibility`: Node degree / distance to major road
   - `equity_score`: Underserved population × poverty weight

**Dataset Construction:**

- **Positive samples**: 4,284 existing GTFS stops (label=1 if in benchmark ward)
- **Negative samples**: 4,250 random candidate locations >300m from existing stops (label=0)
- **Total training samples**: ~8,500 (sufficient for GNN training)

#### C. Graph Construction & GNN Architecture

**Graph Representation:**

Construct an undirected graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathbf{X})$ where:

$$\mathcal{V} = V_{stops} \cup V_{candidates}$$

$$V_{stops} = \{s_1, s_2, ..., s_n\} \text{ (existing GTFS stops)}$$

$$V_{candidates} = \{c_1, c_2, ..., c_k\} \text{ (candidate locations)}$$

**Edge Construction (k-NN Graph):**

For each node $v_i \in \mathcal{V}$, connect to its $k$ nearest neighbors:

$$\mathcal{E} = \{(v_i, v_j) : v_j \in \text{kNN}(v_i, k=10)\}$$

where distance is computed as:

$$d(v_i, v_j) = \sqrt{(lat_i - lat_j)^2 + (lon_i - lon_j)^2}$$

**Node Feature Matrix:**

$$\mathbf{X} \in \mathbb{R}^{|\mathcal{V}| \times 36}$$

where each row $\mathbf{x}_i$ contains the 36-dimensional feature vector for node $v_i$.

**GNN Model Architecture (Graph Attention Network):**

$$\mathbf{H}^{(0)} = \mathbf{X}$$

**Layer 1: Multi-head Graph Attention**

$$\mathbf{H}^{(1)} = \text{ReLU}\left(\text{GAT}(\mathbf{H}^{(0)}, \mathcal{E}; \text{heads}=4)\right)$$

where GAT attention mechanism:

$$\alpha_{ij} = \frac{\exp(\text{LeakyReLU}(\mathbf{a}^T[\mathbf{W}\mathbf{h}_i || \mathbf{W}\mathbf{h}_j]))}{\sum_{k \in \mathcal{N}(i)} \exp(\text{LeakyReLU}(\mathbf{a}^T[\mathbf{W}\mathbf{h}_i || \mathbf{W}\mathbf{h}_k]))}$$

$$\mathbf{h}_i^{(1)} = \sigma\left(\sum_{j \in \mathcal{N}(i)} \alpha_{ij} \mathbf{W}\mathbf{h}_j^{(0)}\right)$$

**Layer 2: Additional GAT Layer**

$$\mathbf{H}^{(2)} = \text{ReLU}\left(\text{GAT}(\mathbf{H}^{(1)}, \mathcal{E}; \text{heads}=2)\right)$$

**Layer 3: GraphSAGE Aggregation**

$$\mathbf{H}^{(3)} = \text{ReLU}\left(\text{SAGE}(\mathbf{H}^{(2)}, \mathcal{E})\right)$$

where:

$$\mathbf{h}_i^{(3)} = \sigma\left(\mathbf{W} \cdot \text{CONCAT}(\mathbf{h}_i^{(2)}, \text{AGG}(\{\mathbf{h}_j^{(2)}, \forall j \in \mathcal{N}(i)\}))\right)$$

**Classification Head:**

$$\mathbf{z}_i = \text{MLP}(\mathbf{h}_i^{(3)}) = \mathbf{W}_2 \cdot \text{ReLU}(\mathbf{W}_1 \mathbf{h}_i^{(3)} + \mathbf{b}_1) + \mathbf{b}_2$$

$$\hat{y}_i = \sigma(\mathbf{z}_i)$$

where $\sigma(\cdot)$ is the sigmoid function and $\hat{y}_i \in [0,1]$ is the predicted stop suitability score.

**Loss Function:**

Binary Cross-Entropy with class weights:

$$\mathcal{L} = -\frac{1}{|\mathcal{V}|}\sum_{i=1}^{|\mathcal{V}|} w_i\left[y_i \log(\hat{y}_i) + (1-y_i)\log(1-\hat{y}_i)\right]$$

where $w_i$ balances positive/negative classes.

**Why GNN?**
- Captures **spatial dependencies** via message passing: $\mathbf{h}_i^{(l+1)} = f(\mathbf{h}_i^{(l)}, \{\mathbf{h}_j^{(l)} : j \in \mathcal{N}(i)\})$
- Models **spatial autocorrelation** (nearby locations have similar suitability)
- Learns **graph-structured relationships** that tabular ML cannot capture

**Training:**
- Optimizer: Adam with $\alpha = 0.001$, $\beta_1 = 0.9$, $\beta_2 = 0.999$
- Train/Val/Test Split: 70/15/15 from benchmark wards
- Metrics: Accuracy, Precision, Recall, F1, AUC-ROC

---

#### D. Stop Placement Prediction & Route Ranking

**Composite Scoring Function:**

For each candidate location $c_i$, compute a multi-objective score:

$$S_{composite}(c_i) = w_{cov} \cdot f_{coverage}(c_i) + w_{eta} \cdot f_{eta}(c_i) + w_{cong} \cdot f_{congestion}(c_i)$$

where:

**Coverage Gain:**

$$f_{coverage}(c_i) = \frac{\Delta P_{served}}{\max(\Delta P_{served})} = \frac{P_{served}^{new} - P_{served}^{current}}{\max_j(P_{served,j}^{new} - P_{served,j}^{current})}$$

**ETA Score (normalized, inverted):**

$$f_{eta}(c_i) = 1 - \frac{\text{ETA}(c_i) - \min(\text{ETA})}{\max(\text{ETA}) - \min(\text{ETA})}$$

**Congestion Score (normalized, inverted):**

$$f_{congestion}(c_i) = 1 - \frac{\text{congestion\_pct}(c_i)}{100}$$

**Weight Configuration:**

$$w_{cov} = 0.6, \quad w_{eta} = 0.2, \quad w_{cong} = 0.2$$

**Final Ranking:**

$$\text{Rank}(c_i) = \text{argsort}_{descending}(S_{composite}(c_1), ..., S_{composite}(c_k))$$

**Outputs:**
- Top-K stop recommendations per underserved ward
- Route extension proposals with predicted coverage gains
- Interactive Folium maps showing predicted vs current coverage

#### D. Stop Placement Prediction & Route Ranking

**Composite Scoring Function:**

For each candidate location $c_i$, compute a multi-objective score:

$$S_{composite}(c_i) = w_{cov} \cdot f_{coverage}(c_i) + w_{eta} \cdot f_{eta}(c_i) + w_{cong} \cdot f_{congestion}(c_i)$$

where:

**Coverage Gain:**

$$f_{coverage}(c_i) = \frac{\Delta P_{served}}{\max(\Delta P_{served})} = \frac{P_{served}^{new} - P_{served}^{current}}{\max_j(P_{served,j}^{new} - P_{served,j}^{current})}$$

**ETA Score (normalized, inverted):**

$$f_{eta}(c_i) = 1 - \frac{\text{ETA}(c_i) - \min(\text{ETA})}{\max(\text{ETA}) - \min(\text{ETA})}$$

**Congestion Score (normalized, inverted):**

$$f_{congestion}(c_i) = 1 - \frac{\text{congestion\_pct}(c_i)}{100}$$

**Weight Configuration:**

$$w_{cov} = 0.6, \quad w_{eta} = 0.2, \quad w_{cong} = 0.2$$

**Final Ranking:**

$$\text{Rank}(c_i) = \text{argsort}_{descending}(S_{composite}(c_1), ..., S_{composite}(c_k))$$

**Outputs:**
- Top-K stop recommendations per underserved ward
- Route extension proposals with predicted coverage gains
- Interactive Folium maps showing predicted vs current coverage


### **Objective 3: Benchmarking & Validation**

**Validation Strategy:**

1. **Holdout validation**: Test GNN on held-out benchmark wards
2. **Spatial cross-validation**: Ensure model generalizes across different geographic regions
3. **Baseline comparison**: GNN vs Random Forest vs XGBoost on tabular features
4. **Ablation studies**: Measure contribution of graph structure vs node features

**Expected Metrics:**
- GNN accuracy: >80% on stop classification
- Coverage improvement: +15-25% in target wards
- Equity gain: Gini coefficient reduction of 0.1-0.15

**Deliverables:**
- Trained GNN model weights
- Benchmark report comparing GNN vs ML baselines
- Interactive dashboard with stop recommendations
- Policy brief for Nairobi transit authorities

## Assumptions & Limitations

### Assumptions

1. **WorldMove as Traffic Proxy**: Synthetic mobility data accurately represents real-world traffic patterns in Nairobi. While derived from real trajectories, it may not capture extreme congestion events or special circumstances.

2. **Static Population Distribution**: Ward-level population data is assumed uniform within each ward. Actual population density varies at finer spatial scales.

3. **500m Walking Distance**: Universal 500m buffer assumes flat terrain and walkable infrastructure. Actual accessibility varies by neighborhood infrastructure quality.

4. **GTFS Completeness**: Digital Matatus GTFS data (2014) represents current routes. The informal nature of matatus means routes may have changed.

5. **Benchmark Transferability**: Patterns learned from well-served wards (≥70% coverage) are assumed transferable to underserved areas despite potential demographic/geographic differences.

### Limitations

1. **Temporal Scope**: WorldMove data represents a single day (October 1, 2025). Seasonal, weekly, and holiday variations are not captured.

2. **Real-Time Data**: No live traffic feeds; all predictions based on historical proxy data.

3. **Informal Dynamics**: Matatu routes are fluid and demand-responsive. Model assumes static route structure from GTFS.

4. **Infrastructure Constraints**: Model predicts optimal locations but doesn't account for land availability, road safety, or physical feasibility.

5. **Equity Weights**: Current equity scoring is heuristic. More sophisticated multi-criteria optimization could improve fairness metrics.

6. **Validation Data**: No ground-truth "optimal stop" dataset exists. Validation relies on proxy metrics (coverage gain, existing stop patterns).


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

* Digital Matatus & University of Nairobi for GTFS data
* WorldMove team at Tsinghua University for mobility dataset
* OpenStreetMap contributors
* Kenya National Bureau of Statistics for census data