# WorldMove Dataset Documentation

## Overview

WorldMove is a large-scale synthetic mobility dataset covering over 1,600 cities across 179 countries and 6 continents. The dataset uses a diffusion-based generative model to create realistic urban mobility patterns from publicly available data sources.

## Links

- **Official Website**: [WorldMove Dataset Portal](https://www.fiblab.net/worldmove/)
- **GitHub Repository**: [https://github.com/tsinghua-fib-lab/WorldMove](https://github.com/tsinghua-fib-lab/WorldMove)
- **Research Paper**: [arXiv:2504.10506](https://arxiv.org/abs/2504.10506)

## Dataset Description

WorldMove generates synthetic mobility data by combining multiple publicly available data sources:
- Gridded population distribution (WorldPop)
- Point-of-Interest (POI) maps (OpenStreetMap)
- Road network data (OpenStreetMap)
- Commuting origin-destination (OD) flows

### Key Features

- **Coverage**: 1,600+ cities globally
- **Methodology**: Diffusion-based generative model
- **Validation**: Validated against real-world mobility patterns
- **Privacy**: Fully synthetic data, no privacy concerns
- **Resolution**: 1km x 1km grid cells

## Nairobi, Kenya Dataset Components

### 1. Administrative Areas
**File Format**: `.shp` (Shapefile)  
**Description**: Geographic boundaries of administrative divisions in Nairobi  
**Usage**: Spatial context and aggregation for analysis

### 2. Grid-cell Coordinates
**File Format**: `.json`  
**Example**: `1098_KE_Nairobi.json`  
**Structure**:
```json
{
  "0": [longitude, latitude],
  "1": [longitude, latitude],
  ...
  "1439": [longitude, latitude]
}
```
**Description**: Centers of 1km x 1km grid cells covering Nairobi (1,440 cells total)  
**Coordinate System**: WGS84 (EPSG:4326)

### 3. Grid-cell Population
**File Format**: `.npy` (NumPy array)  
**Shape**: `(grid_num_rows, grid_num_cols)`  
**Description**: Population count for each grid cell from WorldPop project  
**Usage**: Understanding traffic demand sources and residential density

### 4. Grid-cell POI (Points of Interest)
**File Format**: `.npy` (NumPy array)  
**Shape**: `(grid_num_rows, grid_num_cols, poi_type_num)`  
**Description**: Count of each POI type per grid cell  
**POI Categories**: Commercial, educational, healthcare, recreational, transportation, etc.  
**Usage**: Identifying traffic destination attractors

### 5. Generated Trajectories
**File Format**: `.npy` or `.npz` (NumPy array/archive)  
**Shape**: `(num_trajectories, trajectory_length)`  
**Description**: Sequences of grid cell indices representing individual movement patterns  
**Example**: `[45, 112, 89, 234, ...]` = Person moves from cell 45 → 112 → 89 → 234  
**Temporal Resolution**: Varies by city (typically 10-30 minute intervals)

### 6. Complete Dataset Package
**File Format**: `.npz`  
**Contents**: All components bundled together
- Grid coordinates
- Population data
- POI data
- Trajectory data

## Data Loading Example

```python
import numpy as np
import json

# Load grid coordinates
with open('1098_KE_Nairobi.json', 'r') as f:
    coordinates = json.load(f)

# Load population data
population = np.load('nairobi_population.npy')

# Load POI data
poi_data = np.load('nairobi_poi.npy')

# Load trajectories
trajectories = np.load('nairobi_trajectories.npy')

# Or load complete package
data = np.load('nairobi_complete.npz')
coordinates = data['coordinates']
population = data['population']
poi = data['poi']
trajectories = data['trajectories']
```

## Converting to Traffic Congestion Data

### Methodology

1. **Extract Movements**: Parse trajectories to identify origin-destination pairs
2. **Temporal Aggregation**: Group movements by time intervals (hourly, daily)
3. **Spatial Aggregation**: Map movements to road segments
4. **Calculate Metrics**: Compute traffic intensity, congestion scores, speeds

### Traffic Metrics Schema

```json
{
  "timestamp": "2024-10-28T08:30:00Z",
  "grid_cell_id": 45,
  "traffic_intensity": 156.2,
  "congestion_score": 3,
  "congestion_level": "moderate",
  "vehicle_count": 420,
  "avg_speed_kmh": 25.5
}
```

## Use Cases

### Urban Planning
- Identify congestion hotspots
- Plan new road infrastructure
- Optimize public transportation routes

### Traffic Analysis
- Peak hour identification
- Weekend vs weekday patterns
- Seasonal variations

### Research Applications
- Transportation modeling
- Urban mobility studies
- Carbon emissions analysis

## Citation

If using WorldMove data in research, please cite:

```bibtex
@article{worldmove2025,
  title={WorldMove: A Large-scale Synthetic Mobility Dataset},
  author={Yuan et al.},
  journal={arXiv preprint arXiv:2504.10506},
  year={2025}
}
```

## Data Access

1. Visit the [WorldMove website](https://www.fiblab.net/worldmove/)
2. Navigate to the data download section
3. Select city: Nairobi, Kenya (Country Code: KE, City ID: 1098)
4. Download required components:
   - Administrative boundaries
   - Grid coordinates
   - Population data
   - POI data
   - Trajectory data

## Technical Specifications

- **Grid Resolution**: 1km × 1km
- **Coordinate System**: WGS84 (Latitude/Longitude)
- **Data Format**: JSON, NumPy (.npy/.npz), Shapefile (.shp)
- **City Coverage**: Nairobi Metropolitan Area (1,440 grid cells)

## Limitations

- **Synthetic Data**: Generated from models, not real observations
- **Temporal Scope**: Represents typical mobility patterns, not specific dates
- **Mode of Transport**: Human mobility patterns (can be converted to vehicle traffic)
- **Resolution**: 1km grid cells may not capture fine-grained street-level details

## Support

- **Issues**: Report on [GitHub Issues](https://github.com/tsinghua-fib-lab/WorldMove/issues)
- **Documentation**: See GitHub repository README
- **Research Group**: Tsinghua University FIB Lab

## License

Please refer to the WorldMove website and GitHub repository for licensing information.

---

**Last Updated**: October 28, 2025  
**Dataset Version**: Check WorldMove website for latest version  
**Document Version**: 1.0