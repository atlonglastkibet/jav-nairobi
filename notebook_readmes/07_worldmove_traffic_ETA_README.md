# WorldMove Traffic and Travel Time Analysis: Understanding Urban Mobility Patterns

## Overview

This analysis processes synthetic traffic and mobility data from the WorldMove dataset to understand travel patterns, congestion levels, and estimated travel times across Nairobi. By analyzing agent-based movement trajectories, the study creates traffic indicators that can inform transit planning decisions and help understand how road conditions affect public transport operations.

## Understanding WorldMove Traffic Data

### Synthetic Traffic Generation

The WorldMove dataset contains millions of synthetic individual travel trajectories generated using advanced diffusion-based models. These trajectories represent realistic movement patterns based on population distribution, land use, and mobility behavior learned from global urban mobility data.

**Data Structure**
- **Individual Agents**: Each represents a person's daily movement
- **Trajectory Points**: Timestamped location coordinates throughout the day
- **Movement Patterns**: Realistic representation of urban mobility flows
- **Temporal Resolution**: Hourly and sub-hourly movement tracking

### Traffic Proxy Development

**From Trajectories to Traffic Indicators**
Individual movement trajectories are aggregated into traffic metrics:
1. **Density Analysis**: Count of agents in spatial areas over time
2. **Flow Calculation**: Movement between areas and along corridors
3. **Speed Estimation**: Travel times between connected points
4. **Congestion Assessment**: Relative density and speed patterns

**Spatial-Temporal Aggregation**
- **Grid-Based Analysis**: 1km x 1km cells for consistent spatial units
- **Hourly Patterns**: Service pressure and demand by hour of day
- **Daily Summaries**: Average conditions and peak-hour analysis
- **Corridor Analysis**: Major route and connection assessment

## Analysis Methodology

### Traffic Metrics Calculation

**Primary Traffic Indicators**

**1. Agent Density**
$$\text{Density} = \frac{\text{Number of Agents in Cell}}{\text{Cell Area (km}^2\text{)}}$$

Measures traffic volume and activity level per unit area in different locations.

**2. Flow Analysis**
$$\text{Flow}_{i,j} = \frac{\text{Agent Movements from Cell } i \text{ to Cell } j}{\text{Time Period (hours)}}$$

Captures directional movement patterns and corridor usage between adjacent areas.

**3. Speed Estimation from Trajectories**
For successive trajectory points, calculate instantaneous speed:

$$v_t = \frac{d(P_t, P_{t+1})}{\Delta t}$$

Where:
- $P_t$ = agent position at time $t$
- $d(P_t, P_{t+1})$ = great-circle distance between consecutive points
- $\Delta t$ = time interval between observations

Average speed for a trip segment:
$$\bar{v} = \frac{1}{n-1} \sum_{t=1}^{n-1} v_t$$

**4. Congestion Index**
$$\text{Congestion Index} = \frac{v_{free} - v_{observed}}{v_{free}}$$

Where:
- $v_{free}$ = free-flow speed (baseline: 35 km/h for Nairobi)
- $v_{observed}$ = actual observed speed
- Range: 0 (no congestion) to 1 (complete standstill)

**5. Time-of-Day Speed Profiles**
Congestion-aware speed modeling based on empirical Nairobi traffic patterns:

$$v_{hour} = v_{base}(h) \times f_{distance}(d) \times (1 + \varepsilon)$$

Where:
- $v_{base}(h)$ = base speed for hour $h$ (see profile table)
- $f_{distance}(d)$ = distance adjustment factor
- $\varepsilon \sim \mathcal{N}(0, 0.15^2)$ = random variation (±15%)

**Time-Based Speed Profiles for Nairobi:**

| Time Period | Hours | Base Speed (km/h) | Traffic Condition |
|-------------|-------|------------------|-------------------|
| Night | 00:00-06:00 | 35 | Free flow |
| Morning Rush | 06:00-09:00 | 15 | Heavy congestion |
| Midday | 10:00-14:00 | 25 | Moderate flow |
| Afternoon Rush | 15:00-19:00 | 12 | Heaviest congestion |
| Evening | 20:00-23:00 | 28 | Clearing traffic |

**Distance-Based Speed Adjustment:**
$$f_{distance}(d) = \begin{cases}
0.75 & \text{if } d < 1 \text{ km (short trips)} \\
1.0 & \text{if } 1 \leq d \leq 3 \text{ km (medium trips)} \\
1.15 & \text{if } d > 3 \text{ km (long trips)}
\end{cases}$$

### Temporal Pattern Analysis

**Peak Hour Identification**
- **Morning Peak**: Typically 6:00-9:00 AM
- **Evening Peak**: Usually 4:00-7:00 PM
- **Off-Peak Periods**: Midday and evening hours
- **Baseline Conditions**: Late night and early morning

**Service Pressure Calculation**
$$\text{Service Pressure} = \frac{\text{Peak Hour Demand}}{\text{Average Hourly Demand}}$$

For each cell or ward:
$$\text{Pressure}_{i} = \frac{\max_{h \in [6,7,8,17,18,19]} \text{Flow}_{i,h}}{\frac{1}{24}\sum_{h=0}^{23} \text{Flow}_{i,h}}$$

Where:
- Peak hours: 6-9 AM and 5-8 PM
- Values > 2.0 indicate high service pressure during rush hours

**Route ETA Calculation**
For GTFS routes, estimate travel time using real-time traffic conditions:

$$\text{ETA}_{route} = \sum_{s=1}^{n-1} \frac{d_{s,s+1}}{v_{s,h}} \times 60$$

Where:
- $d_{s,s+1}$ = distance between consecutive stops $s$ and $s+1$ (km)
- $v_{s,h}$ = traffic speed at route midpoint during hour $h$ (km/h)
- Result in minutes

**Segment-Level ETA Calculation:**
1. **Route Segmentation**: Divide route into stop-to-stop segments
2. **Spatial Lookup**: Find nearest traffic cell to segment midpoint
3. **Speed Retrieval**: Get cell-specific speed for target hour
4. **Distance Calculation**: Haversine formula for segment length
5. **Time Estimation**: Apply speed to get segment travel time

$$d_{haversine} = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$

Where $R = 6371$ km (Earth radius), $\phi$ = latitude, $\lambda$ = longitude.

### Geographic Processing

**Spatial Aggregation Methods**
1. **Grid Cell Assignment**: Map trajectory points to 1km grid cells
2. **Ward-Level Aggregation**: Summary statistics by administrative boundaries
3. **Corridor Analysis**: Linear features along major roads and routes
4. **Network Integration**: Connection with GTFS transit network data

## Key Findings and Insights

### Traffic Pattern Discovery

**Spatial Distribution**
- **High-Traffic Areas**: Central business district and major residential nodes
- **Corridor Identification**: Main roads and transport arteries
- **Low-Traffic Zones**: Peripheral areas and less connected neighborhoods
- **Activity Centers**: Employment, commercial, and institutional areas

**Temporal Dynamics**
- **Peak Hour Concentration**: Clear morning and evening peaks
- **Midday Patterns**: Reduced but significant continued activity
- **Weekend Variations**: Different patterns from weekday commuting
- **Directional Flows**: Inbound morning, outbound evening patterns

### Congestion and Delay Analysis

**Congestion Hotspots**
Areas experiencing significant traffic delays:
- **CBD Access Routes**: Major roads entering central Nairobi
- **Residential Connectors**: Links between high-density housing and employment
- **Intersection Areas**: Major road crossings and junctions
- **Transit Corridors**: Roads heavily used by matatu services

**Speed Variations**
- **Free-Flow Speeds**: 40-60 km/h on major roads
- **Peak Hour Speeds**: 15-25 km/h in congested areas
- **Off-Peak Speeds**: 30-45 km/h moderate traffic
- **Severe Congestion**: Under 10 km/h in worst areas

### Service Implications

**Transit Service Pressure**
Areas where high traffic demand creates challenges for public transport:
- **Extended Travel Times**: Congestion affects matatu schedules
- **Reliability Issues**: Traffic variation impacts service consistency
- **Capacity Constraints**: High demand may exceed service supply
- **Route Efficiency**: Traffic affects optimal route planning

## Applications for Transit Planning

### Route Planning Integration

**Congestion-Aware Route Design**
- **Avoidance Strategies**: Routes that minimize traffic delay exposure
- **Time-of-Day Optimization**: Service adjustments based on traffic patterns
- **Alternative Routing**: Options during severe congestion periods
- **Express Service**: Limited-stop services in high-traffic corridors

**Service Frequency Planning**
- **Peak Hour Enhancement**: Increased frequency during high-demand periods
- **Off-Peak Optimization**: Efficient service during lower-demand times
- **Reliability Buffers**: Schedule padding for traffic-affected routes
- **Dynamic Adjustment**: Real-time service modification capabilities

### Infrastructure Planning

**Priority Infrastructure Needs**
- **Bus Priority Lanes**: Corridors where transit needs traffic separation
- **Traffic Signal Optimization**: Intersection improvements for transit
- **Stop Location Planning**: Placement considering traffic flow and safety
- **Terminal Design**: Facilities that accommodate traffic-affected operations

**Integration with Development**
- **Land Use Coordination**: Development planning considering traffic impact
- **Transport-Oriented Development**: Focus on areas with good traffic conditions
- **Congestion Mitigation**: Transit improvements to reduce overall traffic
- **Network Connectivity**: Links that improve overall system efficiency

### Performance Monitoring

**Service Quality Indicators**
- **Travel Time Reliability**: Consistency of journey times
- **Schedule Adherence**: Ability to maintain published schedules
- **Passenger Experience**: Impact of traffic on comfort and predictability
- **System Efficiency**: Overall network performance under traffic conditions

## Technical Implementation

### Data Processing Pipeline

**1. WorldMove Trajectory Processing**
Extract and process synthetic mobility data:

```python
# Load WorldMove .npz archive
traj_data = np.load('worldmove_trajectories.npz')
grid_dict = traj_data['grid'].item()  # Cell ID to coordinates mapping
trajectories = traj_data['traj']      # Agent movements (104,538 agents × 48 timesteps)

# Convert timesteps to hours (48 timesteps = 30-min intervals)
timestep_to_hour = {t: t // 2 for t in range(48)}
```

**2. Spatial Grid Processing**
Map grid cells to administrative boundaries:

```python
# Create grid cell GeoDataFrame
cell_coords = np.array(list(grid_dict.values()))
grid_gdf = gpd.GeoDataFrame(
    {'cell_id': list(grid_dict.keys())},
    geometry=[Point(lon, lat) for lon, lat in cell_coords],
    crs='EPSG:4326'
).to_crs('EPSG:32737')

# Spatial join with wards
cell_to_ward = gpd.sjoin(grid_gdf, wards_gdf, predicate='within')
```

**3. Trip Extraction from Trajectories**
Convert raw agent movements to meaningful trips:

```python
def extract_trips(traj_data, valid_cells):
    """Extract inter-cell movements from trajectory matrix"""
    trips = []

    for agent_id in range(traj_data.shape[0]):
        trajectory = traj_data[agent_id, :]

        # Find movements (cell changes)
        origins = trajectory[:-1]
        destinations = trajectory[1:]
        moved = origins != destinations

        for t in np.where(moved)[0]:
            if origins[t] in valid_cells and destinations[t] in valid_cells:
                trips.append({
                    'agent_id': agent_id,
                    'timestep': t,
                    'hour': timestep_to_hour[t],
                    'origin_cell': origins[t],
                    'dest_cell': destinations[t]
                })

    return pd.DataFrame(trips)
```

**4. Road Network Integration**
Snap grid cells to OpenStreetMap road network:

```python
# Load Nairobi road network
G_drive = ox.graph_from_bbox(bbox=(36.6, -1.5, 37.0, -1.1), network_type='drive')

# Snap cells to nearest road nodes
cell_to_node = {}
for cell_id, (lon, lat) in cell_coords.items():
    try:
        nearest_node = ox.nearest_nodes(G_drive, lon, lat)
        cell_to_node[cell_id] = nearest_node
    except:
        cell_to_node[cell_id] = None
```

**5. Distance and Speed Calculation**
Compute route distances and realistic speeds:

```python
@lru_cache(maxsize=100000)
def route_distance_cached(origin_node, dest_node):
    """Cached network distance calculation"""
    try:
        return ox.shortest_path_length(G_drive, origin_node, dest_node, weight='length')
    except:
        return np.nan

def calculate_realistic_speed(trips_df):
    """Apply congestion-aware speed model"""
    # Time-of-day profiles
    congestion_profiles = {
        'night': {'hours': list(range(0, 6)), 'base_speed': 35, 'variance': 5},
        'morning_rush': {'hours': [6, 7, 8, 9], 'base_speed': 15, 'variance': 8},
        'afternoon_rush': {'hours': [15, 16, 17, 18, 19], 'base_speed': 12, 'variance': 7}
    }

    # Apply speed model with distance and time factors
    trips_df['speed_kmh'] = (
        trips_df['base_speed'] *
        trips_df['distance_factor'] *
        trips_df['random_variation']
    ).clip(5, 60)  # Urban speed limits

    return trips_df
```

**6. Cell-Level Traffic Aggregation**
Create static traffic baseline (Model 2):

```python
# Aggregate trips by origin cell and hour
cell_traffic = trips_df.groupby(['origin_cell', 'hour']).agg({
    'speed_kmh': ['mean', 'std'],
    'agent_id': 'count',
    'congestion_level': lambda x: x.mode()[0] if len(x) > 0 else 'unknown'
}).reset_index()

# Add spatial coordinates
cell_traffic = cell_traffic.merge(cell_coords_df, on='cell_id')
```

### Computational Tools
- **NumPy/Polars**: For efficient trajectory processing and large-scale computations
- **OSMnx**: For road network analysis and routing calculations
- **GeoPandas**: For spatial operations and coordinate transformations
- **SciPy**: For spatial distance calculations and optimization
- **LRU Cache**: For memoizing expensive route calculations

### Data Quality and Validation
- **Trajectory Completeness**: Validate 48-timestep sequences for all active agents
- **Spatial Consistency**: Verify grid cell mapping covers target geographic area
- **Speed Validation**: Check calculated speeds fall within realistic urban ranges (5-60 km/h)
- **Conservation Checks**: Ensure agent counts and trip totals remain consistent across processing steps

### Integration with Transit Data

**GTFS Integration**
- **Stop-Level Traffic**: Traffic conditions near transit stops
- **Route-Level Analysis**: Traffic along transit corridors
- **Schedule Impact**: How traffic affects published timetables
- **Network Effects**: System-wide implications of traffic patterns

**Ward-Level Aggregation**
- **Administrative Summary**: Traffic statistics by ward boundaries
- **Service Integration**: Combine traffic with transit access metrics
- **Equity Analysis**: Traffic impact on different neighborhood types
- **Planning Integration**: Align with administrative planning processes

### Validation and Quality Assurance

**Data Quality Checks**
- **Trajectory Completeness**: Ensure adequate coverage and sampling
- **Speed Validation**: Check calculated speeds against reasonable ranges
- **Temporal Consistency**: Verify patterns align with expected urban rhythms
- **Spatial Coherence**: Confirm geographic patterns make sense

**Comparison with Observed Data**
- **GPS Validation**: Compare with actual traffic speed data where available
- **Transit Performance**: Check against actual matatu journey times
- **Congestion Validation**: Verify patterns match known problem areas
- **Peak Hour Verification**: Confirm timing of traffic peaks

## Results and Data Products

### Traffic Indicator Datasets

**Gridded Traffic Data**
- **Hourly Traffic Density**: Agent counts by hour for each grid cell
- **Daily Average Speeds**: Mean travel speeds by area
- **Congestion Indices**: Relative delay measurements
- **Flow Matrices**: Movement between adjacent areas

**Administrative Summaries**
- **Ward-Level Traffic**: Aggregated indicators by ward boundaries
- **Peak Hour Analysis**: Morning and evening peak characteristics
- **Service Pressure Maps**: Areas of high transit demand relative to supply
- **Corridor Performance**: Major route traffic characteristics

### Interactive Visualizations

**Traffic Heat Maps**
- **Density Visualization**: Color-coded maps showing traffic intensity
- **Speed Analysis**: Geographic display of average travel speeds
- **Congestion Mapping**: Visual identification of problem areas
- **Temporal Animation**: Traffic patterns throughout the day

**Corridor Analysis**
- **Route Performance**: Traffic conditions along major transit routes
- **Bottleneck Identification**: Specific locations with severe delays
- **Alternative Routing**: Options for avoiding congested areas
- **Service Impact**: How traffic affects transit performance

## Limitations and Considerations

### Synthetic Data Limitations

**Model Assumptions**
- Based on learned patterns from global data
- May not capture all local Nairobi-specific behaviors
- Simplified representation of complex traffic dynamics
- Limited integration with actual traffic management systems

**Validation Needs**
- Comparison with real traffic data when available
- Ground-truthing through field observations
- Integration with local traffic management data
- Continuous model calibration and improvement

### Planning Applications

**Decision Support**
- Provides general patterns and trends for planning
- Requires local knowledge for specific implementation decisions
- Should be combined with other data sources for comprehensive analysis
- Useful for strategic rather than detailed operational planning

**Uncertainty Considerations**
- Synthetic data provides estimates rather than precise measurements
- Variability and confidence intervals should be considered
- Sensitivity analysis important for robust planning decisions
- Regular updates needed as urban conditions change

## Future Enhancements

### Real-Time Integration

**Dynamic Traffic Analysis**
- Integration with real-time traffic monitoring systems
- Adaptive routing based on current conditions
- Dynamic service adjustment capabilities
- Predictive modeling for traffic and demand forecasting

**Smart City Integration**
- Connection with intelligent transportation systems
- Integration with mobile phone mobility data
- Real-time passenger information systems
- Coordinated traffic and transit management

### Advanced Analytics

**Machine Learning Applications**
- Traffic prediction models using historical patterns
- Congestion forecasting for proactive management
- Route optimization using traffic and demand data
- Integrated mobility system optimization

**Network Analysis**
- Complex network analysis of traffic and transit systems
- Resilience analysis under different traffic scenarios
- Optimization models for system-wide performance
- Multi-modal integration and coordination

## Conclusion

The WorldMove traffic and travel time analysis provides valuable insights into mobility patterns that affect public transport operations in Nairobi. By processing synthetic trajectory data into actionable traffic indicators, this analysis enables evidence-based planning that considers the complex interactions between traffic conditions and transit service delivery.

The traffic analysis reveals clear patterns of congestion and delay that create challenges for public transport operations, while also identifying opportunities for strategic improvements. Understanding these patterns enables more effective route planning, service scheduling, and infrastructure investment that can improve both transit performance and overall urban mobility.

This traffic foundation supports integrated transport planning that recognizes the interconnected nature of different mobility modes and the importance of considering traffic conditions in transit system design and operation. The resulting insights contribute to more realistic and effective approaches to improving public transport accessibility and reliability across Nairobi's diverse urban landscape.