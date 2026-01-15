"""Track metrics calculation: distance, elevation, speed, duration."""

from dataclasses import dataclass
from datetime import timedelta

from haversine import haversine, Unit

from .gpx_parser import Track, TrackPoint


@dataclass
class ElevationMetrics:
    """Elevation statistics for a track."""

    min_elevation: float
    max_elevation: float
    total_ascent: float
    total_descent: float

    @property
    def elevation_range(self) -> float:
        return self.max_elevation - self.min_elevation


@dataclass
class SpeedMetrics:
    """Speed and timing statistics for a track."""

    duration: timedelta
    avg_speed_kmh: float
    max_speed_kmh: float
    moving_time: timedelta
    avg_moving_speed_kmh: float


@dataclass
class TrackMetrics:
    """All computed metrics for a track."""

    track_name: str
    total_distance_km: float
    point_count: int
    elevation: ElevationMetrics | None
    speed: SpeedMetrics | None


def _point_distance_km(p1: TrackPoint, p2: TrackPoint) -> float:
    """Calculate distance between two points in kilometers."""
    return haversine((p1.latitude, p1.longitude), (p2.latitude, p2.longitude), unit=Unit.KILOMETERS)


def calculate_total_distance(track: Track) -> float:
    """Calculate total track distance in kilometers."""
    if len(track.points) < 2:
        return 0.0

    total = 0.0
    for i in range(1, len(track.points)):
        total += _point_distance_km(track.points[i - 1], track.points[i])
    return total


def calculate_elevation_metrics(track: Track) -> ElevationMetrics | None:
    """Calculate elevation statistics."""
    if not track.has_elevation:
        return None

    elevations = [p.elevation for p in track.points if p.elevation is not None]
    if not elevations:
        return None

    total_ascent = 0.0
    total_descent = 0.0

    # Use a small threshold to filter GPS noise (2 meters)
    threshold = 2.0
    prev_elevation = elevations[0]

    for elevation in elevations[1:]:
        diff = elevation - prev_elevation
        if abs(diff) >= threshold:
            if diff > 0:
                total_ascent += diff
            else:
                total_descent += abs(diff)
            prev_elevation = elevation

    return ElevationMetrics(
        min_elevation=min(elevations),
        max_elevation=max(elevations),
        total_ascent=total_ascent,
        total_descent=total_descent,
    )


def calculate_speed_metrics(track: Track) -> SpeedMetrics | None:
    """Calculate speed and timing statistics."""
    if not track.has_timestamps or len(track.points) < 2:
        return None

    timed_points = [(p, p.time) for p in track.points if p.time is not None]
    if len(timed_points) < 2:
        return None

    # Sort by time
    timed_points.sort(key=lambda x: x[1])

    start_time = timed_points[0][1]
    end_time = timed_points[-1][1]
    duration = end_time - start_time

    if duration.total_seconds() == 0:
        return None

    total_distance = calculate_total_distance(track)
    avg_speed = (total_distance / duration.total_seconds()) * 3600  # km/h

    # Calculate max speed and moving time
    max_speed = 0.0
    moving_time = timedelta()
    moving_distance = 0.0
    min_moving_speed_kmh = 1.0  # Below 1 km/h is considered stopped

    for i in range(1, len(timed_points)):
        p1, t1 = timed_points[i - 1]
        p2, t2 = timed_points[i]

        segment_time = (t2 - t1).total_seconds()
        if segment_time <= 0:
            continue

        segment_dist = _point_distance_km(p1, p2)
        segment_speed = (segment_dist / segment_time) * 3600  # km/h

        # Filter out unrealistic speeds (GPS errors) - max 200 km/h
        if segment_speed > 200:
            continue

        max_speed = max(max_speed, segment_speed)

        if segment_speed >= min_moving_speed_kmh:
            moving_time += t2 - t1
            moving_distance += segment_dist

    avg_moving_speed = 0.0
    if moving_time.total_seconds() > 0:
        avg_moving_speed = (moving_distance / moving_time.total_seconds()) * 3600

    return SpeedMetrics(
        duration=duration,
        avg_speed_kmh=avg_speed,
        max_speed_kmh=max_speed,
        moving_time=moving_time,
        avg_moving_speed_kmh=avg_moving_speed,
    )


def calculate_metrics(track: Track) -> TrackMetrics:
    """Calculate all metrics for a track."""
    return TrackMetrics(
        track_name=track.name,
        total_distance_km=calculate_total_distance(track),
        point_count=len(track.points),
        elevation=calculate_elevation_metrics(track),
        speed=calculate_speed_metrics(track),
    )


def cumulative_distances(track: Track) -> list[float]:
    """Get cumulative distance at each point (for plotting)."""
    distances = [0.0]
    for i in range(1, len(track.points)):
        dist = _point_distance_km(track.points[i - 1], track.points[i])
        distances.append(distances[-1] + dist)
    return distances
