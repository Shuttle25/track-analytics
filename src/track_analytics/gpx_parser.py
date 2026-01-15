"""GPX file parsing for OsmAnd tracks."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import gpxpy
import gpxpy.gpx


@dataclass
class TrackPoint:
    """A single point in a track."""

    latitude: float
    longitude: float
    elevation: float | None
    time: datetime | None


@dataclass
class Track:
    """Parsed GPX track with all points."""

    name: str
    points: list[TrackPoint]
    source_file: Path

    @property
    def has_elevation(self) -> bool:
        return any(p.elevation is not None for p in self.points)

    @property
    def has_timestamps(self) -> bool:
        return any(p.time is not None for p in self.points)


def parse_gpx(file_path: Path) -> Track:
    """Parse a GPX file and return a Track object."""
    with open(file_path, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)

    points: list[TrackPoint] = []
    track_name = file_path.stem

    for track in gpx.tracks:
        if track.name:
            track_name = track.name
        for segment in track.segments:
            for point in segment.points:
                points.append(
                    TrackPoint(
                        latitude=point.latitude,
                        longitude=point.longitude,
                        elevation=point.elevation,
                        time=point.time,
                    )
                )

    # Also check for routes (some GPX files use routes instead of tracks)
    for route in gpx.routes:
        if route.name:
            track_name = route.name
        for point in route.points:
            points.append(
                TrackPoint(
                    latitude=point.latitude,
                    longitude=point.longitude,
                    elevation=point.elevation,
                    time=point.time,
                )
            )

    if not points:
        raise ValueError(f"No track points found in {file_path}")

    return Track(name=track_name, points=points, source_file=file_path)
