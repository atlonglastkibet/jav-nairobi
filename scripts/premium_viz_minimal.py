import folium
from folium import plugins
import numpy as np
import osmnx as ox

# Blue for existing, Green for extensions - harmonious!
COLORS = {
    'existing': '#1A73E8',      # Google Blue
    'extension': '#34A853',     # Google Green
    'alt1': '#FBBC04',          # Yellow
    'alt2': '#EA4335',          # Red
    'stop_existing': '#5F6368', # Gray
    'stop_new': '#34A853'       # Green
}

def get_road_path(G, lat1, lon1, lat2, lon2):
    """Snap to roads - no more straight lines!"""
    try:
        orig = ox.distance.nearest_nodes(G, lon1, lat1)
        dest = ox.distance.nearest_nodes(G, lon2, lat2)
        route = ox.shortest_path(G, orig, dest, weight='length')
        if route:
            return [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
    except:
        pass
    return [[lat1, lon1], [lat2, lon2]]

def build_route_path(G, stops_df):
    """Build complete road-snapped path through stops"""
    path = []
    for i in range(len(stops_df) - 1):
        lat1, lon1 = stops_df.iloc[i][['stop_lat', 'stop_lon']]
        lat2, lon2 = stops_df.iloc[i+1][['stop_lat', 'stop_lon']]
        segment = get_road_path(G, lat1, lon1, lat2, lon2)
        if i == 0:
            path.extend(segment)
        else:
            path.extend(segment[1:])
    return path

def build_extension_path(G, last_coords, new_coords):
    """Build road-snapped extension"""
    path = []
    last_lat, last_lon = last_coords
    for coord in new_coords:
        segment = get_road_path(G, last_lat, last_lon, coord[0], coord[1])
        if not path:
            path.extend(segment)
        else:
            path.extend(segment[1:])
        last_lat, last_lon = coord[0], coord[1]
    return path

def create_viz(route_id, variants_df, route_geometries, selected_candidates, feed, G, df):
    """Create premium viz with road snapping"""
    
    route_variants = variants_df[variants_df['route_id'] == route_id].sort_values('final_score', ascending=False)
    if len(route_variants) == 0:
        return None
    
    original = route_geometries[route_id]
    center = [original['stop_lat'].mean(), original['stop_lon'].mean()]
    
    m = folium.Map(center, zoom_start=13, tiles='cartodbpositron', prefer_canvas=True)
    folium.TileLayer('cartodbdark_matter', name='Dark Mode').add_to(m)
    folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Satellite').add_to(m)
    
    print("Snapping to roads...")
    
    # Build existing route - ROAD SNAPPED
    existing_path = build_route_path(G, original)
    
    # EXISTING ROUTE (Blue)
    ex_route = folium.FeatureGroup(name='Existing Route', show=True)
    ex_stops = folium.FeatureGroup(name='Existing Stops', show=True)
    ex_labels = folium.FeatureGroup(name='Existing Labels', show=False)
    
    folium.PolyLine(existing_path, color=COLORS['existing'], weight=5, opacity=0.85).add_to(ex_route)
    
    for i, (_, s) in enumerate(original.iterrows()):
        folium.CircleMarker([s['stop_lat'], s['stop_lon']], radius=6, color='white', 
                          fillColor=COLORS['stop_existing'], fillOpacity=1, weight=2).add_to(ex_stops)
        folium.Marker([s['stop_lat'], s['stop_lon']], 
                     icon=folium.DivIcon(html=f'<div style="font:11px Roboto;background:white;padding:2px 6px;border-radius:3px;border:1px solid #ddd">{i+1}</div>')).add_to(ex_labels)
    
    ex_route.add_to(m)
    ex_stops.add_to(m)
    ex_labels.add_to(m)
    
    # RECOMMENDED EXTENSION (Green) - ROAD SNAPPED
    rec = route_variants.iloc[0]
    rec_route = folium.FeatureGroup(name='Extension (Recommended)', show=True)
    rec_stops = folium.FeatureGroup(name='New Stops', show=True)
    rec_labels = folium.FeatureGroup(name='New Labels', show=False)
    
    last_coords = (original.iloc[-1]['stop_lat'], original.iloc[-1]['stop_lon'])
    ext_path = build_extension_path(G, last_coords, rec['new_stop_coords'])
    
    folium.PolyLine(ext_path, color=COLORS['extension'], weight=6, opacity=0.9).add_to(rec_route)
    
    for i, (sid, coord) in enumerate(zip(rec['new_stops'], rec['new_stop_coords'])):
        num = len(original) + i + 1
        info = selected_candidates[selected_candidates['stop_id'] == sid].iloc[0]
        folium.CircleMarker(coord, radius=8, color='white', fillColor=COLORS['stop_new'], 
                          fillOpacity=1, weight=2.5, 
                          popup=f"Stop {num}<br>{sid}<br>Pop: {info['pop_within_500m']:,.0f}").add_to(rec_stops)
        folium.Marker(coord, icon=folium.DivIcon(
            html=f'<div style="font:600 11px Roboto;background:{COLORS["stop_new"]};color:white;padding:3px 7px;border-radius:3px">{num}</div>')).add_to(rec_labels)
    
    rec_route.add_to(m)
    rec_stops.add_to(m)
    rec_labels.add_to(m)
    
    # ALTERNATIVES - ROAD SNAPPED
    for idx, (_, var) in enumerate(route_variants.iloc[1:3].iterrows()):
        if idx >= 2:
            break
        c = COLORS['alt1'] if idx == 0 else COLORS['alt2']
        alt_route = folium.FeatureGroup(name=f'Alternative {idx+2}', show=False)
        alt_stops = folium.FeatureGroup(name=f'Alt {idx+2} Stops', show=False)
        
        alt_path = build_extension_path(G, last_coords, var['new_stop_coords'])
        folium.PolyLine(alt_path, color=c, weight=5, opacity=0.7, dashArray='8,4').add_to(alt_route)
        
        for coord in var['new_stop_coords']:
            folium.CircleMarker(coord, radius=7, color='white', fillColor=c, fillOpacity=0.85, weight=2).add_to(alt_stops)
        
        alt_route.add_to(m)
        alt_stops.add_to(m)
    
    # Info panel
    route_info = feed.routes[feed.routes['route_id'] == route_id].iloc[0]
    orig_pop = sum(df[df['stop_id']==s]['pop_within_500m'].iloc[0] if len(df[df['stop_id']==s])>0 else 0 for s in original['stop_id'])
    new_pop = rec['total_pop_served']
    
    info = f'<div style="position:fixed;top:80px;left:20px;width:280px;background:white;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.15);font:13px Roboto;z-index:9999"><div style="background:{COLORS["extension"]};color:white;padding:12px;border-radius:8px 8px 0 0"><div style="font-size:16px;font-weight:500">{route_id}</div></div><div style="padding:12px"><div style="display:flex;gap:8px;margin-bottom:10px"><div style="flex:1;text-align:center;padding:8px;background:#f8f9fa;border-radius:4px"><div style="font-size:10px;color:#666">EXISTING</div><div style="font-size:20px;font-weight:500;color:{COLORS["existing"]}">{len(original)}</div><div style="font-size:10px">stops</div></div><div style="flex:1;text-align:center;padding:8px;background:#f8f9fa;border-radius:4px"><div style="font-size:10px;color:#666">ADDING</div><div style="font-size:20px;font-weight:500;color:{COLORS["extension"]}">{len(rec["new_stops"])}</div><div style="font-size:10px">stops</div></div></div><div style="background:#f8f9fa;padding:8px;border-radius:4px;margin-bottom:8px"><div style="font-size:11px;color:#666;margin-bottom:4px">Population</div><div style="display:flex;justify-content:space-between;font-size:12px"><span>Existing</span><span>{orig_pop:,.0f}</span></div><div style="display:flex;justify-content:space-between;font-size:12px;color:{COLORS["extension"]}"><span>Extension</span><span>+{new_pop:,.0f}</span></div></div><div style="background:{COLORS["extension"]};color:white;padding:8px;border-radius:4px;text-align:center;font-weight:500">+{(new_pop/orig_pop*100 if orig_pop>0 else 0):.0f}% Increase</div></div></div>'
    m.get_root().html.add_child(folium.Element(info))
    
    # Legend
    legend = f'<div style="position:fixed;bottom:20px;right:20px;width:220px;background:white;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.15);padding:12px;font:12px Roboto;z-index:9999"><div style="font-weight:500;margin-bottom:8px;border-bottom:1px solid #ddd;padding-bottom:6px">Legend</div><div style="display:flex;align-items:center;margin:6px 0"><div style="width:24px;height:3px;background:{COLORS["existing"]};margin-right:8px"></div>Existing</div><div style="display:flex;align-items:center;margin:6px 0"><div style="width:24px;height:4px;background:{COLORS["extension"]};margin-right:8px"></div>Extension</div><div style="display:flex;align-items:center;margin:6px 0"><div style="width:24px;height:3px;background:{COLORS["alt1"]};margin-right:8px;opacity:0.7"></div>Alternatives</div></div>'
    m.get_root().html.add_child(folium.Element(legend))
    
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    plugins.Fullscreen(position='topright').add_to(m)
    
    print(f"✓ Done! Routes snap to roads, Blue=existing, Green=extension")
    return m