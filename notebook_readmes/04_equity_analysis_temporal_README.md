# Temporal Equity Analysis: How Transit Service Varies Throughout the Day

## Overview

This analysis examines how public transport service levels change during different times of the day and whether these temporal patterns create equity issues for different neighborhoods. While spatial analysis shows where services are located, temporal analysis reveals when services are available and how this affects access for different communities.

## What is Temporal Equity?

Temporal equity in public transport refers to how fairly transit services are distributed across different times of the day. An equitable system provides adequate service not just in certain locations, but also during the hours when people need to travel. This includes consideration of:

- Peak versus off-peak service levels
- Early morning and late evening availability
- Weekend and holiday service provision
- Consistency of service throughout operational hours

## Research Questions Addressed

1. **Service Distribution Over Time**: How does transit service per capita change across hours of the day (6 AM, 9 AM, 3 PM)?

2. **Ward-Level Temporal Patterns**: Which neighborhoods maintain good service throughout the day versus those where service quality fluctuates significantly?

3. **Temporal Inequality**: Do disadvantaged areas experience disproportionately poor service during certain hours?

4. **Service Consistency**: Are temporal disparities as significant as spatial ones, or does service remain relatively consistent over time?

## Analysis Framework

### Data Preparation

**GTFS Schedule Integration**
- Integration of Digital Matatus GTFS data with ward-level population estimates
- Processing of stop_times and frequencies tables to extract hourly service patterns
- Conversion of headway information (time between vehicles) into trips per hour metrics

**Temporal Segmentation**
The analysis focuses on three key time periods representing different travel demand patterns:
- **6 AM**: Morning peak (commuting to work/school)
- **9 AM**: Late morning (post-peak, mixed travel purposes)
- **3 PM**: Afternoon peak (return commuting, school pickup)

**Population Normalization**
Service metrics are calculated per 1,000 population to enable fair comparison between areas of different sizes:
```
Service per 1k population = (Total trips per hour / Ward population) × 1000
```

### Service Intensity Calculation

**Trip Frequency Analysis**
For each time period, the analysis calculates:
- **Total trips per hour**: Raw count of vehicle departures serving each ward
- **Trips per 1,000 people**: Population-normalized service intensity
- **Service rank**: Ward ranking by service level during each time period

**Headway-Based Metrics**
Service frequency derived from GTFS frequencies table:
- **Peak hours**: 300-second headways (12 trips per hour)
- **Off-peak hours**: 900-second headways (4 trips per hour)
- **Service span**: Duration of service availability

## Key Findings

### Temporal Service Patterns

**Citywide Service Distribution**
- **Morning Peak (6 AM)**: 3,168 total trips per hour across all routes
- **Late Morning (9 AM)**: 1,056 total trips per hour (66% reduction)
- **Afternoon Peak (3 PM)**: 3,168 total trips per hour (return to peak levels)

**Peak-to-Off-Peak Ratios**
The analysis reveals a clear temporal pattern where:
- Morning and afternoon peaks provide equivalent service levels
- Mid-day service operates at approximately one-third of peak intensity
- This pattern reflects commuter-focused service design

### Ward-Level Temporal Analysis

**Consistently High-Performing Wards**
Areas maintaining strong service across all three time periods:
- **Nairobi Central Ward**: 148-191 trips per 1,000 people per hour
- **Kayole South Ward**: 82-96 trips per 1,000 people per hour
- **Ngara Ward**: 62-81 trips per 1,000 people per hour
- **Parklands/Highridge Ward**: 27-41 trips per 1,000 people per hour

**Consistently Low-Performing Wards**
Areas with poor service throughout the day:
- **Mathare North Ward**: 0.05-0.16 trips per 1,000 people per hour
- **Korogocho Ward**: Zero service during all measured periods
- **Kawangware Ward**: Minimal service across time periods
- **Lucky Summer Ward**: Very limited service availability

### Temporal Inequality Measurement

**Gini Coefficient Analysis**
The analysis applies inequality measurement across different temporal dimensions:

**Hourly Gini (0.610)**
- Calculated across all ward-hour combinations
- Captures both spatial differences between wards and temporal differences within wards
- Indicates moderate to high temporal inequality

**Daily-Average Gini (0.573)**
- Calculated after averaging each ward's service across the day
- Focuses on ward-level differences while smoothing temporal variation
- Slightly lower than hourly Gini, suggesting temporal variation contributes to overall inequality

### Inequality Consistency Across Time

**Hour-by-Hour Gini Analysis**
- **6 AM Gini**: ~0.57
- **9 AM Gini**: ~0.57
- **3 PM Gini**: ~0.57

**Key Finding**: The Gini coefficient remains remarkably stable across different hours (~0.57 for all three time periods). This indicates that:
- Inequality patterns persist throughout the day
- Well-served areas remain well-served at all hours
- Poorly served areas remain underserved regardless of time
- Temporal variation does not significantly alter the equity landscape

## Ranking Analysis

### Service Ranking Systems

**Overall Rank (1-255)**
- Ranks all ward-hour combinations globally
- Shows where each ward-hour stands in citywide service hierarchy
- Enables identification of extreme service gaps

**Hourly Rank (1-85 per hour)**
- Ranks wards within each specific hour
- Reveals temporal shifts in relative ward performance
- Helps identify wards that improve or decline at certain times

**Ranking Stability**
Most wards maintain similar relative positions across different hours, confirming the stability of service patterns throughout the day.

## Visualization and Insights

### Interactive Time-Based Maps

**Multi-Hour Mapping**
The analysis includes interactive maps that allow exploration of service levels at different times:
- Color-coded wards showing trips per 1,000 people per hour
- Time slider functionality for comparing 6 AM, 9 AM, and 3 PM patterns
- Consistent geographic patterns visible across all time periods

**Service Distribution Charts**
- Bar charts comparing top and bottom performing wards across time periods
- Temporal trend lines showing stability of service patterns
- Population-weighted service histograms

### Lorenz Curve Analysis

**Inequality Visualization**
Lorenz curves illustrate how service is distributed across the population:
- **Daily-average curve**: Shows ward-level inequality
- **Hourly-pooled curve**: Shows combined temporal and spatial inequality
- Both curves demonstrate significant departure from perfect equality line

**Bottom 50% Analysis**
- Bottom 50% of ward-hours receive only ~15% of total service
- Bottom 50% of wards (daily average) receive only ~20% of total service
- Indicates significant concentration of service in top-performing areas

## Policy Implications

### Temporal Service Planning

**Peak Service Optimization**
- Current peak-hour service levels appear adequate for high-demand periods
- Off-peak service reductions may limit access for non-commuter trips
- Consider impact of reduced midday service on essential trips (healthcare, shopping, education)

**Service Consistency**
- Strong correlation between spatial and temporal service quality
- Areas with poor service suffer throughout the day
- Targeted investments needed in persistently underserved areas

### Equity Interventions

**Time-Sensitive Equity**
Since temporal inequality mirrors spatial inequality:
- Spatial equity improvements will likely improve temporal equity
- Focus on expanding service to underserved areas rather than just adjusting schedules
- Consider all-day service needs, not just peak-hour commuting

**Service Redistribution**
- Evaluation of whether peak-hour concentration serves broader community needs
- Assessment of midday service adequacy for essential trip purposes
- Balance between efficiency (peak focus) and equity (all-day service)

## Technical Methods

### Data Processing Pipeline

**GTFS Integration**
- Processing of stop_times and frequencies tables
- Spatial joining of transit stops with ward boundaries
- Aggregation of trip counts by ward and hour

**Temporal Aggregation**
- Conversion of scheduled arrival times to hourly service counts
- Population normalization for cross-ward comparison
- Ranking calculation for relative performance assessment

**Statistical Analysis**
- Gini coefficient calculation for inequality measurement
- Lorenz curve generation for inequality visualization
- Time series analysis of service patterns

### Quality Assurance

**Data Validation**
- Verification of temporal aggregation accuracy
- Cross-checking of population normalization calculations
- Validation of Gini coefficient computations

**Missing Data Handling**
- Complete ward-hour grid creation to ensure all combinations represented
- Zero-filling for wards with no service rather than missing data treatment
- Conservative assumptions for data quality preservation

## Applications and Extensions

### Planning Applications
- Schedule optimization for improved temporal equity
- Service reallocation between high and low-performing areas
- Integration with demand modeling for service planning

### Research Extensions
- Detailed trip-purpose analysis by time of day
- Integration with employment and activity patterns
- Accessibility modeling incorporating temporal service variation

### Policy Development
- Evidence base for equitable service standards
- Framework for monitoring temporal equity over time
- Integration with broader urban mobility planning

## Conclusions

The temporal equity analysis reveals that **inequality patterns in Nairobi's transit system are remarkably stable throughout the day**. This finding suggests that:

1. **Spatial inequalities dominate temporal ones** - where you live matters more than when you travel
2. **System-wide improvements needed** rather than schedule adjustments alone
3. **Consistent investment required** in underserved areas to achieve equity goals
4. **All-day access considerations** important for comprehensive transport equity

This analysis provides crucial evidence for transport planning that addresses not just where services are provided, but when they are available to serve diverse community needs throughout the day.