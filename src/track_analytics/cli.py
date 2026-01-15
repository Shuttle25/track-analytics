"""Command-line interface for track comparison."""

import argparse
import sys
from pathlib import Path

from .gpx_parser import parse_gpx
from .metrics import calculate_metrics
from .overlap import analyze_overlap
from .output import format_metrics_comparison, format_overlap_result
from .charts import generate_comparison_charts


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="track-analytics",
        description="Compare and analyze OsmAnd GPX tracks",
    )

    parser.add_argument(
        "track1",
        type=Path,
        help="Path to first GPX file",
    )
    parser.add_argument(
        "track2",
        type=Path,
        help="Path to second GPX file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output path for comparison chart (PNG). Default: comparison.png",
    )
    parser.add_argument(
        "--no-chart",
        action="store_true",
        help="Skip chart generation",
    )
    parser.add_argument(
        "--overlap-threshold",
        type=float,
        default=50.0,
        help="Distance threshold in meters for overlap detection (default: 50)",
    )

    args = parser.parse_args()

    # Validate input files
    if not args.track1.exists():
        print(f"Error: File not found: {args.track1}", file=sys.stderr)
        return 1
    if not args.track2.exists():
        print(f"Error: File not found: {args.track2}", file=sys.stderr)
        return 1

    # Parse tracks
    try:
        track1 = parse_gpx(args.track1)
        track2 = parse_gpx(args.track2)
    except Exception as e:
        print(f"Error parsing GPX file: {e}", file=sys.stderr)
        return 1

    # Calculate metrics
    metrics1 = calculate_metrics(track1)
    metrics2 = calculate_metrics(track2)

    # Print comparison
    print(format_metrics_comparison(metrics1, metrics2))

    # Analyze overlap
    overlap = analyze_overlap(track1, track2, threshold_meters=args.overlap_threshold)
    print(format_overlap_result(overlap, track1.name, track2.name))

    # Generate charts
    if not args.no_chart:
        output_path = args.output or Path("comparison.png")
        try:
            generate_comparison_charts(track1, track2, output_path)
            print(f"Chart saved to: {output_path}")
        except Exception as e:
            print(f"Warning: Could not generate chart: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
