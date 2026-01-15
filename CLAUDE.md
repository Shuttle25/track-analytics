# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Track Analytics is a Python CLI tool for comparing OsmAnd GPX tracks. It analyzes distance, elevation, speed/timing metrics, and route overlap between two tracks, outputting both text summaries and visual charts.

## Commands

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .

# Run the tool
track-analytics track1.gpx track2.gpx

# Run without chart generation
track-analytics track1.gpx track2.gpx --no-chart

# Custom output path and overlap threshold
track-analytics track1.gpx track2.gpx -o output.png --overlap-threshold 100
```

## Architecture

```
src/track_analytics/
├── gpx_parser.py   # GPX parsing, Track and TrackPoint dataclasses
├── metrics.py      # Distance, elevation, speed calculations
├── overlap.py      # Route overlap analysis using spatial proximity
├── output.py       # Text formatting for terminal output
├── charts.py       # Matplotlib chart generation
└── cli.py          # Argument parsing and main workflow
```

Key data flow: `parse_gpx()` → `Track` → `calculate_metrics()` / `analyze_overlap()` → formatters/charts

## Key Dependencies

- `gpxpy`: GPX file parsing
- `haversine`: Geographic distance calculations
- `matplotlib`: Chart generation
- `numpy`: Numerical operations
