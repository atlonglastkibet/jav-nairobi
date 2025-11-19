# Calendar: Spatial and Temporal GTFS Data Analysis

## Overview
This notebook extends the previous spatial and temporal GTFS analysis by incorporating a calendar component to enable sequential and longitudinal analysis of transit service patterns. It creates a comprehensive ward-level dataset that accounts for realistic weekend service variations in Nairobi's transit system.

## Key Objectives
1. **Data Cleaning**: Prepare the dataset for downstream temporal processing
2. **Calendar Integration**: Add a daily calendar structure for October 2025 to enable date-aware analysis
3. **Weekend Adjustment**: Account for reduced transit service levels on weekends using empirically-based multipliers
4. **Temporal Structure**: Create a complete ward × hour × date grid for time-series analysis

## Data Sources
- **Input**: `wards_full_gdf(with_spatial_temporal_gini).parquet` - Previously processed ward-level data with spatial accessibility and equity indicators
- **Output**: `spatio_temporal_calendar.parquet` - Enhanced dataset with calendar integration and weekend adjustments

## Key Features

### Calendar Component
- **Date Range**: October 1-31, 2025 (31 days)
- **Weekday Identification**: Day names and weekend/weekday classification
- **Temporal Structure**: Enables sequential day-by-day analysis and weekday vs. weekend comparisons

### Weekend Service Adjustments
The notebook implements realistic weekend service reductions based on literature and local observations:

| Day | Service Multiplier | Rationale |
|-----|-------------------|-----------|
| **Weekdays** | 1.0 | Baseline service level |
| **Saturday** | 0.7 | 60-80% of weekday service |
| **Sunday** | 0.5 | 40-60% of weekday service |

### Sensitivity Analysis
Three scenarios tested to account for uncertainty in weekend service patterns:
- **Conservative**: Saturday 0.6, Sunday 0.4
- **Central** (adopted): Saturday 0.7, Sunday 0.5
- **Optimistic**: Saturday 0.8, Sunday 0.6

## Technical Implementation

### Data Structure
The final dataset contains **24 hours × 31 days × 170 wards = 126,720 records**, each with:

#### Spatial Identifiers
- Ward, subcounty, constituency, county boundaries
- Geometry and coverage metrics
- Population and demographic indicators

#### Service Metrics
- `trips_per_hour`: Original weekday service levels
- `trips_per_hour_adj`: Weekend-adjusted service levels
- `service_per_1k_pop_adj`: Population-normalized service (per 1,000 residents)
- `trips_per_person_per_hour_adj`: Individual-level service access

#### Temporal Context
- `date`: Daily timestamps (2025-10-01 to 2025-10-31)
- `weekday`: Day names (Monday-Sunday)
- `is_weekend`: Boolean weekend indicator
- `hour`: Hourly service periods

### Key Transformations
1. **Cross-join**: Wards × Calendar to create complete temporal grid
2. **Weekend scaling**: Apply day-specific multipliers to service metrics
3. **Metric recalculation**: Update population-normalized indicators
4. **Sorting**: Organize by ward → date → hour for time-series consistency

## Analysis Applications

This enhanced dataset enables several advanced analyses:

### Temporal Patterns
- **Peak vs. off-peak** service variations throughout the week
- **Weekday vs. weekend** service equity comparisons
- **Day-to-day** service consistency analysis

### Equity Studies
- **Longitudinal equity**: How service disparities change over time
- **Weekend accessibility**: Impact of reduced service on different populations
- **Service ranking stability**: Consistency of ward-level service rankings

### Predictive Modeling
- **LSTM preparation**: Sequential data structure for neural network training
- **Trajectory integration**: Ready for WorldMove mobility data fusion
- **Scenario planning**: Framework for testing service improvement strategies

## Key Insights

### Service Variation
- **Weekday consistency**: ~650 trips/hour maintained Monday-Friday
- **Saturday reduction**: Service drops to 455-520 trips/hour depending on scenario
- **Sunday minimum**: Lowest service at 260-390 trips/hour

### Data Quality
- **No missing values**: Complete dataset with 126,720 valid records
- **Spatial coverage**: All 170 wards included with full temporal coverage
- **Temporal integrity**: Consistent hour-by-hour service patterns

## Next Steps
1. **Mobility integration**: Incorporate WorldMove trajectory data for demand-supply matching
2. **Equity modeling**: Apply temporal equity metrics across the weekly cycle
3. **Predictive analysis**: Use LSTM models to forecast service patterns and equity outcomes
4. **Scenario testing**: Evaluate service improvement strategies using the temporal framework

## Dependencies
- **pandas**: Data manipulation and calendar creation
- **geopandas**: Geospatial operations and parquet handling
- **numpy**: Numerical computations
- **matplotlib/seaborn**: Visualization support
- **missingno**: Data quality assessment

## Usage Notes
- The central weekend multipliers (0.7 Saturday, 0.5 Sunday) represent conservative estimates based on ITDP guidelines and Nairobi observations
- The dataset maintains original weekday values while providing adjusted metrics for realistic temporal modeling
- Calendar structure is designed for October 2025 but can be easily extended to other time periods