"""Route overlap analysis between two tracks."""

from dataclasses import dataclass

from haversine import haversine, Unit

from .gpx_parser import Track, TrackPoint


@dataclass
class OverlapResult:
    """Results of overlap analysis between two tracks."""

    track1_overlap_km: float
    track1_overlap_percent: float
    track2_overlap_km: float
    track2_overlap_percent: float
    shared_distance_km: float
    track1_unique_km: float
    track2_unique_km: float


def _find_nearest_point_distance(point: TrackPoint, track: Track) -> float:
    """Find the minimum distance from a point to any point in a track."""
    min_dist = float("inf")
    for tp in track.points:
        dist = haversine(
            (point.latitude, point.longitude),
            (tp.latitude, tp.longitude),
            unit=Unit.METERS,
        )
        min_dist = min(min_dist, dist)
    return min_dist


def _segment_distance_km(p1: TrackPoint, p2: TrackPoint) -> float:
    """Calculate distance between two points in kilometers."""
    return haversine(
        (p1.latitude, p1.longitude),
        (p2.latitude, p2.longitude),
        unit=Unit.KILOMETERS,
    )


def analyze_overlap(
    track1: Track,
    track2: Track,
    threshold_meters: float = 50.0,
) -> OverlapResult:
    """
    Analyze how much two tracks overlap.

    A segment is considered overlapping if its midpoint is within
    threshold_meters of any point on the other track.

    Args:
        track1: First track
        track2: Second track
        threshold_meters: Distance threshold for considering points as overlapping

    Returns:
        OverlapResult with overlap statistics
    """
    # Calculate overlap for track1 (how much of track1 is near track2)
    track1_total_km = 0.0
    track1_overlap_km = 0.0

    for i in range(1, len(track1.points)):
        p1 = track1.points[i - 1]
        p2 = track1.points[i]
        segment_dist = _segment_distance_km(p1, p2)
        track1_total_km += segment_dist

        # Check midpoint of segment
        mid_lat = (p1.latitude + p2.latitude) / 2
        mid_lon = (p1.longitude + p2.longitude) / 2
        mid_point = TrackPoint(mid_lat, mid_lon, None, None)

        if _find_nearest_point_distance(mid_point, track2) <= threshold_meters:
            track1_overlap_km += segment_dist

    # Calculate overlap for track2 (how much of track2 is near track1)
    track2_total_km = 0.0
    track2_overlap_km = 0.0

    for i in range(1, len(track2.points)):
        p1 = track2.points[i - 1]
        p2 = track2.points[i]
        segment_dist = _segment_distance_km(p1, p2)
        track2_total_km += segment_dist

        mid_lat = (p1.latitude + p2.latitude) / 2
        mid_lon = (p1.longitude + p2.longitude) / 2
        mid_point = TrackPoint(mid_lat, mid_lon, None, None)

        if _find_nearest_point_distance(mid_point, track1) <= threshold_meters:
            track2_overlap_km += segment_dist

    # Calculate percentages
    track1_overlap_pct = (track1_overlap_km / track1_total_km * 100) if track1_total_km > 0 else 0.0
    track2_overlap_pct = (track2_overlap_km / track2_total_km * 100) if track2_total_km > 0 else 0.0

    # Shared distance is approximated as the average of overlapping portions
    shared_km = (track1_overlap_km + track2_overlap_km) / 2

    return OverlapResult(
        track1_overlap_km=track1_overlap_km,
        track1_overlap_percent=track1_overlap_pct,
        track2_overlap_km=track2_overlap_km,
        track2_overlap_percent=track2_overlap_pct,
        shared_distance_km=shared_km,
        track1_unique_km=track1_total_km - track1_overlap_km,
        track2_unique_km=track2_total_km - track2_overlap_km,
    )
