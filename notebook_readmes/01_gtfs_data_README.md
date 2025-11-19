# GTFS Data Analysis: Understanding Nairobi's Public Transport System

## Overview

This analysis explores the Digital Matatus GTFS (General Transit Feed Specification) dataset, which contains comprehensive information about Nairobi's informal public transport system. The Digital Matatus project, a collaboration between MIT and local partners, mapped 135 matatu routes serving over 4,000 stops throughout Nairobi.

## What is GTFS?

GTFS is an internationally recognized standard for sharing public transit schedules and geographic information. Originally developed by Google in 2005, GTFS enables transit agencies, mapping applications, and researchers to work with consistent, structured data about bus routes, schedules, and stop locations.

## Data Sources

**Primary Dataset**: Digital Matatus GTFS Feed 2019
- Source: MIT Digital Matatus Project
- Coverage: Nairobi Metropolitan Area
- Routes: 136 matatu routes
- Stops: 4,284 transit stops
- Time Period: March 2012 to December 2020

## Analysis Workflow

### Data Validation and Quality Assessment

The analysis begins with comprehensive data quality checks using specialized GTFS validation tools. The assessment reveals that while some distance measurements between stops are missing, the dataset contains complete route shapes and schedule information, making it suitable for transport analysis.

Key findings from quality assessment:
- No duplicate route names
- Complete shape geometry for all routes
- All departure times properly formatted
- Missing stop-to-stop distances (addressed through calculation)

### Core Data Components Explored

**Agency Information**
The dataset represents services provided by approved SACCOs (Savings and Credit Cooperative Organizations) operating under University of Nairobi coordination.

**Route Structure**
- 136 unique routes covering major corridors
- All routes classified as bus service (route_type = 3)
- Routes connect central business district to residential areas
- Average of 31.5 stops per route

**Stop Distribution**
- 4,284 total stops across Nairobi
- 2,474 unique stop names (some locations served by multiple routes)
- Common stop names include major landmarks like Tuskys, Naivas, and Equity Bank locations
- Stops concentrated in high-density corridors

**Service Patterns**
The analysis examines service frequency throughout the day:
- Peak hours: 6 AM and 3 PM (3,168 trips per hour)
- Off-peak: 9 AM (1,056 trips per hour)
- Service operates on daily schedules with some holiday exceptions

### Interactive Mapping

The notebook creates several interactive maps to visualize the transport network:

1. **Complete Route Network**: Shows all 136 routes with route numbers labeled at midpoints
2. **Stop Density Maps**: Displays the distribution of stops across the city
3. **Route Detail Views**: Examines individual route patterns, including the stop sequence for sample routes like the Ruaka-Ruiru line

### Service Analysis

**Route Coverage**
Routes primarily serve radial patterns connecting outlying areas to the central business district. Major corridors include:
- North-South connections through the city center
- East-West routes linking residential areas
- Orbital routes connecting suburbs without passing through downtown

**Temporal Patterns**
Service intensity varies significantly throughout the day:
- Morning and evening peaks serve commuter demand
- Midday service operates at reduced frequency
- Weekend and holiday service follows modified schedules

## Key Insights

### Network Characteristics
- Hub-and-spoke pattern centered on Nairobi CBD
- High stop density in central areas
- Lower frequency service in peripheral areas
- Route overlaps provide redundancy in core corridors

### Service Quality Indicators
- Consistent morning and evening peak service
- Significant frequency reduction during midday hours
- Well-distributed coverage across metropolitan area
- Integration challenges between different route operators

### Data Completeness
- Excellent geographic coverage with precise stop coordinates
- Comprehensive schedule data for frequency analysis
- Complete route geometry for mapping applications
- Some gaps in stop-to-stop travel time data

## Applications and Use Cases

This GTFS analysis provides the foundation for several planning applications:
- Accessibility analysis for different neighborhoods
- Service gap identification
- Route optimization studies
- Integration planning for formal transit systems
- Equity analysis of transport provision

## Technical Notes

**Data Processing**
- GTFS validation using gtfs-kit library
- Spatial analysis with folium mapping
- Schedule analysis using pandas for temporal patterns
- Interactive visualization for exploration

**Quality Assurance**
- Automated validation of GTFS standards compliance
- Geographic coordinate verification
- Schedule consistency checks
- Route geometry validation

## Next Steps

This foundational analysis sets up subsequent investigations into:
- Population and demographic overlay analysis
- Traffic and congestion impact assessment
- Equity analysis across different ward areas
- Service frequency optimization recommendations

The clean, validated GTFS dataset serves as the backbone for comprehensive transport planning analysis throughout the project.