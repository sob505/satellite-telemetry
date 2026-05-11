#!/usr/bin/env python
"""
Generate Markdown knowledge base from ESA Mission 1 parquet telemetry files.

Usage:
    python make_markdown.py ^
        --parquet-dir data/parquet ^
        --metadata channel_metadata.csv ^
        --output esa_mission1_kb.md
"""

from pathlib import Path
import argparse
import pandas as pd


def load_channel_metadata(metadata_file: Path) -> dict:
    """
    Load channel metadata CSV.

    Returns:
        Dict keyed by channel name.
    """
    metadata_df = pd.read_csv(metadata_file)

    metadata = {}

    for _, row in metadata_df.iterrows():
        channel = str(row["Channel"]).strip()

        metadata[channel] = {
            "subsystem": row.get("Subsystem", "unknown"),
            "physical_unit": row.get("Physical Unit", "unknown"),
            "group": row.get("Group", "unknown"),
            "categorical": row.get("Categorical", "unknown"),
        }

    return metadata


def summarize_parquet(parquet_file: Path) -> dict:
    """
    Compute summary statistics for a parquet telemetry channel.
    """
    df = pd.read_parquet(parquet_file)

    column_name = df.columns[0]
    series = pd.to_numeric(df[column_name], errors="coerce")

    return {
        "rows": len(df),
        "missing": int(series.isna().sum()),
        "mean": float(series.mean()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),
        "first_values": series.head(10).tolist(),
    }


def build_markdown(
        parquet_dir: Path,
        metadata: dict,
        output_file: Path,
):
    """
    Build structured markdown knowledge base.
    """

    parquet_files = sorted(parquet_dir.glob("*.parquet"))

    lines = []

    lines.append("# ESA Mission 1 Telemetry Knowledge Base\n")
    lines.append(
        "Structured telemetry channel documentation for RAG systems.\n"
    )

    lines.append("## Dataset Overview\n")
    lines.append(f"- Total channels: {len(parquet_files)}")
    lines.append("- Data format: Apache Parquet")
    lines.append("- Source: ESA Mission 1 telemetry dataset")
    lines.append("- Purpose: Satellite telemetry analysis and modeling\n")

    for parquet_file in parquet_files:
        channel_name = parquet_file.stem

        print(f"Processing {channel_name}...")

        stats = summarize_parquet(parquet_file)

        meta = metadata.get(channel_name, {})

        subsystem = meta.get("subsystem", "unknown")
        physical_unit = meta.get("physical_unit", "unknown")
        group = meta.get("group", "unknown")
        categorical = meta.get("categorical", "unknown")

        lines.append(f"\n# {channel_name}\n")

        lines.append("## Metadata\n")
        lines.append(f"- Channel: {channel_name}")
        lines.append(f"- Subsystem: {subsystem}")
        lines.append(f"- Physical Unit: {physical_unit}")
        lines.append(f"- Group: {group}")
        lines.append(f"- Categorical: {categorical}")
        lines.append(f"- File: `{parquet_file.name}`\n")

        lines.append("## Data Statistics\n")
        lines.append(f"- Rows: {stats['rows']:,}")
        lines.append(f"- Missing Values: {stats['missing']:,}")
        lines.append(f"- Mean: {stats['mean']:.6f}")
        lines.append(f"- Standard Deviation: {stats['std']:.6f}")
        lines.append(f"- Minimum: {stats['min']:.6f}")
        lines.append(f"- Maximum: {stats['max']:.6f}\n")

        lines.append("## Sample Values\n")

        for value in stats["first_values"]:
            lines.append(f"- {value}")

        lines.append("\n## RAG Notes\n")
        lines.append(
            f"- {channel_name} belongs to {subsystem}"
        )
        lines.append(
            f"- Uses physical measurement category {physical_unit}"
        )
        lines.append(
            f"- Associated with telemetry group {group}"
        )
        lines.append(
            "- Data stored as time-series telemetry values"
        )
        lines.append(
            "- Suitable for trend analysis and forecasting\n"
        )

    output_file.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print(f"\n✓ Markdown knowledge base saved to:")
    print(output_file)


def main():
    parser = argparse.ArgumentParser(
        description="Generate ESA telemetry markdown KB"
    )

    parser.add_argument(
        "--parquet-dir",
        default="data/parquet",
        help="Directory containing parquet files"
    )

    parser.add_argument(
        "--metadata",
        default="data/channels.csv"
    )

    parser.add_argument(
        "--output",
        default="data/summary.md",
        help="Output markdown file"
    )

    args = parser.parse_args()

    parquet_dir = Path(args.parquet_dir)
    metadata_file = Path(args.metadata)
    output_file = Path(args.output)

    metadata = load_channel_metadata(metadata_file)

    build_markdown(
        parquet_dir=parquet_dir,
        metadata=metadata,
        output_file=output_file,
    )


if __name__ == "__main__":
    main()