"""
Interactive Folium visualization utilities for transit route analysis.
"""

import folium
import geopandas as gpd
from shapely.geometry import LineString, Point
import osmnx as ox
from folium import LayerControl, FeatureGroup
from folium.plugins import MarkerCluster

# Color scheme
COLORS = {
    'existing_route': '#1A73E8',
    'recommended': '#34A853',
    'alt_1': '#FBBC04',
    'alt_2': '#EA4335',
    'existing_stop': '#5F6368',
    'new_stop_rec': '#34A853'
}
ALT_COLORS = [COLORS['alt_1'], COLORS['alt_2'], '#95A5A6']


def get_road_path_between_stops(G, lat1, lon1, lat2, lon2):
    """Get shortest road path between two stops."""
    try:
        orig_node = ox.distance.nearest_nodes(G, lon1, lat1)
        dest_node = ox.distance.nearest_nodes(G, lon2, lat2)
        route = ox.shortest_path(G, orig_node, dest_node, weight='length')
        coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
        return coords
    except Exception:
        return [(lat1, lon1), (lat2, lon2)]


def route_stops_to_coords(G, stops_df):
    """Convert route stops to road-following coordinates."""
    all_coords = []
    for i in range(len(stops_df) - 1):
        lat1, lon1 = stops_df.iloc[i][['stop_lat', 'stop_lon']]
        lat2, lon2 = stops_df.iloc[i + 1][['stop_lat', 'stop_lon']]
        segment = get_road_path_between_stops(G, lat1, lon1, lat2, lon2)
        if i == 0:
            all_coords.extend(segment)
        else:
            all_coords.extend(segment[1:])
    return all_coords


def extension_coords(G, original_stops, new_stop_coords):
    """Generate coordinates for route extensions."""
    if not new_stop_coords:
        return None
    last_lat, last_lon = original_stops.iloc[-1][['stop_lat', 'stop_lon']]
    ext_coords = []
    for coord in new_stop_coords:
        lat, lon = coord
        seg = get_road_path_between_stops(G, last_lat, last_lon, lat, lon)
        if not ext_coords:
            ext_coords.extend(seg)
        else:
            ext_coords.extend(seg[1:])
        last_lat, last_lon = lat, lon
    return [[c[0], c[1]] for c in ext_coords]


def plot_route_variants_folium(
    route_id, 
    G, 
    route_geometries, 
    variants_df, 
    selected_candidates, 
    feed, 
    df, 
    max_variants_to_plot=3,
    output_path=None
):
    """
    Create interactive map with stats panel for route variants.
    
    Parameters:
    -----------
    route_id : str
        ID of the route to visualize
    G : networkx.MultiDiGraph
        Road network graph from OSMnx
    route_geometries : dict
        Dictionary mapping route_id to stops DataFrame
    variants_df : pd.DataFrame
        DataFrame containing route variants and scores
    selected_candidates : pd.DataFrame
        DataFrame of candidate stops
    feed : gtfs_kit.Feed
        GTFS feed object
    df : pd.DataFrame
        Main stops DataFrame with population data
    max_variants_to_plot : int, default=3
        Maximum number of variants to display
    output_path : str, optional
        Path to save the HTML file. If None, doesn't save.
        
    Returns:
    --------
    folium.Map
        Interactive Folium map object
    """
    
    original_stops = route_geometries[route_id].reset_index(drop=True)
    original_coords = route_stops_to_coords(G, original_stops)
    original_coords_folium = [[c[0], c[1]] for c in original_coords]
    
    route_variants = variants_df[variants_df['route_id'] == route_id].sort_values(
        'final_score', ascending=False
    ).reset_index(drop=True)
    
    top_variant = route_variants.iloc[0]
    top_ext_coords = extension_coords(G, original_stops, top_variant['new_stop_coords'])
    new_top_ids = top_variant['new_stops']
    new_top_df = selected_candidates[selected_candidates['stop_id'].isin(new_top_ids)]
    
    variants_to_plot = route_variants.head(max_variants_to_plot)
    variant_extensions = []
    variant_new_dfs = []
    for _, row in variants_to_plot.iterrows():
        ext_coords = extension_coords(G, original_stops, row['new_stop_coords'])
        variant_extensions.append(ext_coords)
        df_new = selected_candidates[selected_candidates['stop_id'].isin(row['new_stops'])]
        variant_new_dfs.append(df_new)
    
    # Calculate map center
    all_lats = [s['stop_lat'] for s in original_stops.to_dict('records')]
    all_lons = [s['stop_lon'] for s in original_stops.to_dict('records')]
    if top_ext_coords:
        for coord in top_ext_coords:
            all_lats.append(coord[0])
            all_lons.append(coord[1])
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)
    
    # Get route info
    route_info = feed.routes[feed.routes['route_id'] == route_id].iloc[0]
    route_short_name = route_info.get('route_short_name', 'N/A')
    route_long_name = route_info.get('route_long_name', 'N/A')
    
    # Dark mode only
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=13, 
        tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr='&copy; CARTO'

    )
    
    # Existing route (BLUE)
    original_layer = FeatureGroup(name='Existing Route', show=True)
    folium.PolyLine(
        locations=original_coords_folium,
        color=COLORS['existing_route'],
        weight=5,
        opacity=0.85,
        popup=f'<b>Existing Route {route_id}</b><br>{route_short_name}: {route_long_name}<br>Stops: {len(original_stops)}'
    ).add_to(original_layer)
    original_layer.add_to(m)
    
    stops_cluster = MarkerCluster(name='Existing Stops', show=True).add_to(m)
    for idx, stop in original_stops.iterrows():
        folium.CircleMarker(
            location=[stop['stop_lat'], stop['stop_lon']],
            radius=6,
            popup=f"<b>Stop {idx+1}</b><br>ID: {stop['stop_id']}",
            color=COLORS['existing_stop'],
            fill=True,
            fillColor='white',
            fillOpacity=1,
            weight=2
        ).add_to(stops_cluster)
    
    orig_pop = sum(df[df['stop_id']==s]['pop_within_500m'].iloc[0] if len(df[df['stop_id']==s])>0 else 0 for s in original_stops['stop_id'])
    
    # Prepare stats for all variants
    variants_stats = []
    for idx, row in variants_to_plot.iterrows():
        new_pop = row['total_pop_served']
        increase = (new_pop/orig_pop*100) if orig_pop > 0 else 0
        variants_stats.append({
            'id': row['variant_id'],
            'score': row['final_score'],
            'new_stops': len(row['new_stops']),
            'equity': row['equity_multiplier'],
            'coverage': row['coverage_score'],
            'temporal': row['temporal_equity_score'],
            'orig_pop': orig_pop,
            'new_pop': new_pop,
            'total_pop': orig_pop + new_pop,
            'increase': increase
        })
    
    # JavaScript for interactive stats panel (dark mode only)
    stats_js = f"""
    <script>
    var variantStats = {variants_stats};
    
    function updateStats(index) {{
        var stats = variantStats[index];
        var color = index === 0 ? '{COLORS["recommended"]}' : (index === 1 ? '{COLORS["alt_1"]}' : '{COLORS["alt_2"]}');
        
        document.getElementById('variant-name').innerHTML = stats.id;
        document.getElementById('variant-name').style.color = color;
        document.getElementById('stat-score').innerHTML = stats.score.toFixed(3);
        document.getElementById('stat-stops').innerHTML = stats.new_stops;
        document.getElementById('stat-equity').innerHTML = stats.equity.toFixed(2) + 'x';
        document.getElementById('stat-coverage').innerHTML = stats.coverage.toFixed(3);
        document.getElementById('stat-temporal').innerHTML = stats.temporal.toFixed(3);
        document.getElementById('stat-orig-pop').innerHTML = stats.orig_pop.toLocaleString();
        document.getElementById('stat-new-pop').innerHTML = '+' + stats.new_pop.toLocaleString();
        document.getElementById('stat-new-pop').style.color = color;
        document.getElementById('stat-total-pop').innerHTML = stats.total_pop.toLocaleString();
        document.getElementById('stat-increase').innerHTML = '+' + stats.increase.toFixed(0) + '% Coverage';
        document.getElementById('stat-increase').style.background = color;
    }}
    
    function applyDarkMode() {{
        var layerControl = document.querySelector('.leaflet-control-layers');
        if (layerControl) {{
            layerControl.style.background = '#1e1e1e';
            layerControl.style.color = '#e0e0e0';
            layerControl.style.border = '2px solid #3a3a3a';
        }}
        
        var layerLabels = document.querySelectorAll('.leaflet-control-layers-list label');
        layerLabels.forEach(function(label) {{
            label.style.color = '#e0e0e0';
        }});
        
        var separators = document.querySelectorAll('.leaflet-control-layers-separator');
        separators.forEach(function(sep) {{
            sep.style.borderTop = '1px solid #3a3a3a';
        }});
    }}
    
    // Aggressive dark mode application using MutationObserver
    var observer = new MutationObserver(function(mutations) {{
        applyDarkMode();
    }});
    
    // Initialize
    document.addEventListener('DOMContentLoaded', function() {{
        updateStats(0);
        
        // Start observing for layer control creation
        observer.observe(document.body, {{
            childList: true,
            subtree: true
        }});
        
        // Apply dark mode immediately and repeatedly
        applyDarkMode();
        setTimeout(applyDarkMode, 50);
        setTimeout(applyDarkMode, 100);
        setTimeout(applyDarkMode, 200);
        setTimeout(applyDarkMode, 500);
        setTimeout(applyDarkMode, 1000);
        setTimeout(applyDarkMode, 2000);
        
        // Stop observing after 3 seconds
        setTimeout(function() {{
            observer.disconnect();
        }}, 3000);
    }});
    
    // Backup: apply on window load
    window.onload = function() {{
        updateStats(0);
        applyDarkMode();
        setTimeout(applyDarkMode, 100);
        setTimeout(applyDarkMode, 500);
    }};
    </script>
    """
    
    # Recommended extension (GREEN) - clickable to update stats
    rec_layer = FeatureGroup(name='Recommended Extension', show=True)
    if top_ext_coords:
        folium.PolyLine(
            locations=top_ext_coords,
            color=COLORS['recommended'],
            weight=6,
            opacity=0.9,
            popup=f"<button onclick='updateStats(0)' style='padding:8px 16px;background:{COLORS['recommended']};color:white;border:none;border-radius:4px;cursor:pointer;font-weight:600;'>View Stats</button>",
            tooltip="Click to view stats"
        ).add_to(rec_layer)
    
    for idx, stop in new_top_df.iterrows():
        folium.Marker(
            location=[stop['lat'], stop['lon']],
            popup=f"<b>New Stop</b><br>ID: {stop['stop_id']}<br>Quality: {stop['gnn_probability']:.1%}<br>Pop: {int(stop['pop_within_500m']):,}",
            icon=folium.Icon(color='green', icon='plus', prefix='fa')
        ).add_to(rec_layer)
    
    rec_layer.add_to(m)
    
    # Alternative variants - clickable to update stats
    for i, (ext_coords, df_new, (idx, row)) in enumerate(zip(variant_extensions, variant_new_dfs, variants_to_plot.iterrows())):
        if i == 0:
            continue
            
        alt_layer = FeatureGroup(name=f'Alternative {i}: {row["variant_id"]}', show=False)
        color_alt = ALT_COLORS[(i-1) % len(ALT_COLORS)]
        
        if ext_coords:
            folium.PolyLine(
                locations=ext_coords,
                color=color_alt,
                weight=5,
                opacity=0.7,
                dashArray='8, 4',
                popup=f"<button onclick='updateStats({i})' style='padding:8px 16px;background:{color_alt};color:white;border:none;border-radius:4px;cursor:pointer;font-weight:600;'>View Stats</button>",
                tooltip=f"Click to view {row['variant_id']} stats"
            ).add_to(alt_layer)
        
        for _, stop in df_new.iterrows():
            folium.CircleMarker(
                location=[stop['lat'], stop['lon']],
                radius=7,
                popup=f"<b>Alt Stop</b><br>ID: {stop['stop_id']}<br>Quality: {stop['gnn_probability']:.1%}",
                color=color_alt,
                fill=True,
                fillOpacity=0.85,
                weight=2
            ).add_to(alt_layer)
        
        alt_layer.add_to(m)
    
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # ULTRA AGGRESSIVE CSS - Force dark mode on everything
    layer_control_css = """
    <style>
    /* Force dark backgrounds on everything */
    .leaflet-control-layers,
    .leaflet-control-layers-expanded {
        background: #1e1e1e !important;
        color: #e0e0e0 !important;
        border: 2px solid #3a3a3a !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
        padding: 10px !important;
    }
    
    .leaflet-control-layers-base,
    .leaflet-control-layers-overlays {
        color: #e0e0e0 !important;
    }
    
    .leaflet-control-layers-base label,
    .leaflet-control-layers-overlays label,
    .leaflet-control-layers label {
        color: #e0e0e0 !important;
        font-weight: 500 !important;
    }
    
    .leaflet-control-layers-separator {
        border-top: 1px solid #3a3a3a !important;
        margin: 8px 0 !important;
    }
    
    .leaflet-control-layers-toggle {
        background-color: #1e1e1e !important;
        border: 2px solid #3a3a3a !important;
        background-image: none !important;
    }
    
    .leaflet-control-layers-list {
        color: #e0e0e0 !important;
    }
    
    /* Make checkboxes and radio buttons visible in dark mode */
    .leaflet-control-layers input[type="radio"],
    .leaflet-control-layers input[type="checkbox"] {
        filter: invert(1) hue-rotate(180deg) !important;
        margin-right: 5px !important;
    }
    
    /* Hover effects */
    .leaflet-control-layers label:hover {
        background: #2a2a2a !important;
    }
    </style>
    """
    
    m.get_root().html.add_child(folium.Element(layer_control_css))
    
    # ROUTE HEADER (dark mode only)
    route_header = f'''
    <div class="panel-dark" style="position: fixed; top: 20px; left: 20px; width: 380px;
                background: #1e1e1e; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                padding: 16px; font-family: 'Segoe UI', Roboto, Arial; z-index: 9999;">
        
        <div style="margin-bottom: 12px;">
            <div class="sub-text" style="font-size: 10px; color: #999; text-transform: uppercase; 
                       letter-spacing: 0.8px; margin-bottom: 4px;">
                ROUTE {route_id} • {route_short_name}
            </div>
            <div style="font-size: 18px; font-weight: 700; color: #e0e0e0; line-height: 1.3;">
                {route_long_name}
            </div>
        </div>
        
        <div class="panel-border" style="border-top: 1px solid #3a3a3a; padding-top: 12px;">
            <div class="sub-text" style="font-size: 11px; color: #999; margin-bottom: 6px;">Current Extension</div>
            <div id="variant-name" style="font-size: 15px; font-weight: 600; color: {COLORS['recommended']};">
                {top_variant['variant_id']}
            </div>
        </div>
    </div>
    '''
    
    # STATS PANEL - Updates when clicking routes
    stats_panel = f'''
    <div class="panel-dark" style="position: fixed; top: 140px; left: 20px; width: 380px;
                background: #1e1e1e; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                font-family: 'Segoe UI', Roboto, Arial; font-size: 13px; z-index: 9999;">
        
        <div style="padding: 16px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
                <div class="stat-card" style="background: #2a2a2a; padding: 12px; border-radius: 6px; text-align: center;">
                    <div class="sub-text" style="font-size: 10px; color: #999; margin-bottom: 4px;">EXISTING</div>
                    <div style="font-size: 24px; font-weight: 700; color: {COLORS['existing_route']};">{len(original_stops)}</div>
                    <div class="sub-text" style="font-size: 10px; color: #999;">stops</div>
                </div>
                <div class="stat-card" style="background: #2a2a2a; padding: 12px; border-radius: 6px; text-align: center;">
                    <div class="sub-text" style="font-size: 10px; color: #999; margin-bottom: 4px;">ADDING</div>
                    <div id="stat-stops" style="font-size: 24px; font-weight: 700; color: {COLORS['recommended']};">{len(top_variant['new_stops'])}</div>
                    <div class="sub-text" style="font-size: 10px; color: #999;">stops</div>
                </div>
            </div>
            
            <div class="stat-card" style="background: #2a2a2a; padding: 12px; border-radius: 6px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin: 6px 0;">
                    <span class="sub-text" style="color: #999;">Score</span>
                    <span id="stat-score" style="font-weight: 700; color: #e0e0e0;">{top_variant['final_score']:.3f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 6px 0;">
                    <span class="sub-text" style="color: #999;">Equity</span>
                    <span id="stat-equity" style="font-weight: 700; color: #e0e0e0;">{top_variant['equity_multiplier']:.2f}x</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 6px 0;">
                    <span class="sub-text" style="color: #999;">Coverage</span>
                    <span id="stat-coverage" style="font-weight: 600; color: #e0e0e0;">{top_variant['coverage_score']:.3f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 6px 0;">
                    <span class="sub-text" style="color: #999;">Temporal</span>
                    <span id="stat-temporal" style="font-weight: 600; color: #e0e0e0;">{top_variant['temporal_equity_score']:.3f}</span>
                </div>
            </div>
            
            <div class="stat-card" style="background: #2a2a2a; padding: 12px; border-radius: 6px; margin-bottom: 12px;">
                <div class="sub-text" style="font-size: 11px; color: #999; margin-bottom: 8px; font-weight: 600;">Population Coverage</div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin: 6px 0; color: #e0e0e0;">
                    <span>Existing</span>
                    <span id="stat-orig-pop">{orig_pop:,.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin: 6px 0;">
                    <span style="color: #e0e0e0;">Adding</span>
                    <span id="stat-new-pop" style="font-weight: 700; color: {COLORS['recommended']};">+{variants_stats[0]['new_pop']:,.0f}</span>
                </div>
                <div class="panel-border" style="border-top: 1px solid #3a3a3a; padding-top: 8px; margin-top: 8px;
                           display: flex; justify-content: space-between; font-weight: 700; color: #e0e0e0;">
                    <span>Total</span>
                    <span id="stat-total-pop">{orig_pop + variants_stats[0]['new_pop']:,.0f}</span>
                </div>
            </div>
            
            <div id="stat-increase" style="background: {COLORS['recommended']}; color: white; 
                       padding: 12px; border-radius: 6px; text-align: center; font-weight: 700; font-size: 14px;">
                +{variants_stats[0]['increase']:.0f}% Coverage
            </div>
            
            <div class="sub-text" style="margin-top: 12px; font-size: 10px; color: #666; text-align: center; font-style: italic;">
                💡 Click route lines to compare variants
            </div>
        </div>
    </div>
    {stats_js}
    '''
    
    m.get_root().html.add_child(folium.Element(route_header))
    m.get_root().html.add_child(folium.Element(stats_panel))
    
    # Legend
    legend_html = f'''
    <div class="panel-dark" style="position: fixed; bottom: 20px; right: 20px; width: 220px;
                background: #1e1e1e; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                padding: 14px; font-family: 'Segoe UI', Roboto, Arial; font-size: 12px; z-index: 9999;">
        <div style="font-weight: 600; margin-bottom: 10px; color: #e0e0e0;">Legend</div>
        <div style="display: flex; align-items: center; margin: 8px 0;">
            <div style="width: 28px; height: 3px; background: {COLORS['existing_route']}; margin-right: 10px;"></div>
            <span style="color: #e0e0e0;">Existing</span>
        </div>
        <div style="display: flex; align-items: center; margin: 8px 0;">
            <div style="width: 28px; height: 4px; background: {COLORS['recommended']}; margin-right: 10px;"></div>
            <span style="color: #e0e0e0; font-weight: 600;">Recommended</span>
        </div>
        <div style="display: flex; align-items: center; margin: 8px 0;">
            <div style="width: 28px; height: 3px; background: {COLORS['alt_1']}; margin-right: 10px; opacity: 0.7;"></div>
            <span style="color: #e0e0e0;">Alternatives</span>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    if output_path:
        m.save(output_path)
        print(f"Map saved to: {output_path}")
    
    return m


# ============================================================================
# WRAPPER FUNCTION - USE THIS FOR QUICK VISUALIZATION
# ============================================================================

def quick_viz(route_id, data_dict, save=True, output_dir='/home/dataopske/Desktop/jav/data/folium'):
    """
    Quick visualization with sensible defaults.
    
    Parameters:
    -----------
    route_id : str
        Route to visualize
    data_dict : dict
        Dictionary with keys: 'G', 'route_geometries', 'variants_df', 
        'selected_candidates', 'feed', 'df'
    save : bool, default=True
        Whether to save the HTML file
    output_dir : str, default='/home/dataopske/Desktop/jav/data/folium'
        Directory to save the HTML file
        
    Returns:
    --------
    folium.Map
        Interactive Folium map object
        
    Example:
    --------
    >>> from utils.viz_utils import quick_viz
    >>> viz_data = {
    ...     'G': G,
    ...     'route_geometries': route_geometries,
    ...     'variants_df': variants_df,
    ...     'selected_candidates': selected_candidates,
    ...     'feed': feed,
    ...     'df': df
    ... }
    >>> m = quick_viz('route_123', viz_data)
    """
    output_path = None
    if save:
        output_path = f'{output_dir}/route_{route_id}_interactive.html'
    
    return plot_route_variants_folium(
        route_id=route_id,
        output_path=output_path,
        **data_dict
    )