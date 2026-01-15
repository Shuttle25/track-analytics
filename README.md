# Track Analytics

Compare and analyze OsmAnd GPX tracks.

## Features

- **Distance & elevation metrics** — total distance, elevation gain/loss, min/max elevation
- **Speed & timing** — duration, average/max speed, moving time
- **Route overlap analysis** — find shared and unique segments between tracks
- **Visual charts** — route map overlay, elevation profiles, speed profiles

## Installation

```bash
git clone https://github.com/Shuttle25/track-analytics.git
cd track-analytics
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
# Compare two tracks
track-analytics track1.gpx track2.gpx

# Save chart to custom path
track-analytics track1.gpx track2.gpx -o comparison.png

# Text output only (no chart)
track-analytics track1.gpx track2.gpx --no-chart

# Adjust overlap detection threshold (default: 50 meters)
track-analytics track1.gpx track2.gpx --overlap-threshold 100
```

## Example Output

```
======================================================================
TRACK COMPARISON
======================================================================

Track 1: Morning_Ride
Track 2: Evening_Ride

  Metric                          Track 1        Track 2     Difference
----------------------------------------------------------------------
  Distance                       13.47 km       13.37 km       +0.09 km
  Track points                        213            208             +5

ELEVATION
----------------------------------------------------------------------
  Min elevation                      55 m           68 m          -13 m
  Max elevation                     102 m          116 m          -14 m
  Total ascent                      330 m          225 m         +105 m
  Total descent                     338 m          217 m         +121 m

ROUTE OVERLAP ANALYSIS
----------------------------------------------------------------------
  Morning_Ride:
    Overlapping:  8.52 km (63.2%)
    Unique:       4.95 km

  Evening_Ride:
    Overlapping:  9.01 km (67.3%)
    Unique:       4.37 km
```

## License

MIT
