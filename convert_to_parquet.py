"""
Convert ESA pickle telemetry files directly to Parquet.

This avoids CSV entirely and preserves data types.
"""

from pathlib import Path
import pickle
import pandas as pd


def load_pickle(pickle_path: Path) -> pd.DataFrame:
    """Load DataFrame from pickle file."""
    with open(pickle_path, "rb") as f:
        data = pickle.load(f)

    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got {type(data)}")

    return data


def convert_pickle_to_parquet(pickle_path: Path, output_dir: Path) -> Path:
    """
    Convert a single pickle file to Parquet.
    """
    df = load_pickle(pickle_path)

    # Optional: normalize timestamps if present
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

    # Preserve channel structure
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{pickle_path.stem}.parquet"

    df.to_parquet(output_path, index=False, compression="snappy")

    print(f"Converted: {pickle_path} → {output_path}")

    return output_path


def convert_all_pickles(input_dir: str, output_dir: str) -> None:
    """
    Recursively convert all pickle files in ESA dataset.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    pickle_files = [
        p for p in input_dir.rglob("*")
        if p.is_file() and p.suffix != ".zip"
    ]

    print(f"Found {len(pickle_files)} files")

    for file in pickle_files:
        try:
            convert_pickle_to_parquet(file, output_dir)
        except Exception as e:
            print(f"Failed {file}: {e}")


if __name__ == "__main__":
    convert_all_pickles(
        input_dir="ESA-Mission1/ESA-Mission1/channels",
        output_dir="data/parquet"
    )