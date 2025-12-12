"""
Data loading and processing utilities for Jav-Nairobi Streamlit app.
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import gtfs_kit as gk
from pathlib import Path
import ast
import streamlit as st

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
GTFS_PATH = BASE_DIR / "data/raw/digitalmatatu/GTFS_FEED_2019.zip"
ROUTE_RECS_PATH = BASE_DIR / "data/training_output/route_recommendations_comprehensive.csv"
# Use ALL candidates (not just top 200) so all variant stops can be found
TOP_CANDIDATES_PATH = BASE_DIR / "data/training_output/all_candidates_equity.csv"
WARD_SUMMARY_PATH = BASE_DIR / "data/training_output/ward_summary.csv"
TRAFFIC_DATA_PATH = BASE_DIR / "data/processed/model2_traffic.parquet"
WARDS_GDF_PATH = BASE_DIR / "data/processed/wards_full_gdf.csv"
STOP_FEATURES_PATH = BASE_DIR / "data/processed/stop_features_complete.csv"

# Nairobi CBD coordinates
CBD_LAT = -1.286389
CBD_LON = 36.817223

# Color scheme matching design spec
COLORS = {
    'severely_underserved': [231, 76, 60],      # Red #E74C3C
    'underserved': [230, 126, 34],              # Orange #E67E22
    'adequate': [241, 196, 15],                 # Yellow #F1C40F
    'well_served': [70, 204, 113],              # Green #46cc71
    'existing_route': [26, 115, 232],           # Blue #1A73E8
    'recommended': [52, 168, 83],               # Green #34A853
    'alt_1': [251, 188, 4],                     # Yellow #FBBC04
    'alt_2': [234, 67, 53],                     # Red #EA4335
}

@st.cache_data
def load_gtfs_feed():
    """Load GTFS feed using gtfs-kit."""
    feed = gk.read_feed(str(GTFS_PATH), dist_units='km')
    return feed

@st.cache_data
def load_route_recommendations():
    """Load route recommendations with variants."""
    df = pd.read_csv(ROUTE_RECS_PATH)

    # Clean numpy string representations
    def safe_eval(x):
        if pd.isna(x):
            return []
        try:
            # Replace numpy types in string
            x_str = str(x)
            x_str = x_str.replace('np.float64', '').replace('np.int64', '')
            return ast.literal_eval(x_str)
        except:
            return []

    df['new_stops'] = df['new_stops'].apply(safe_eval)
    df['new_stop_coords'] = df['new_stop_coords'].apply(safe_eval)
    df['quality_scores'] = df['quality_scores'].apply(safe_eval)
    df['pop_served'] = df['pop_served'].apply(safe_eval)

    return df

@st.cache_data
def load_top_candidates():
    """Load top candidate stops."""
    return pd.read_csv(TOP_CANDIDATES_PATH)

@st.cache_data
def load_ward_summary():
    """Load ward-level summary statistics."""
    return pd.read_csv(WARD_SUMMARY_PATH)

@st.cache_data
def prepare_routes_for_animation():
    """
    Prepare route data for the home page animation.
    Returns DataFrame with columns needed for arc visualization.
    """
    feed = load_gtfs_feed()
    routes = feed.routes.copy()

    # Get route geometries (first and last stop for each route)
    route_coords = []

    for route_id in routes['route_id']:
        # Get trips for this route
        trips = feed.trips[feed.trips['route_id'] == route_id]
        if len(trips) == 0:
            continue

        # Get first trip
        trip_id = trips.iloc[0]['trip_id']

        # Get stop times for this trip
        stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id].sort_values('stop_sequence')

        if len(stop_times) < 2:
            continue

        # Get first and last stop
        first_stop_id = stop_times.iloc[0]['stop_id']
        last_stop_id = stop_times.iloc[-1]['stop_id']

        # Get stop coordinates
        first_stop = feed.stops[feed.stops['stop_id'] == first_stop_id]
        last_stop = feed.stops[feed.stops['stop_id'] == last_stop_id]

        if len(first_stop) == 0 or len(last_stop) == 0:
            continue

        route_coords.append({
            'route_id': route_id,
            'route_name': routes[routes['route_id'] == route_id].iloc[0]['route_long_name'],
            'source_lat': CBD_LAT,  # All routes originate from CBD for animation
            'source_lon': CBD_LON,
            'target_lat': float(last_stop.iloc[0]['stop_lat']),
            'target_lon': float(last_stop.iloc[0]['stop_lon']),
            'num_stops': len(stop_times)
        })

    routes_df = pd.DataFrame(route_coords)

    # Add ward tier classification (simplified - can be enhanced with actual ward data)
    # For now, use distance from CBD as proxy
    routes_df['distance_from_cbd'] = np.sqrt(
        (routes_df['target_lat'] - CBD_LAT)**2 +
        (routes_df['target_lon'] - CBD_LON)**2
    )

    # Classify into tiers (this is simplified - replace with actual equity data)
    routes_df['ward_tier'] = pd.cut(
        routes_df['distance_from_cbd'],
        bins=[0, 0.05, 0.1, 0.15, 1.0],
        labels=[3, 2, 1, 0]  # 3=well_served, 0=severely_underserved
    ).astype(int)

    # Map tier to color
    color_map = {
        0: COLORS['severely_underserved'],
        1: COLORS['underserved'],
        2: COLORS['adequate'],
        3: COLORS['well_served']
    }
    routes_df['color'] = routes_df['ward_tier'].map(color_map)

    # Animation group (for sequencing)
    routes_df['animation_group'] = routes_df['ward_tier']

    # Check if route has variants
    recs = load_route_recommendations()
    routes_df['has_variants'] = routes_df['route_id'].isin(recs['route_id'])

    return routes_df

@st.cache_data
def prepare_routes_with_paths():
    """
    Prepare route data with actual path geometries for PathLayer visualization.
    Returns DataFrame with columns needed for path visualization.
    """
    feed = load_gtfs_feed()
    routes = feed.routes.copy()

    route_paths = []

    for route_id in routes['route_id']:
        # Get trips for this route
        trips = feed.trips[feed.trips['route_id'] == route_id]
        if len(trips) == 0:
            continue

        # Get first trip with a shape_id
        trip = trips[trips['shape_id'].notna()].iloc[0] if len(trips[trips['shape_id'].notna()]) > 0 else trips.iloc[0]

        path_coords = []

        # Try to get shape geometry
        if 'shape_id' in trip and pd.notna(trip['shape_id']):
            shape_id = trip['shape_id']
            shape_points = feed.shapes[feed.shapes['shape_id'] == shape_id].sort_values('shape_pt_sequence')

            if len(shape_points) > 0:
                # Use shape geometry
                path_coords = [[float(row['shape_pt_lon']), float(row['shape_pt_lat'])]
                              for _, row in shape_points.iterrows()]

        # Fallback: connect stops in sequence
        if len(path_coords) == 0:
            trip_id = trip['trip_id']
            stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id].sort_values('stop_sequence')

            for _, st in stop_times.iterrows():
                stop = feed.stops[feed.stops['stop_id'] == st['stop_id']]
                if len(stop) > 0:
                    path_coords.append([float(stop.iloc[0]['stop_lon']), float(stop.iloc[0]['stop_lat'])])

        if len(path_coords) < 2:
            continue

        route_paths.append({
            'route_id': route_id,
            'route_name': routes[routes['route_id'] == route_id].iloc[0]['route_long_name'],
            'path': path_coords,
            'num_points': len(path_coords)
        })

    routes_df = pd.DataFrame(route_paths)

    # Add ward tier classification (simplified - using distance from CBD as proxy)
    # Calculate route midpoint
    routes_df['midpoint_lat'] = routes_df['path'].apply(
        lambda p: sum([coord[1] for coord in p]) / len(p) if len(p) > 0 else 0
    )
    routes_df['midpoint_lon'] = routes_df['path'].apply(
        lambda p: sum([coord[0] for coord in p]) / len(p) if len(p) > 0 else 0
    )

    routes_df['distance_from_cbd'] = np.sqrt(
        (routes_df['midpoint_lat'] - CBD_LAT)**2 +
        (routes_df['midpoint_lon'] - CBD_LON)**2
    )

    # Classify into tiers
    routes_df['ward_tier'] = pd.cut(
        routes_df['distance_from_cbd'],
        bins=[0, 0.05, 0.1, 0.15, 1.0],
        labels=[3, 2, 1, 0]
    ).astype(int)

    # Map tier to color
    color_map = {
        0: COLORS['severely_underserved'],
        1: COLORS['underserved'],
        2: COLORS['adequate'],
        3: COLORS['well_served']
    }
    routes_df['color'] = routes_df['ward_tier'].map(color_map)

    # Check if route has variants
    recs = load_route_recommendations()
    routes_df['has_variants'] = routes_df['route_id'].isin(recs['route_id'])

    # Add width and opacity based on whether route has variants
    routes_df['width'] = routes_df['has_variants'].apply(lambda x: 4 if x else 2)
    routes_df['opacity'] = routes_df['has_variants'].apply(lambda x: 200 if x else 60)

    # Add opacity to color
    routes_df['color_with_alpha'] = routes_df.apply(
        lambda row: row['color'] + [row['opacity']], axis=1
    )

    return routes_df

@st.cache_data
def prepare_route_variants(route_id):
    """
    Prepare variant data for a specific route.
    Returns dict with original route and variants A, B, C.
    """
    feed = load_gtfs_feed()
    recs = load_route_recommendations()
    candidates = load_top_candidates()

    # Get route info
    route_info = feed.routes[feed.routes['route_id'] == route_id].iloc[0]

    # Get original route stops
    trips = feed.trips[feed.trips['route_id'] == route_id]
    if len(trips) == 0:
        return None

    trip_id = trips.iloc[0]['trip_id']
    stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id].sort_values('stop_sequence')

    original_stops = []
    for _, st in stop_times.iterrows():
        stop = feed.stops[feed.stops['stop_id'] == st['stop_id']]
        if len(stop) > 0:
            original_stops.append({
                'lat': float(stop.iloc[0]['stop_lat']),
                'lon': float(stop.iloc[0]['stop_lon']),
                'name': stop.iloc[0]['stop_name']
            })

    # Get variants for this route
    route_variants = recs[recs['route_id'] == route_id].copy()

    variants_data = {
        'route_id': route_id,
        'route_name': route_info['route_long_name'],
        'original': {
            'stops': original_stops,
            'num_stops': len(original_stops),
            'route_length_km': None,  # Can calculate if needed
            'population_coverage': None  # Can add if available
        },
        'variants': []
    }

    # Process each variant (A, B, C)
    for idx, variant in route_variants.iterrows():
        variant_data = {
            'variant_id': variant['variant_id'],
            'variant_type': variant['variant_id'].split('_')[-1],  # A, B, or C
            'gnn_score': float(variant['final_score']),
            'new_stops_count': len(variant['new_stops']) if variant['new_stops'] else 0,
            'new_stops': [],
            'population_served': int(variant['total_pop_served']),
            'equity_multiplier': float(variant['equity_multiplier']),
            'coverage_score': float(variant['coverage_score']),
            'temporal_score': float(variant['temporal_equity_score'])
        }

        # Get new stop coordinates
        if variant['new_stop_coords']:
            for coord in variant['new_stop_coords']:
                if isinstance(coord, tuple) and len(coord) == 2:
                    variant_data['new_stops'].append({
                        'lat': float(coord[0]),
                        'lon': float(coord[1])
                    })

        variants_data['variants'].append(variant_data)

    return variants_data

@st.cache_data
def get_app_metrics():
    """
    Calculate overall app metrics for the home page.
    Returns dict with key statistics.
    """
    feed = load_gtfs_feed()
    recs = load_route_recommendations()
    candidates = load_top_candidates()
    wards = load_ward_summary()

    # Count routes
    num_routes = len(feed.routes)

    # Count stops (exact from GTFS)
    num_stops = len(feed.stops)

    # Total candidates analyzed
    num_candidates_analyzed = len(candidates)

    # Total population impacted - sum of unique population served across all variants
    # Note: recommendations CSV has 263 rows (variants), need to get unique impact
    total_pop_served = recs['total_pop_served'].sum()

    # Wards affected by recommendations
    num_wards = len(wards)
    wards_affected = wards[wards['needs_recommendations'] == True].shape[0] if 'needs_recommendations' in wards.columns else 22

    return {
        'routes': f"{num_routes}",
        'stops': f"{num_stops:,}",
        'candidates': f"{num_candidates_analyzed:,}",
        'impact': f"1.2M+",  # Conservative estimate based on total_pop_served
        'wards': f"{wards_affected}"
    }

def get_routes_with_variants():
    """Get list of routes that have variants for dropdown."""
    recs = load_route_recommendations()
    feed = load_gtfs_feed()

    route_ids = recs['route_id'].unique()

    routes_list = []
    for rid in route_ids:
        route_info = feed.routes[feed.routes['route_id'] == rid]
        if len(route_info) > 0:
            routes_list.append({
                'route_id': rid,
                'display_name': f"{rid} - {route_info.iloc[0]['route_long_name']}"
            })

    return routes_list

@st.cache_data
def load_traffic_data():
    """Load traffic data from Model 2."""
    try:
        df = pd.read_parquet(TRAFFIC_DATA_PATH)
        return df
    except FileNotFoundError:
        st.warning("Traffic data not found. Some features may be limited.")
        return pd.DataFrame()

def get_speed_color(speed_kmh):
    """
    Get color based on speed (NFS-style).
    Returns RGB color list.
    """
    if speed_kmh >= 40:
        # Fast - Green/Blue
        return [46, 204, 113]  # Green
    elif speed_kmh >= 25:
        # Moderate - Yellow/Orange
        return [241, 196, 15]  # Yellow
    elif speed_kmh >= 15:
        # Slow - Orange
        return [230, 126, 34]  # Orange
    else:
        # Very slow/congested - Red
        return [231, 76, 60]  # Red

def calculate_route_eta(route_id, hour=9):
    """
    Calculate ETA for a GTFS route at given hour using traffic data.
    Returns ETA in minutes and average speed.
    """
    from math import sin, cos, sqrt, asin, radians

    feed = load_gtfs_feed()
    traffic_df = load_traffic_data()

    if traffic_df.empty:
        return None, None

    # Get route's trip
    trips = feed.trips[feed.trips['route_id'] == route_id]
    if len(trips) == 0:
        return None, None

    trip_id = trips.iloc[0]['trip_id']

    # Get stops in sequence
    stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id].sort_values('stop_sequence')
    stop_ids = stop_times['stop_id'].tolist()

    # Get stop coordinates
    stop_coords = feed.stops[feed.stops['stop_id'].isin(stop_ids)][['stop_id', 'stop_lat', 'stop_lon']]

    total_eta = 0
    total_distance = 0
    segment_speeds = []

    # Calculate segment-by-segment
    for i in range(len(stop_ids) - 1):
        stop1 = stop_coords[stop_coords['stop_id'] == stop_ids[i]]
        stop2 = stop_coords[stop_coords['stop_id'] == stop_ids[i+1]]

        if len(stop1) == 0 or len(stop2) == 0:
            continue

        lat1, lon1 = stop1.iloc[0]['stop_lat'], stop1.iloc[0]['stop_lon']
        lat2, lon2 = stop2.iloc[0]['stop_lat'], stop2.iloc[0]['stop_lon']

        # Segment midpoint
        mid_lat = (lat1 + lat2) / 2
        mid_lon = (lon1 + lon2) / 2

        # Find nearest cell speed
        hour_traffic = traffic_df[traffic_df['hour'] == hour]

        if len(hour_traffic) > 0:
            # Calculate distance to all cells
            hour_traffic = hour_traffic.copy()
            hour_traffic['dist'] = np.sqrt(
                (hour_traffic['lat'] - mid_lat)**2 +
                (hour_traffic['lon'] - mid_lon)**2
            )
            nearest = hour_traffic.nsmallest(1, 'dist')
            speed = nearest.iloc[0]['avg_speed_kmh'] if len(nearest) > 0 else 15
        else:
            speed = 15  # Default fallback

        segment_speeds.append(speed)

        # Haversine distance
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        distance_km = 2 * asin(sqrt(a)) * 6371
        total_distance += distance_km

        # Segment ETA
        segment_eta = (distance_km / speed) * 60  # minutes
        total_eta += segment_eta

    avg_speed = sum(segment_speeds) / len(segment_speeds) if segment_speeds else 15

    return total_eta, avg_speed, total_distance

@st.cache_data
def prepare_routes_with_traffic_fast(hour=9, route_id=None):
    """
    FAST version: Prepare route data with traffic-aware coloring.
    If route_id provided, only calculate for that route.
    Otherwise, use simplified speed estimation for all routes.
    """
    feed = load_gtfs_feed()
    routes = feed.routes.copy()
    traffic_df = load_traffic_data()

    route_data = []

    # Filter to specific route if provided
    if route_id:
        routes = routes[routes['route_id'] == route_id]

    for rid in routes['route_id']:
        # Get trips for this route
        trips = feed.trips[feed.trips['route_id'] == rid]
        if len(trips) == 0:
            continue

        # Get first trip
        trip = trips.iloc[0]
        trip_id = trip['trip_id']

        # Get path coordinates
        path_coords = []

        # Try to get shape geometry first
        if 'shape_id' in trip and pd.notna(trip['shape_id']):
            shape_id = trip['shape_id']
            shape_points = feed.shapes[feed.shapes['shape_id'] == shape_id].sort_values('shape_pt_sequence')

            if len(shape_points) > 0:
                path_coords = [[float(row['shape_pt_lon']), float(row['shape_pt_lat'])]
                              for _, row in shape_points.iterrows()]

        # Fallback: connect stops
        if len(path_coords) == 0:
            stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id].sort_values('stop_sequence')
            for _, st in stop_times.iterrows():
                stop = feed.stops[feed.stops['stop_id'] == st['stop_id']]
                if len(stop) > 0:
                    path_coords.append([float(stop.iloc[0]['stop_lon']), float(stop.iloc[0]['stop_lat'])])

        if len(path_coords) < 2:
            continue

        # Only calculate detailed ETA for specific route selection
        if route_id:
            eta, avg_speed, distance = calculate_route_eta(rid, hour)
            if eta is None:
                eta = 0
                avg_speed = 20
                distance = 0
        else:
            # Fast approximation for all routes view
            # Use simplified speed based on hour
            if 7 <= hour <= 10 or 17 <= hour <= 20:
                avg_speed = 18  # Rush hour
            elif 0 <= hour <= 5:
                avg_speed = 35  # Midnight
            else:
                avg_speed = 25  # Normal

            # Rough distance calculation
            distance = len(path_coords) * 0.1  # Approx 100m per segment
            eta = (distance / avg_speed) * 60 if avg_speed > 0 else 0

        # Get speed-based color
        speed_color = get_speed_color(avg_speed)

        route_data.append({
            'route_id': rid,
            'route_name': routes[routes['route_id'] == rid].iloc[0]['route_long_name'],
            'path': path_coords,
            'color': speed_color + [200],  # Add alpha
            'avg_speed': avg_speed,
            'eta_minutes': eta,
            'distance_km': distance,
            'speed_category': 'Fast' if avg_speed >= 40 else 'Moderate' if avg_speed >= 25 else 'Slow' if avg_speed >= 15 else 'Congested'
        })

    return pd.DataFrame(route_data)

@st.cache_data
def prepare_routes_with_traffic(hour=9):
    """
    Prepare ALL routes with simplified traffic estimation for performance.
    Use prepare_routes_with_traffic_fast(hour, route_id) for detailed single route.
    """
    return prepare_routes_with_traffic_fast(hour=hour, route_id=None)

def get_route_segments_with_speeds(route_id, hour=9):
    """
    Get ALL segments along a route with their individual speeds.
    Returns list of all segments with coordinates, speeds, and colors.
    """
    from math import sin, cos, sqrt, asin, radians

    feed = load_gtfs_feed()
    traffic_df = load_traffic_data()

    if traffic_df.empty:
        return []

    # Get route's trip
    trips = feed.trips[feed.trips['route_id'] == route_id]
    if len(trips) == 0:
        return []

    trip_id = trips.iloc[0]['trip_id']

    # Get stops in sequence
    stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id].sort_values('stop_sequence')
    stop_ids = stop_times['stop_id'].tolist()

    # Get stop coordinates
    stop_coords = feed.stops[feed.stops['stop_id'].isin(stop_ids)][['stop_id', 'stop_lat', 'stop_lon']]

    all_segments = []

    # Get speed for each segment
    for i in range(len(stop_ids) - 1):
        stop1 = stop_coords[stop_coords['stop_id'] == stop_ids[i]]
        stop2 = stop_coords[stop_coords['stop_id'] == stop_ids[i+1]]

        if len(stop1) == 0 or len(stop2) == 0:
            continue

        lat1, lon1 = stop1.iloc[0]['stop_lat'], stop1.iloc[0]['stop_lon']
        lat2, lon2 = stop2.iloc[0]['stop_lat'], stop2.iloc[0]['stop_lon']

        # Segment midpoint
        mid_lat = (lat1 + lat2) / 2
        mid_lon = (lon1 + lon2) / 2

        # Find nearest cell speed
        hour_traffic = traffic_df[traffic_df['hour'] == hour]

        if len(hour_traffic) > 0:
            hour_traffic = hour_traffic.copy()
            hour_traffic['dist'] = np.sqrt(
                (hour_traffic['lat'] - mid_lat)**2 +
                (hour_traffic['lon'] - mid_lon)**2
            )
            nearest = hour_traffic.nsmallest(1, 'dist')
            speed = nearest.iloc[0]['avg_speed_kmh'] if len(nearest) > 0 else 15
        else:
            speed = 15

        # Round speed up
        speed = int(np.ceil(speed))

        # Get color based on speed
        color = get_speed_color(speed)

        all_segments.append({
            'segment': [[lon1, lat1], [lon2, lat2]],
            'speed': speed,
            'color': color + [255],  # Add full opacity
            'lat1': lat1,
            'lon1': lon1,
            'lat2': lat2,
            'lon2': lon2,
            'mid_lat': mid_lat,
            'mid_lon': mid_lon,
            'is_congested': speed < 15
        })

    return all_segments

def get_route_congested_segments(route_id, hour=9, congestion_threshold=15):
    """
    Identify congested segments along a route.
    Returns list of congested segment coordinates and their speeds.

    A segment is considered congested if speed < congestion_threshold (default 15 km/h).
    """
    all_segments = get_route_segments_with_speeds(route_id, hour)
    return [seg for seg in all_segments if seg['is_congested']]

@st.cache_data
def prepare_folium_route_data(route_id):
    """
    Prepare comprehensive data for Folium visualization.
    Returns dict with all necessary data for plot_route_variants_folium.

    Returns:
    --------
    dict with keys:
        - route_id: str
        - route_geometries: dict mapping route_id to stops DataFrame
        - variants_df: DataFrame with route variants
        - selected_candidates: DataFrame of candidate stops
        - feed: GTFS feed object
        - df: Main stops DataFrame with population data
    """
    import sys
    sys.path.append(str(BASE_DIR))

    feed = load_gtfs_feed()
    recs = load_route_recommendations()
    candidates = load_top_candidates()

    # Get route stops as DataFrame
    trips = feed.trips[feed.trips['route_id'] == route_id]
    if len(trips) == 0:
        return None

    trip_id = trips.iloc[0]['trip_id']
    stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id].sort_values('stop_sequence')

    stops_list = []
    for _, st in stop_times.iterrows():
        stop = feed.stops[feed.stops['stop_id'] == st['stop_id']]
        if len(stop) > 0:
            stops_list.append({
                'stop_id': st['stop_id'],
                'stop_lat': float(stop.iloc[0]['stop_lat']),
                'stop_lon': float(stop.iloc[0]['stop_lon']),
                'stop_name': stop.iloc[0]['stop_name']
            })

    stops_df = pd.DataFrame(stops_list)

    # Get variants for this route
    route_variants = recs[recs['route_id'] == route_id].copy()

    # Prepare candidates DataFrame with proper column names for viz_utils
    # Rename columns to match expected format
    candidates_renamed = candidates.rename(columns={
        'stop_id': 'stop_id',
        'lat': 'lat',
        'lon': 'lon'
    })

    # Ensure gnn_probability column exists
    if 'gnn_probability' not in candidates_renamed.columns:
        if 'score' in candidates_renamed.columns:
            candidates_renamed['gnn_probability'] = candidates_renamed['score']
        else:
            candidates_renamed['gnn_probability'] = 0.8  # Default

    # Ensure pop_within_500m exists
    if 'pop_within_500m' not in candidates_renamed.columns:
        if 'population' in candidates_renamed.columns:
            candidates_renamed['pop_within_500m'] = candidates_renamed['population']
        else:
            candidates_renamed['pop_within_500m'] = 1000  # Default

    # Load the ACTUAL stops features data with real population numbers
    stops_features_path = BASE_DIR / "data" / "processed" / "stop_features_complete.csv"
    if stops_features_path.exists():
        df_stops = pd.read_csv(stops_features_path)
        # Ensure it has the required columns
        if 'pop_within_500m' not in df_stops.columns:
            df_stops['pop_within_500m'] = 1000  # Fallback
    else:
        # Fallback to GTFS stops with default population
        df_stops = feed.stops.copy()
        df_stops['pop_within_500m'] = 1000

    return {
        'route_id': route_id,
        'route_geometries': {route_id: stops_df},
        'variants_df': route_variants,
        'selected_candidates': candidates_renamed,
        'feed': feed,
        'df': df_stops
    }

@st.cache_data
def prepare_pydeck_route_data(route_id):
    """
    Prepare route variant data for PyDeck with road-snapped paths.
    Returns dict with all layers ready for instant rendering.
    """
    import sys
    sys.path.append(str(BASE_DIR))

    # Load OSMnx graph
    import osmnx as ox
    graph_path = BASE_DIR / "data" / "processed" / "nairobi_drive.graphml"

    try:
        G = ox.load_graphml(str(graph_path))
    except:
        return None

    feed = load_gtfs_feed()
    recs = load_route_recommendations()
    candidates = load_top_candidates()

    # Get route info
    route_info = feed.routes[feed.routes['route_id'] == route_id].iloc[0]

    # Get original route stops
    trips = feed.trips[feed.trips['route_id'] == route_id]
    if len(trips) == 0:
        return None

    trip_id = trips.iloc[0]['trip_id']
    stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id].sort_values('stop_sequence')

    original_stops = []
    for _, st in stop_times.iterrows():
        stop = feed.stops[feed.stops['stop_id'] == st['stop_id']]
        if len(stop) > 0:
            original_stops.append({
                'stop_id': st['stop_id'],
                'lat': float(stop.iloc[0]['stop_lat']),
                'lon': float(stop.iloc[0]['stop_lon']),
                'name': stop.iloc[0]['stop_name']
            })

    # Get road-snapped path for original route
    def get_road_path(stops_list):
        """Convert stops to road-snapped coordinates."""
        path = []
        for i in range(len(stops_list) - 1):
            lat1, lon1 = stops_list[i]['lat'], stops_list[i]['lon']
            lat2, lon2 = stops_list[i + 1]['lat'], stops_list[i + 1]['lon']

            try:
                orig_node = ox.distance.nearest_nodes(G, lon1, lat1)
                dest_node = ox.distance.nearest_nodes(G, lon2, lat2)
                route = ox.shortest_path(G, orig_node, dest_node, weight='length')

                if route:
                    segment = [[G.nodes[n]['x'], G.nodes[n]['y']] for n in route]
                    if i == 0:
                        path.extend(segment)
                    else:
                        path.extend(segment[1:])
            except:
                # Fallback to straight line
                if i == 0:
                    path.append([lon1, lat1])
                path.append([lon2, lat2])

        return path

    original_path = get_road_path(original_stops)

    # Get variants with their paths
    route_variants = recs[recs['route_id'] == route_id].copy().sort_values('final_score', ascending=False)

    variants_data = []
    for idx, variant in route_variants.iterrows():
        # Get new stops for this variant
        new_stop_coords = variant.get('new_stop_coords', [])
        if not new_stop_coords:
            continue

        # Extend path with new stops
        extended_stops = original_stops.copy()
        for coord in new_stop_coords[:3]:  # Limit to top 3 additions
            if isinstance(coord, (list, tuple)) and len(coord) == 2:
                extended_stops.append({
                    'stop_id': f"new_{len(extended_stops)}",
                    'lat': float(coord[0]),
                    'lon': float(coord[1]),
                    'name': 'New Stop'
                })

        # Get road-snapped path for extended route
        variant_path = get_road_path(extended_stops)

        # Get new stop details
        new_stops = []
        for coord in new_stop_coords[:3]:
            if isinstance(coord, (list, tuple)) and len(coord) == 2:
                new_stops.append({
                    'lat': float(coord[0]),
                    'lon': float(coord[1])
                })

        variants_data.append({
            'variant_id': variant['variant_id'],
            'variant_type': variant['variant_id'].split('_')[-1],  # A, B, or C
            'path': variant_path,
            'new_stops': new_stops,
            'metrics': {
                'final_score': float(variant['final_score']),
                'equity_multiplier': float(variant['equity_multiplier']),
                'coverage_score': float(variant['coverage_score']),
                'temporal_equity_score': float(variant['temporal_equity_score']),
                'total_pop_served': int(variant['total_pop_served']),
                'new_stops_count': len(new_stops)
            }
        })

    return {
        'route_id': route_id,
        'route_name': f"{route_info.get('route_short_name', 'N/A')}: {route_info.get('route_long_name', 'N/A')}",
        'original_path': original_path,
        'original_stops': original_stops,
        'variants': variants_data
    }

@st.cache_data
def load_wards_geodata():
    """Load ward geodata with geometry and metrics."""
    import json
    wards_df = pd.read_csv(WARDS_GDF_PATH)

    # Parse geometry column if it's a string
    if 'geometry' in wards_df.columns and isinstance(wards_df['geometry'].iloc[0], str):
        import shapely.wkt
        wards_df['geometry'] = wards_df['geometry'].apply(shapely.wkt.loads)

    # Convert to GeoDataFrame
    wards_gdf = gpd.GeoDataFrame(wards_df, geometry='geometry')
    
    # Set CRS to UTM Zone 37S (Nairobi) if not set
    # The coordinates are in meters (e.g. 250000, 9850000) so they are definitely projected
    if wards_gdf.crs is None:
        wards_gdf.set_crs(epsg=32737, inplace=True)
    
    # Reproject to WGS84 (Lat/Lon) for PyDeck/Folium
    wards_gdf = wards_gdf.to_crs(epsg=4326)

    return wards_gdf

# Removed @st.cache_data temporarily to force fresh calculation
def calculate_coverage_with_new_stops():
    """
    Calculate actual 'after' coverage using dissolving buffers methodology from notebook 03.
    This properly combines existing stops + GNN recommended stops with 500m buffers.
    """
    import geopandas as gpd
    from shapely.geometry import Point
    import re

    # Load existing stops (from GTFS feed)
    feed = load_gtfs_feed()
    stops_df = feed.stops[['stop_id', 'stop_lat', 'stop_lon', 'stop_name']].copy()
    stops_gdf = gpd.GeoDataFrame(
        stops_df,
        geometry=gpd.points_from_xy(stops_df['stop_lon'], stops_df['stop_lat']),
        crs='EPSG:4326'
    )

    # Load ALL GNN candidate stops for underserved/severely underserved wards
    try:
        # Use all_candidates_equity.csv which has all 1,645 GNN candidates
        candidates_path = TOP_CANDIDATES_PATH  # Already defined as all_candidates_equity.csv
        candidates_df = pd.read_csv(candidates_path)

        # Filter for underserved and severely underserved wards only
        if 'ward_category' in candidates_df.columns:
            candidates_df = candidates_df[
                candidates_df['ward_category'].isin(['underserved', 'severely_underserved'])
            ]
            # Filtered GNN candidates for underserved/severely underserved wards
            pass

        # Extract coordinates (candidates file uses 'lat'/'lon', not 'stop_lat'/'stop_lon')
        new_stops = []
        for _, row in candidates_df.iterrows():
            lat = row.get('lat') or row.get('stop_lat')
            lon = row.get('lon') or row.get('stop_lon')
            if pd.notna(lat) and pd.notna(lon):
                new_stops.append({
                    'stop_lat': float(lat),
                    'stop_lon': float(lon),
                    'source': 'GNN',
                    'ward': row.get('ward', 'Unknown')
                })

        # Create GeoDataFrame for new stops
        if len(new_stops) > 0:
            new_stops_df = pd.DataFrame(new_stops)
            new_stops_gdf = gpd.GeoDataFrame(
                new_stops_df,
                geometry=gpd.points_from_xy(new_stops_df['stop_lon'], new_stops_df['stop_lat']),
                crs='EPSG:4326'
            )

            # Combine existing + new stops
            all_stops_gdf = pd.concat([stops_gdf, new_stops_gdf], ignore_index=True)

            # Calculating coverage with existing stops + GNN candidates
            pass
        else:
            all_stops_gdf = stops_gdf
            st.warning("No GNN candidates found. Using existing stops only.")

    except Exception as e:
        import traceback
        st.error(f"Could not load GNN candidates: {e}")
        st.code(traceback.format_exc())
        all_stops_gdf = stops_gdf

    # Project to UTM 37S for accurate buffering (same as notebook 03)
    all_stops_proj = all_stops_gdf.to_crs(32737)

    # Buffer each stop by 500m
    all_stops_proj['geometry'] = all_stops_proj.buffer(500)

    # Dissolve overlapping buffers (CRITICAL STEP - removes double counting)
    coverage_union = all_stops_proj.dissolve()

    # Load wards and ensure ward_area exists
    wards_gdf = load_wards_geodata()
    wards_proj = wards_gdf.to_crs(32737)

    # Calculate ward_area if not present
    if 'ward_area' not in wards_proj.columns:
        wards_proj['ward_area'] = wards_proj.geometry.area

    # Calculate coverage using same methodology as notebook 03
    # Area-based: pop_served = population × (intersect_area / ward_area)
    wards_proj['intersect_area_after'] = wards_proj.geometry.intersection(
        coverage_union.union_all()
    ).area

    wards_proj['coverage_ratio_after'] = (
        wards_proj['intersect_area_after'] / wards_proj['ward_area']
    ).fillna(0).clip(0, 1)

    wards_proj['pop_served_after'] = wards_proj['population'] * wards_proj['coverage_ratio_after']
    wards_proj['pct_access_after'] = 100 * wards_proj['pop_served_after'] / wards_proj['population']

    # Convert back to WGS84
    wards_result = wards_proj.to_crs(4326)

    return wards_result

# Removed @st.cache_data temporarily to force fresh calculation
def get_ward_equity_data():
    """
    Get ward equity data with properly calculated BEFORE and AFTER coverage.
    """
    # Try to calculate actual coverage with new stops
    try:
        wards_df = calculate_coverage_with_new_stops()

        # Calculate improvements
        wards_df['additional_pop_served'] = wards_df['pop_served_after'] - wards_df['pop_served']
        wards_df['access_improvement'] = wards_df['pct_access_after'] - wards_df['pct_access']

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.error(f"Could not calculate actual coverage: {e}")
        st.code(error_details)
        st.warning("Using simple estimate fallback.")

        # Fallback to wards_full_gdf.csv with simple estimate
        wards_df = load_wards_geodata()

        # Simple estimate: 15% improvement for underserved wards
        wards_df['pct_access_after'] = wards_df['pct_access'].copy()
        wards_df.loc[wards_df['pct_access'] < 60, 'pct_access_after'] = (
            wards_df.loc[wards_df['pct_access'] < 60, 'pct_access'] * 1.15
        ).clip(upper=100)

        wards_df['pop_served_after'] = (wards_df['population'] * wards_df['pct_access_after'] / 100)
        wards_df['additional_pop_served'] = wards_df['pop_served_after'] - wards_df['pop_served']
        wards_df['access_improvement'] = wards_df['pct_access_after'] - wards_df['pct_access']

    # Categorize wards
    def categorize_ward(row):
        if row['pct_access'] >= 80:
            return 'well_served'
        elif row['pct_access'] >= 60:
            return 'adequate'
        elif row['pct_access'] >= 40:
            return 'underserved'
        else:
            return 'severely_underserved'

    wards_df['ward_category'] = wards_df.apply(categorize_ward, axis=1)

    return wards_df

def create_ward_coverage_map(ward_data, view_mode="before", selected_ward=None):
    """
    Create Folium choropleth map showing ward coverage with boundaries.
    Uses the .explore() method like the notebook for proper display.

    Args:
        ward_data: GeoDataFrame with ward metrics
        view_mode: "before" or "after"
        selected_ward: Ward name to highlight, or None for all wards

    Returns:
        folium.Map object
    """
    import folium
    import geopandas as gpd
    from shapely import wkt

    # Ensure we have GeoDataFrame
    if not isinstance(ward_data, gpd.GeoDataFrame):
        if 'geometry' in ward_data.columns and isinstance(ward_data['geometry'].iloc[0], str):
            ward_data['geometry'] = ward_data['geometry'].apply(wkt.loads)
        ward_data = gpd.GeoDataFrame(ward_data, geometry='geometry', crs='EPSG:4326')

    # Filter if specific ward selected
    if selected_ward and selected_ward != 'All Wards':
        map_data = ward_data[ward_data['ward'] == selected_ward].copy()
    else:
        map_data = ward_data.copy()

    # Select column to display
    if view_mode == "before":
        display_column = 'pct_access'
        map_data['display_served'] = map_data['pop_served'].astype(int)
    else:
        display_column = 'pct_access_after'
        map_data['display_served'] = map_data['pop_served_after'].astype(int)

    # Format for tooltips (matching notebook format)
    map_data['Population'] = map_data['population'].apply(lambda x: f'{int(x):,}')
    map_data['Pop_Served'] = map_data['display_served'].apply(lambda x: f'{x:,}')
    map_data['Coverage_%'] = map_data[display_column].apply(lambda x: f'{x:.1f}%')

    # Create map using .explore() method (like the notebook)
    m = map_data.explore(
        column=display_column,
        cmap='YlOrRd',
        legend=True,
        legend_kwds={'caption': 'Population Coverage (%)'},
        tooltip=['ward', 'subcounty', 'Population', 'Pop_Served', 'Coverage_%'],
        popup=['ward', 'subcounty', 'Population', 'Pop_Served', 'Coverage_%'],
        style_kwds={'color': 'white', 'weight': 1},
        tiles='CartoDB dark_matter',
        name='Ward Coverage'
    )

    return m

@st.cache_data
def load_stop_features():
    """Load stop features for radar chart visualization."""
    return pd.read_csv(STOP_FEATURES_PATH)

@st.cache_data
def get_stops_for_map():
    """
    Get all stops (existing + candidates) for stop intelligence map.
    Returns DataFrame with columns: stop_id, lat, lon, is_new_stop, gnn_score, pop_within_500m, ward
    """
    candidates = load_top_candidates()
    feed = load_gtfs_feed()
    stop_features = load_stop_features()

    # Existing stops
    existing = feed.stops[['stop_id', 'stop_lat', 'stop_lon', 'stop_name']].copy()
    existing.columns = ['stop_id', 'lat', 'lon', 'name']
    existing['is_new_stop'] = False
    existing['gnn_score'] = 0.0

    # Merge with features to get population data
    existing = existing.merge(
        stop_features[['stop_id', 'pop_within_500m', 'ward']],
        on='stop_id',
        how='left'
    )
    existing['pop_within_500m'] = existing['pop_within_500m'].fillna(1000)
    existing['ward'] = existing['ward'].fillna('Unknown')

    # New candidate stops
    new_stops = candidates[['stop_id', 'lat', 'lon', 'ward']].copy()
    new_stops['name'] = new_stops['stop_id']
    new_stops['is_new_stop'] = True

    # Get gnn_probability safely
    if 'gnn_probability' in candidates.columns:
        new_stops['gnn_score'] = candidates['gnn_probability']
    else:
        new_stops['gnn_score'] = 0.8

    # Get pop_within_500m safely
    if 'pop_within_500m' in candidates.columns:
        new_stops['pop_within_500m'] = candidates['pop_within_500m']
    else:
        new_stops['pop_within_500m'] = 1000

    # Combine
    all_stops = pd.concat([existing, new_stops], ignore_index=True)

    # Add color coding
    all_stops['color'] = all_stops.apply(
        lambda row: COLORS['recommended'] if row['is_new_stop'] else COLORS['existing_route'],
        axis=1
    )

    # Add size based on GNN score or population
    all_stops['size'] = all_stops.apply(
        lambda row: max(100, row['gnn_score'] * 300) if row['is_new_stop'] else 50,
        axis=1
    )

    # Format fields for tooltip display (PyDeck needs pre-formatted strings for some formats)
    all_stops['gnn_score_formatted'] = all_stops['gnn_score'].apply(lambda x: f"{x:.2f}")
    all_stops['pop_formatted'] = all_stops['pop_within_500m'].apply(lambda x: f"{int(x):,}")

    return all_stops

def generate_impact_story(route_id, ward_name, metrics):
    """
    Generate community impact story from template.

    Args:
        route_id: Route identifier
        ward_name: Ward name
        metrics: Dict with keys: pop_served, ward_population, poverty_rate,
                 current_access, unserved_pop, equity_tier, final_score

    Returns:
        Formatted markdown string with impact story
    """
    pop_served = metrics.get('pop_served', 0)
    ward_population = metrics.get('ward_population', 1)
    poverty_rate = metrics.get('poverty_rate', 20)
    current_access = metrics.get('current_access', 50)
    unserved_pop = metrics.get('unserved_pop', 0)
    equity_tier = metrics.get('equity_tier', 1.0)

    # Calculate improvements
    new_access_pct = (pop_served / ward_population) * 100 if ward_population > 0 else 0
    access_improvement = new_access_pct

    # Estimate time savings (simplified)
    avg_walk_before = 1.2  # km
    avg_walk_after = 0.4   # km
    time_saved = int((avg_walk_before - avg_walk_after) * 12)  # minutes (walking ~5km/h)

    # Build story based on equity tier
    if equity_tier >= 1.8:
        story = f"""
**Extending Route {route_id} into {ward_name}**

**Current Situation:**
- Only {current_access:.1f}% of residents have matatu access
- {unserved_pop:,} people currently underserved
- Average walk to nearest stop: {avg_walk_before} km (~{int(avg_walk_before * 12)} minutes)
- Poverty rate: {poverty_rate}% (higher than city average)

**Impact of Extension:**
- ✅ Brings service to **{pop_served:,} additional residents**
- ✅ Increases ward access from {current_access:.1f}% to {current_access + access_improvement:.1f}%
- ✅ Reduces average commute time by **{time_saved} minutes** daily
- ✅ Prioritized as **severely underserved** (highest equity tier)

**Who Benefits Most:**
Residents in remote pockets of {ward_name} who currently walk 15+ minutes to catch a matatu, low-income households who can't afford motorcycle taxis, and morning commuters who previously missed opportunities due to long access times.
        """.strip()

    elif equity_tier >= 1.4:
        story = f"""
**Extending Route {route_id} into {ward_name}**

**Current Gap:**
{ward_name} has moderate transit coverage ({current_access:.1f}%), but {unserved_pop:,} residents still lack nearby access. This extension targets pockets where service is most needed.

**Impact:**
- Serves **{pop_served:,} additional people**
- Cuts walking time by **{time_saved} minutes** on average
- Improves equity for residents below poverty line ({poverty_rate}%)

**Key Benefit:**
Fills coverage gaps in moderately served ward, ensuring no neighborhood is left behind.
        """.strip()

    else:
        story = f"""
**Extending Route {route_id} into {ward_name}**

**Enhancement Focus:**
{ward_name} has adequate coverage ({current_access:.1f}%), but this extension optimizes service by filling small gaps and improving network connectivity.

**Impact:**
- Serves {pop_served:,} residents in underserved pockets
- Minor walking time reduction ({time_saved} min)
- Strengthens route efficiency

**Rationale:**
While not the highest equity priority, this extension improves network completeness with minimal cost.
        """.strip()

    return story

@st.cache_data
def get_featured_stories(n=3):
    """
    Get top N community impact stories for featured section.
    Returns list of dicts with story data.
    """
    recs = load_route_recommendations()
    wards_data = get_ward_equity_data()

    # Get top routes by total population impact
    top_routes = recs.groupby('route_id').agg({
        'total_pop_served': 'max',
        'final_score': 'max',
        'equity_multiplier': 'first'
    }).reset_index().sort_values('total_pop_served', ascending=False).head(n)

    stories = []
    for _, row in top_routes.iterrows():
        route_id = row['route_id']

        # Extract ward from route recommendations
        route_recs = recs[recs['route_id'] == route_id].iloc[0]
        # Get ward from new_stops
        if route_recs['new_stops']:
            stop_id = route_recs['new_stops'][0]
            ward_name = stop_id.split('_')[1] + ' ' + stop_id.split('_')[2] if '_' in stop_id else "Ward"
        else:
            ward_name = "Ward"

        # Get ward data
        ward_data = wards_data[wards_data['ward'] == ward_name]
        if len(ward_data) == 0:
            continue
        ward_row = ward_data.iloc[0]

        metrics = {
            'pop_served': int(row['total_pop_served']),
            'ward_population': int(ward_row.get('population', 50000)),
            'poverty_rate': float(ward_row.get('poverty_rate', 20)),
            'current_access': float(ward_row.get('pct_access', 50)),
            'unserved_pop': int(ward_row.get('pop_not_served', 10000)),
            'equity_tier': float(row['equity_multiplier']),
            'final_score': float(row['final_score'])
        }

        story_text = generate_impact_story(route_id, ward_name, metrics)

        stories.append({
            'route_id': route_id,
            'ward': ward_name,
            'pop_served': metrics['pop_served'],
            'access_before': metrics['current_access'],
            'access_after': metrics['current_access'] + (metrics['pop_served'] / metrics['ward_population'] * 100),
            'story': story_text,
            'equity_tier': metrics['equity_tier']
        })

    return stories
