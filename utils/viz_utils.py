"""
Interactive Folium visualization utilities for transit route analysis.
"""

import folium
import geopandas as gpd
from shapely.geometry import LineString, Point
import osmnx as ox
from folium import LayerControl, FeatureGroup
from folium.plugins import MarkerCluster
import json

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
    
    import ast

    top_variant = route_variants.iloc[0]
    top_ext_coords = extension_coords(G, original_stops, top_variant['new_stop_coords'])
    # Parse new_stops from string to list
    new_top_ids = ast.literal_eval(top_variant['new_stops']) if isinstance(top_variant['new_stops'], str) else top_variant['new_stops']
    new_top_df = selected_candidates[selected_candidates['stop_id'].isin(new_top_ids)]

    variants_to_plot = route_variants.head(max_variants_to_plot)
    variant_extensions = []
    variant_new_dfs = []
    for _, row in variants_to_plot.iterrows():
        ext_coords = extension_coords(G, original_stops, row['new_stop_coords'])
        variant_extensions.append(ext_coords)
        # Parse new_stops from string to list
        new_stops_list = ast.literal_eval(row['new_stops']) if isinstance(row['new_stops'], str) else row['new_stops']
        df_new = selected_candidates[selected_candidates['stop_id'].isin(new_stops_list)]
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
    
    # Calculate original population served by existing stops
    # Sum pop_within_500m for all existing stops on this route
    orig_pop = 0
    for stop_id in original_stops['stop_id']:
        stop_data = df[df['stop_id'] == stop_id]
        if len(stop_data) > 0:
            orig_pop += stop_data.iloc[0]['pop_within_500m']

    # Prepare stats for all variants
    # NOTE: total_pop_served in variants_df is the ADDITIONAL population from new stops
    variants_stats = []
    for idx, row in variants_to_plot.iterrows():
        new_pop = row['total_pop_served']  # Additional population from new stops
        total_pop = orig_pop + new_pop  # Total = existing + new
        increase = (new_pop/orig_pop*100) if orig_pop > 0 else 0

        # Parse new_stops to get actual count
        new_stops_parsed = ast.literal_eval(row['new_stops']) if isinstance(row['new_stops'], str) else row['new_stops']

        variants_stats.append({
            'id': str(row['variant_id']),
            'score': float(row['final_score']),
            'new_stops': int(len(new_stops_parsed)),
            'equity': float(row['equity_multiplier']),
            'coverage': float(row['coverage_score']),
            'temporal': float(row['temporal_equity_score']),
            'orig_pop': int(orig_pop),
            'new_pop': int(new_pop),
            'total_pop': int(total_pop),
            'increase': float(increase)
        })

    # JavaScript for interactive stats panel (dark mode only)
    stats_js = f"""
    <script>
    var variantStats = {json.dumps(variants_stats)};
    
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
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Arial; padding: 8px; min-width: 150px;">
            <div style="font-weight: 700; color: {COLORS['recommended']}; font-size: 13px; margin-bottom: 8px;">
                Variant A (Recommended)
            </div>
            <div style="font-size: 11px; color: #666; margin-bottom: 10px;">
                Click route to view stats →
            </div>
            <div style="font-size: 10px; color: #999;">
                Score: {top_variant['final_score']:.3f}<br>
                Stops: {len(top_variant['new_stops'])}<br>
                Pop: +{variants_stats[0]['new_pop']:,.0f}
            </div>
        </div>
        """
        folium.PolyLine(
            locations=top_ext_coords,
            color=COLORS['recommended'],
            weight=6,
            opacity=0.9,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip="<b>Variant A (Recommended)</b><br>Click line to view stats"
        ).add_to(rec_layer)
    
    # Add new stops markers for recommended variant - USE ACTUAL MARKER PINS (RED)
    for idx, stop in new_top_df.iterrows():
        # Add 500m buffer circle to show catchment area
        folium.Circle(
            location=[stop['lat'], stop['lon']],
            radius=500,  # 500 meters
            color='#46CC71',  # Green border
            weight=1,  # Thin border
            fill=True,
            fillColor='#46CC71',  # Green fill
            fillOpacity=0.1,  # Very transparent so it doesn't overwhelm
            popup=f"<b>500m Catchment Area</b><br>Population: {int(stop['pop_within_500m']):,}",
            tooltip="500m service radius"
        ).add_to(rec_layer)

        # Create detailed popup content matching the format
        # Format quality - use more precision for very small values
        quality_pct = stop['gnn_probability'] * 100
        if quality_pct < 0.1 and quality_pct > 0:
            quality_str = f"{quality_pct:.3f}%"
        else:
            quality_str = f"{quality_pct:.1f}%"

        popup_content = f"""
        <div style="font-family: Arial, sans-serif; min-width: 220px;">
            <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #E74C3C;">
                New Stop (Recommended)
            </div>
            <div style="font-size: 12px; line-height: 1.6;">
                <b>ID:</b> {stop['stop_id']}<br>
                <b>GNN Quality:</b> {quality_str}<br>
                <b>Pop:</b> {int(stop['pop_within_500m']):,}
            </div>
            <div style="font-size: 10px; color: #666; margin-top: 6px; font-style: italic;">
                Selected based on overall equity & coverage
            </div>
        </div>
        """

        # Use Folium Marker with RED icon for pin-like appearance
        folium.Marker(
            location=[stop['lat'], stop['lon']],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=f"<b>New Stop</b><br>ID: {stop['stop_id']}<br>GNN Quality: {quality_str}<br>Pop: {int(stop['pop_within_500m']):,}",
            icon=folium.Icon(
                color='red',
                icon='plus',
                prefix='fa'
            )
        ).add_to(rec_layer)

    rec_layer.add_to(m)
    
    # Alternative variants - clickable to update stats
    for i, (ext_coords, df_new, (idx, row)) in enumerate(zip(variant_extensions, variant_new_dfs, variants_to_plot.iterrows())):
        if i == 0:
            continue

        alt_layer = FeatureGroup(name=f'Alternative {i}: {row["variant_id"]}', show=False)
        color_alt = ALT_COLORS[(i-1) % len(ALT_COLORS)]

        if ext_coords:
            popup_html = f"""
            <div style="font-family: 'Segoe UI', Arial; padding: 8px; min-width: 150px;">
                <div style="font-weight: 700; color: {color_alt}; font-size: 13px; margin-bottom: 8px;">
                    Variant {row['variant_id'].split('_')[-1]}
                </div>
                <div style="font-size: 11px; color: #666; margin-bottom: 10px;">
                    Click route to view stats →
                </div>
                <div style="font-size: 10px; color: #999;">
                    Score: {row['final_score']:.3f}<br>
                    Stops: {len(row['new_stops'])}<br>
                    Pop: +{variants_stats[i]['new_pop']:,.0f}
                </div>
            </div>
            """
            folium.PolyLine(
                locations=ext_coords,
                color=color_alt,
                weight=5,
                opacity=0.7,
                dashArray='8, 4',
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=f"<b>Variant {row['variant_id'].split('_')[-1]}</b><br>Click line to view stats"
            ).add_to(alt_layer)
        
        # Add marker pins for alternative variant stops
        icon_color_map = {COLORS['alt_1']: 'orange', COLORS['alt_2']: 'purple'}
        icon_color = icon_color_map.get(color_alt, 'orange')

        for _, stop in df_new.iterrows():
            # Add 500m buffer circle to show catchment area
            folium.Circle(
                location=[stop['lat'], stop['lon']],
                radius=500,  # 500 meters
                color='#46CC71',  # Green border
                weight=1,  # Thin border
                fill=True,
                fillColor='#46CC71',  # Green fill
                fillOpacity=0.1,  # Very transparent
                popup=f"<b>500m Catchment Area</b><br>Population: {int(stop['pop_within_500m']):,}",
                tooltip="500m service radius"
            ).add_to(alt_layer)

            # Create detailed popup content matching the format
            # Format quality - use more precision for very small values
            alt_quality_pct = stop['gnn_probability'] * 100
            if alt_quality_pct < 0.1 and alt_quality_pct > 0:
                alt_quality_str = f"{alt_quality_pct:.3f}%"
            else:
                alt_quality_str = f"{alt_quality_pct:.1f}%"

            alt_popup_content = f"""
            <div style="font-family: Arial, sans-serif; min-width: 220px;">
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: {color_alt};">
                    New Stop (Alt {row['variant_id'].split('_')[-1]})
                </div>
                <div style="font-size: 12px; line-height: 1.6;">
                    <b>ID:</b> {stop['stop_id']}<br>
                    <b>GNN Quality:</b> {alt_quality_str}<br>
                    <b>Pop:</b> {int(stop['pop_within_500m']):,}
                </div>
                <div style="font-size: 10px; color: #666; margin-top: 6px; font-style: italic;">
                    Selected based on overall equity & coverage
                </div>
            </div>
            """

            # Use Folium Marker with icon
            folium.Marker(
                location=[stop['lat'], stop['lon']],
                popup=folium.Popup(alt_popup_content, max_width=250),
                tooltip=f"<b>New Stop</b><br>ID: {stop['stop_id']}<br>GNN Quality: {alt_quality_str}<br>Pop: {int(stop['pop_within_500m']):,}",
                icon=folium.Icon(
                    color=icon_color,
                    icon='plus',
                    prefix='fa'
                )
            ).add_to(alt_layer)
        
        alt_layer.add_to(m)
    
    folium.LayerControl(position='topright', collapsed=False).add_to(m)

    # Add click handlers to all polylines
    click_handlers_js = f"""
    <script>
    // Wait for map to be ready
    setTimeout(function() {{
        // Get all polylines on the map
        var allLayers = [];

        // Function to find all polylines recursively
        function findPolylines(layer) {{
            if (layer instanceof L.Polyline && !(layer instanceof L.Polygon)) {{
                allLayers.push(layer);
            }}
            if (layer.getLayers) {{
                layer.getLayers().forEach(findPolylines);
            }}
        }}

        // Find all polylines
        if (typeof map_{m._id} !== 'undefined') {{
            map_{m._id}.eachLayer(findPolylines);

            // Assign click handlers based on color
            allLayers.forEach(function(polyline, index) {{
                var color = polyline.options.color;

                // Determine variant index based on color
                var variantIndex = -1;
                if (color === '{COLORS['recommended']}') {{
                    variantIndex = 0;  // Variant A
                }} else if (color === '{COLORS['alt_1']}') {{
                    variantIndex = 1;  // Variant B
                }} else if (color === '{COLORS['alt_2']}') {{
                    variantIndex = 2;  // Variant C
                }}

                // Add click event only for variant polylines (not existing route)
                if (variantIndex >= 0) {{
                    polyline.on('click', function(e) {{
                        L.DomEvent.stopPropagation(e);
                        if (typeof updateStats === 'function') {{
                            updateStats(variantIndex);
                        }}
                    }});

                    // Add cursor pointer style
                    polyline.on('mouseover', function() {{
                        this._path.style.cursor = 'pointer';
                    }});
                }}
            }});
        }}
    }}, 500);
    </script>
    """
    m.get_root().html.add_child(folium.Element(click_handlers_js))
    
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
    
    # ROUTE HEADER (dark mode only) - INCREASED BY 1/3
    route_header = f'''
    <div class="panel-dark" style="position: fixed; top: 20px; left: 20px; width: 253px;
                background: #1e1e1e; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                padding: 12px; font-family: 'Segoe UI', Roboto, Arial; font-size: 12px; z-index: 9999;">

        <div style="margin-bottom: 8px;">
            <div class="sub-text" style="font-size: 9px; color: #999; text-transform: uppercase;
                       letter-spacing: 0.5px; margin-bottom: 3px;">
                {route_short_name}
            </div>
            <div style="font-size: 14px; font-weight: 700; color: #e0e0e0; line-height: 1.2;">
                {route_long_name[:35]}{'...' if len(route_long_name) > 35 else ''}
            </div>
        </div>

        <div class="panel-border" style="border-top: 1px solid #3a3a3a; padding-top: 8px;">
            <div class="sub-text" style="font-size: 9px; color: #999; margin-bottom: 3px;">Current</div>
            <div id="variant-name" style="font-size: 12px; font-weight: 600; color: {COLORS['recommended']};">
                Variant {top_variant['variant_id'].split('_')[-1]}
            </div>
        </div>
    </div>
    '''
    
    # STATS PANEL - Updates when clicking routes - INCREASED BY 1/3
    stats_panel = f'''
    <div class="panel-dark" style="position: fixed; top: 100px; left: 20px; width: 253px;
                background: #1e1e1e; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                font-family: 'Segoe UI', Roboto, Arial; font-size: 11px; z-index: 9999;">

        <div style="padding: 10px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px;">
                <div class="stat-card" style="background: #2a2a2a; padding: 8px; border-radius: 4px; text-align: center;">
                    <div class="sub-text" style="font-size: 8px; color: #999; margin-bottom: 3px;">EXISTING</div>
                    <div style="font-size: 18px; font-weight: 700; color: {COLORS['existing_route']};">{len(original_stops)}</div>
                    <div class="sub-text" style="font-size: 8px; color: #999;">stops</div>
                </div>
                <div class="stat-card" style="background: #2a2a2a; padding: 8px; border-radius: 4px; text-align: center;">
                    <div class="sub-text" style="font-size: 8px; color: #999; margin-bottom: 3px;">ADDING</div>
                    <div id="stat-stops" style="font-size: 18px; font-weight: 700; color: {COLORS['recommended']};">{len(top_variant['new_stops'])}</div>
                    <div class="sub-text" style="font-size: 8px; color: #999;">stops</div>
                </div>
            </div>

            <div class="stat-card" style="background: #2a2a2a; padding: 8px; border-radius: 4px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; margin: 4px 0; font-size: 10px;">
                    <span class="sub-text" style="color: #999;">Score</span>
                    <span id="stat-score" style="font-weight: 700; color: #e0e0e0;">{top_variant['final_score']:.3f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 4px 0; font-size: 10px;">
                    <span class="sub-text" style="color: #999;">Equity</span>
                    <span id="stat-equity" style="font-weight: 700; color: #e0e0e0;">{top_variant['equity_multiplier']:.2f}x</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 4px 0; font-size: 10px;">
                    <span class="sub-text" style="color: #999;">Coverage</span>
                    <span id="stat-coverage" style="font-weight: 600; color: #e0e0e0;">{top_variant['coverage_score']:.3f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 4px 0; font-size: 10px;">
                    <span class="sub-text" style="color: #999;">Temporal</span>
                    <span id="stat-temporal" style="font-weight: 600; color: #e0e0e0;">{top_variant['temporal_equity_score']:.3f}</span>
                </div>
            </div>

            <div class="stat-card" style="background: #2a2a2a; padding: 8px; border-radius: 4px; margin-bottom: 8px;">
                <div class="sub-text" style="font-size: 10px; color: #999; margin-bottom: 5px; font-weight: 600;">Pop. Coverage</div>
                <div style="display: flex; justify-content: space-between; font-size: 10px; margin: 4px 0; color: #e0e0e0;">
                    <span>Existing</span>
                    <span id="stat-orig-pop">{orig_pop:,.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 10px; margin: 4px 0;">
                    <span style="color: #e0e0e0;">Adding</span>
                    <span id="stat-new-pop" style="font-weight: 700; color: {COLORS['recommended']};">+{variants_stats[0]['new_pop']:,.0f}</span>
                </div>
                <div class="panel-border" style="border-top: 1px solid #3a3a3a; padding-top: 5px; margin-top: 5px;
                           display: flex; justify-content: space-between; font-weight: 700; color: #e0e0e0; font-size: 10px;">
                    <span>Total</span>
                    <span id="stat-total-pop">{orig_pop + variants_stats[0]['new_pop']:,.0f}</span>
                </div>
            </div>

            <div id="stat-increase" style="background: {COLORS['recommended']}; color: white;
                       padding: 8px; border-radius: 4px; text-align: center; font-weight: 700; font-size: 11px;">
                +{variants_stats[0]['increase']:.0f}% Coverage
            </div>

            <div class="sub-text" style="margin-top: 8px; font-size: 8px; color: #666; text-align: center; font-style: italic;">
                💡 Click routes to compare
            </div>
        </div>
    </div>
    {stats_js}
    '''
    
    m.get_root().html.add_child(folium.Element(route_header))
    m.get_root().html.add_child(folium.Element(stats_panel))
    
    # Legend - REDUCED BY 1/2
    legend_html = f'''
    <div class="panel-dark" style="position: fixed; bottom: 20px; right: 20px; width: 55px;
                background: #1e1e1e; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                padding: 4px; font-family: 'Segoe UI', Roboto, Arial; font-size: 7px; z-index: 9999;">
        <div style="font-weight: 600; margin-bottom: 3px; color: #e0e0e0; font-size: 8px; text-align: center;">Legend</div>
        <div style="display: flex; flex-direction: column; gap: 2px;">
            <div style="display: flex; align-items: center;">
                <div style="width: 10px; height: 2px; background: {COLORS['existing_route']}; margin-right: 3px;"></div>
                <span style="color: #e0e0e0; font-size: 6px;">Exist</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 10px; height: 2px; background: {COLORS['recommended']}; margin-right: 3px;"></div>
                <span style="color: #e0e0e0; font-weight: 600; font-size: 6px;">Rec</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 10px; height: 2px; background: {COLORS['alt_1']}; margin-right: 3px; opacity: 0.7;"></div>
                <span style="color: #e0e0e0; font-size: 6px;">Alt</span>
            </div>
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

def quick_viz(route_id, data_dict, save=True, output_dir='data/folium'):
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
    output_dir : str, default='data/folium'
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