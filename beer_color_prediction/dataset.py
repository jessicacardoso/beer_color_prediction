from pathlib import Path
import pandas as pd
import typer
import re
from loguru import logger

from beer_color_prediction.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

app = typer.Typer()


def slugify(s):
    return re.sub(r"\W+", "_", s).lower().strip("_")


def preprocess_data(
    data: pd.DataFrame,
    handle_negative_values: str = "keep",
    handle_outliers: str = "keep",
    outlier_threshold: float = 1.5,
    lower_percentile: float = 0.05,
    upper_percentile: float = 0.95,
) -> pd.DataFrame:
    """Preprocesses the input DataFrame.

    Args:
        data (pd.DataFrame): Input DataFrame.
        handle_negative_values (str, optional): How to handle negative values. Defaults to "keep".
        Options: "keep", "replace_with_zero", "replace_with_nan", "drop".
        handle_outliers (str, optional): How to handle outliers. Defaults to "keep".
        Options: "keep", "clip", "replace_with_nan", "drop".
        outlier_threshold (float, optional): Threshold for outlier detection. Defaults to 1.5.
        lower_percentile (float, optional): Lower percentile for outlier detection. Defaults to 0.05.
        upper_percentile (float, optional): Upper percentile for outlier detection. Defaults to 0.95.

    Returns:
        pd.DataFrame: Preprocessed DataFrame.
    """

    data = data.drop(columns=["product", "roast_color"], errors="ignore")

    if handle_negative_values == "replace_with_zero":
        data = data.clip(lower=0)
    elif handle_negative_values == "replace_with_nan":
        data = data.where(data >= 0)
    elif handle_negative_values == "drop":
        data = data[(data >= 0).all(axis=1)]

    if (
        handle_outliers == "clip"
        or handle_outliers == "replace_with_nan"
        or handle_outliers == "drop"
    ):
        iqrs = data.quantile(upper_percentile) - data.quantile(lower_percentile)
        lower_bound = data.quantile(lower_percentile) - outlier_threshold * iqrs
        upper_bound = data.quantile(upper_percentile) + outlier_threshold * iqrs
        if handle_outliers == "clip":
            data = data.clip(lower=lower_bound, upper=upper_bound, axis=1)
        elif handle_outliers == "replace_with_nan":
            data = data.where((data >= lower_bound) & (data <= upper_bound))
        elif handle_outliers == "drop":
            data = data[((data >= lower_bound) & (data <= upper_bound)).all(axis=1)]

    return data


@app.command()
def main(
    input_path: Path = RAW_DATA_DIR / "dataset.csv",
    output_path: Path = PROCESSED_DATA_DIR / "dataset.parquet",
    # ----------------------------------------------
):
    logger.info("Processing dataset...")
    # Load the dataset
    df = pd.read_csv(input_path)
    df = df.drop(columns=["Unnamed: 0", "Date/Time"], errors="ignore")
    df = df.set_index("Job ID")
    df.columns = [slugify(col) for col in df.columns]
    df = df.dropna(subset=["color"])
    df = df.query("color >= 0")

    # Preprocess the dataset
    df = preprocess_data(
        df,
        handle_negative_values="replace_with_zero",
        handle_outliers="clip",
    )

    df.to_parquet(output_path)

    logger.success(f"Processed dataset saved to {output_path}")
    # -----------------------------------------


if __name__ == "__main__":
    app()
