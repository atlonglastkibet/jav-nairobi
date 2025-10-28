# Digital Matatus GTFS Data

## Overview
The Digital Matatus project provides open GTFS (General Transit Feed Specification) data for Nairobi's informal matatu (minibus) system, collected via crowdsourced cell phone tracking. This dataset covers 135+ routes and 2,000+ stops, enabling analysis of semi-formal transit patterns. Shapes files include route geometries for visualization. Data is from 2015-2017 (with updates via community contributions); ideal for ETA modeling, equity audits, or route optimization in projects like Jav.

**Key Stats**: 135 routes, ~2k stops, paratransit-focused (flexible, unregulated service).

**License**: Creative Commons Attribution 4.0 (CC BY 4.0) – Attribute to Digital Matatus Project (MIT Senseable City Lab, UC Berkeley, + partners).

## Files Included
Standard GTFS ZIP structure, with Digital Matatus extensions (e.g., unique route/stop IDs for informal networks). Extract with `unzip digital_matatus_nairobi_gtfs.zip`.

| File | Description | Size (approx.) | Notes |
|------|-------------|----------------|-------|
| **agency.txt** | Transit agencies (e.g., matatu saccos/operators). | 1 KB | 10+ entries; includes names like "Nairobi Matatu Owners Association". |
| **stops.txt** | Stop locations (lat/lon, names like "Kibera Stage"). | 50 KB | 2,000+ rows; geo-enabled for mapping. |
| **routes.txt** | Route details (IDs, names like "Route 33: CBD-Kilimani", types). | 10 KB | 135+ informal routes; short/long-haul variants. |
| **trips.txt** | Trip instances (route ID, trip ID, direction). | 100 KB | Links routes to schedules; handles bidirectional service. |
| **stop_times.txt** | Timetables (arrival/departure per stop/trip). | 500 KB | Variable headways; proxy for frequencies (e.g., every 5-15 mins). |
| **calendar.txt** | Service days (Mon-Sun validity for trips). | 5 KB | Covers daily/weekly patterns; no holidays (paratransit norm). |
| **shapes.txt** | Route geometries (polyline points for shapes). | 200 KB | 1,000+ shape IDs; lat/lon sequences for Folium/Leaflet viz. |
| **frequencies.txt** | Headway intervals (e.g., mats/hour). | 20 KB | Key for demand modeling; varies by peak/off-peak. |

**Total Size**: ~1 MB (ZIP). No feed_info.txt (static feed).

## Usage
Load in Python for analysis (e.g., with `gtfs-kit` or Pandas):

```python
import pandas as pd
import geopandas as gpd

# Extract ZIP if needed
df_stops = pd.read_csv('stops.txt')  # Geo: gpd.GeoDataFrame(df_stops, geometry=gpd.points_from_xy(df_stops.lon, df_stops.lat))
df_shapes = pd.read_csv('shapes.txt')  # Plot: df_shapes.plot(x='shape_pt_lon', y='shape_pt_lat')

# Example: Route graph
from gtfs_kit import GTFS
gtfs = GTFS.from_path('.')  # Or 'digital_matatus_nairobi_gtfs.zip'
print(gtfs.head('routes'))  # Inspect
```

For shapes: Use Shapely/GeoPandas to buffer routes (e.g., 500m service areas) or Folium for maps.

**Tips**: Handle informal quirks (e.g., variable stops) with interpolation. Validate feed with Google's GTFS validator.

## Source & Credits
- **Download**: [digitalmatatus.com/data](https://digitalmatatus.com/data) (ZIP feed).
- **Project**: MIT Senseable City Lab + UC Berkeley (2015-ongoing); crowdsourced via app.
- **Docs**: [GTFS Spec](https://gtfs.org/reference/static/) + [Digital Matatus Paper](https://dspace.mit.edu/handle/1721.1/120152).

**Last Updated**: October 2025 (v2.1; check site for refreshes). Contribute fixes via GitHub issues!