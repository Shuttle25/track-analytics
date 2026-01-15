"""Text output formatting for track comparison."""

from datetime import timedelta

from .metrics import TrackMetrics
from .overlap import OverlapResult


def _format_duration(td: timedelta) -> str:
    """Format a timedelta as HH:MM:SS."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes:02d}m {seconds:02d}s"
    elif minutes > 0:
        return f"{minutes}m {seconds:02d}s"
    else:
        return f"{seconds}s"


def _format_row(label: str, val1: str, val2: str, diff: str = "") -> str:
    """Format a comparison row."""
    return f"  {label:<24} {val1:>14} {val2:>14} {diff:>14}"


def format_metrics_comparison(metrics1: TrackMetrics, metrics2: TrackMetrics) -> str:
    """Format a side-by-side comparison of two tracks."""
    lines = []

    # Header
    lines.append("=" * 70)
    lines.append("TRACK COMPARISON")
    lines.append("=" * 70)
    lines.append("")

    # Track names
    lines.append(f"Track 1: {metrics1.track_name}")
    lines.append(f"Track 2: {metrics2.track_name}")
    lines.append("")

    # Column headers
    lines.append(_format_row("Metric", "Track 1", "Track 2", "Difference"))
    lines.append("-" * 70)

    # Distance
    dist_diff = metrics1.total_distance_km - metrics2.total_distance_km
    diff_str = f"{dist_diff:+.2f} km"
    lines.append(
        _format_row(
            "Distance",
            f"{metrics1.total_distance_km:.2f} km",
            f"{metrics2.total_distance_km:.2f} km",
            diff_str,
        )
    )

    # Points
    point_diff = metrics1.point_count - metrics2.point_count
    lines.append(
        _format_row(
            "Track points",
            str(metrics1.point_count),
            str(metrics2.point_count),
            f"{point_diff:+d}",
        )
    )

    # Elevation metrics
    if metrics1.elevation or metrics2.elevation:
        lines.append("")
        lines.append("ELEVATION")
        lines.append("-" * 70)

        e1 = metrics1.elevation
        e2 = metrics2.elevation

        if e1 and e2:
            lines.append(
                _format_row(
                    "Min elevation",
                    f"{e1.min_elevation:.0f} m",
                    f"{e2.min_elevation:.0f} m",
                    f"{e1.min_elevation - e2.min_elevation:+.0f} m",
                )
            )
            lines.append(
                _format_row(
                    "Max elevation",
                    f"{e1.max_elevation:.0f} m",
                    f"{e2.max_elevation:.0f} m",
                    f"{e1.max_elevation - e2.max_elevation:+.0f} m",
                )
            )
            lines.append(
                _format_row(
                    "Total ascent",
                    f"{e1.total_ascent:.0f} m",
                    f"{e2.total_ascent:.0f} m",
                    f"{e1.total_ascent - e2.total_ascent:+.0f} m",
                )
            )
            lines.append(
                _format_row(
                    "Total descent",
                    f"{e1.total_descent:.0f} m",
                    f"{e2.total_descent:.0f} m",
                    f"{e1.total_descent - e2.total_descent:+.0f} m",
                )
            )
        else:
            val1 = "available" if e1 else "N/A"
            val2 = "available" if e2 else "N/A"
            lines.append(_format_row("Elevation data", val1, val2))

    # Speed/timing metrics
    if metrics1.speed or metrics2.speed:
        lines.append("")
        lines.append("TIMING & SPEED")
        lines.append("-" * 70)

        s1 = metrics1.speed
        s2 = metrics2.speed

        if s1 and s2:
            dur_diff = s1.duration - s2.duration
            lines.append(
                _format_row(
                    "Duration",
                    _format_duration(s1.duration),
                    _format_duration(s2.duration),
                    _format_duration(dur_diff) if dur_diff >= timedelta() else f"-{_format_duration(-dur_diff)}",
                )
            )
            lines.append(
                _format_row(
                    "Moving time",
                    _format_duration(s1.moving_time),
                    _format_duration(s2.moving_time),
                    "",
                )
            )
            lines.append(
                _format_row(
                    "Avg speed",
                    f"{s1.avg_speed_kmh:.1f} km/h",
                    f"{s2.avg_speed_kmh:.1f} km/h",
                    f"{s1.avg_speed_kmh - s2.avg_speed_kmh:+.1f} km/h",
                )
            )
            lines.append(
                _format_row(
                    "Avg moving speed",
                    f"{s1.avg_moving_speed_kmh:.1f} km/h",
                    f"{s2.avg_moving_speed_kmh:.1f} km/h",
                    f"{s1.avg_moving_speed_kmh - s2.avg_moving_speed_kmh:+.1f} km/h",
                )
            )
            lines.append(
                _format_row(
                    "Max speed",
                    f"{s1.max_speed_kmh:.1f} km/h",
                    f"{s2.max_speed_kmh:.1f} km/h",
                    f"{s1.max_speed_kmh - s2.max_speed_kmh:+.1f} km/h",
                )
            )
        else:
            val1 = "available" if s1 else "N/A"
            val2 = "available" if s2 else "N/A"
            lines.append(_format_row("Timing data", val1, val2))

    lines.append("")
    return "\n".join(lines)


def format_overlap_result(overlap: OverlapResult, name1: str, name2: str) -> str:
    """Format overlap analysis results."""
    lines = []

    lines.append("ROUTE OVERLAP ANALYSIS")
    lines.append("-" * 70)
    lines.append(f"  {name1}:")
    lines.append(f"    Overlapping:  {overlap.track1_overlap_km:.2f} km ({overlap.track1_overlap_percent:.1f}%)")
    lines.append(f"    Unique:       {overlap.track1_unique_km:.2f} km")
    lines.append("")
    lines.append(f"  {name2}:")
    lines.append(f"    Overlapping:  {overlap.track2_overlap_km:.2f} km ({overlap.track2_overlap_percent:.1f}%)")
    lines.append(f"    Unique:       {overlap.track2_unique_km:.2f} km")
    lines.append("")
    lines.append(f"  Approximate shared route: {overlap.shared_distance_km:.2f} km")
    lines.append("")

    return "\n".join(lines)
