
import pandas as pd
import shapely.wkt
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent))

try:
    from utils.data_loader import get_ward_equity_data
    
    print("Loading ward data...")
    ward_data = get_ward_equity_data()
    
    print("Columns:", ward_data.columns.tolist())
    
    if 'geometry' in ward_data.columns:
        geom = ward_data['geometry'].iloc[0]
        print(f"First geometry type: {type(geom)}")
        print(f"First geometry: {str(geom)[:100]}...")
        
        # Check coordinate values
        if hasattr(geom, 'centroid'):
            centroid = geom.centroid
            print(f"Centroid: {centroid.x}, {centroid.y}")
            
            if centroid.x > 180 or centroid.y > 90:
                print("ISSUE DETECTED: Coordinates seem to be projected (not Lat/Lon).")
            else:
                print("Coordinates seem to be Lat/Lon.")
    else:
        print("No geometry column found.")
        
except Exception as e:
    print(f"Error: {e}")
