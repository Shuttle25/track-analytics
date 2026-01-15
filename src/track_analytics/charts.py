"""Chart generation for track comparison visualization."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .gpx_parser import Track
from .metrics import cumulative_distances


def generate_comparison_charts(
    track1: Track,
    track2: Track,
    output_path: Path,
) -> None:
    """
    Generate comparison charts for two tracks.

    Creates a multi-panel figure with:
    - Route map overlay
    - Elevation profiles
    - Speed profiles (if timing data available)
    """
    has_elevation = track1.has_elevation and track2.has_elevation
    has_timing = track1.has_timestamps and track2.has_timestamps

    # Determine number of subplots
    num_plots = 1  # Always have route map
    if has_elevation:
        num_plots += 1
    if has_timing:
        num_plots += 1

    fig, axes = plt.subplots(num_plots, 1, figsize=(12, 4 * num_plots))
    if num_plots == 1:
        axes = [axes]

    plot_idx = 0

    # Route map
    ax = axes[plot_idx]
    _plot_route_map(ax, track1, track2)
    plot_idx += 1

    # Elevation profile
    if has_elevation:
        ax = axes[plot_idx]
        _plot_elevation_profiles(ax, track1, track2)
        plot_idx += 1

    # Speed profile
    if has_timing:
        ax = axes[plot_idx]
        _plot_speed_profiles(ax, track1, track2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def _plot_route_map(ax: plt.Axes, track1: Track, track2: Track) -> None:
    """Plot route map with both tracks overlaid."""
    lats1 = [p.latitude for p in track1.points]
    lons1 = [p.longitude for p in track1.points]
    lats2 = [p.latitude for p in track2.points]
    lons2 = [p.longitude for p in track2.points]

    ax.plot(lons1, lats1, "b-", linewidth=2, label=track1.name, alpha=0.7)
    ax.plot(lons2, lats2, "r-", linewidth=2, label=track2.name, alpha=0.7)

    # Mark start and end points
    ax.plot(lons1[0], lats1[0], "go", markersize=10, label="Start (Track 1)")
    ax.plot(lons1[-1], lats1[-1], "g^", markersize=10, label="End (Track 1)")
    ax.plot(lons2[0], lats2[0], "mo", markersize=8)
    ax.plot(lons2[-1], lats2[-1], "m^", markersize=8)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Route Comparison")
    ax.legend(loc="best")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)


def _plot_elevation_profiles(ax: plt.Axes, track1: Track, track2: Track) -> None:
    """Plot elevation profiles for both tracks."""
    dist1 = cumulative_distances(track1)
    elev1 = [p.elevation for p in track1.points]

    dist2 = cumulative_distances(track2)
    elev2 = [p.elevation for p in track2.points]

    ax.plot(dist1, elev1, "b-", linewidth=1.5, label=track1.name, alpha=0.8)
    ax.plot(dist2, elev2, "r-", linewidth=1.5, label=track2.name, alpha=0.8)

    ax.fill_between(dist1, elev1, alpha=0.2, color="blue")
    ax.fill_between(dist2, elev2, alpha=0.2, color="red")

    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Elevation (m)")
    ax.set_title("Elevation Profiles")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)


def _plot_speed_profiles(ax: plt.Axes, track1: Track, track2: Track) -> None:
    """Plot speed profiles for both tracks."""
    speeds1, dist1 = _calculate_segment_speeds(track1)
    speeds2, dist2 = _calculate_segment_speeds(track2)

    if speeds1:
        ax.plot(dist1, speeds1, "b-", linewidth=1, label=track1.name, alpha=0.7)
    if speeds2:
        ax.plot(dist2, speeds2, "r-", linewidth=1, label=track2.name, alpha=0.7)

    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title("Speed Profiles")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)


def _calculate_segment_speeds(track: Track) -> tuple[list[float], list[float]]:
    """Calculate speed for each segment of the track."""
    from haversine import haversine, Unit

    speeds = []
    distances = [0.0]

    timed_points = [(p, p.time) for p in track.points if p.time is not None]
    if len(timed_points) < 2:
        return [], []

    for i in range(1, len(timed_points)):
        p1, t1 = timed_points[i - 1]
        p2, t2 = timed_points[i]

        segment_time = (t2 - t1).total_seconds()
        if segment_time <= 0:
            continue

        segment_dist = haversine(
            (p1.latitude, p1.longitude),
            (p2.latitude, p2.longitude),
            unit=Unit.KILOMETERS,
        )

        speed = (segment_dist / segment_time) * 3600  # km/h

        # Filter unrealistic speeds
        if speed > 200:
            speed = speeds[-1] if speeds else 0

        speeds.append(speed)
        distances.append(distances[-1] + segment_dist)

    # Remove first distance entry to match speeds length
    return speeds, distances[1:]
