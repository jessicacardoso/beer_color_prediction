from pathlib import Path
import pandas as pd
import typer
from loguru import logger
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler
from beer_color_prediction.config import MODELS_DIR, PROCESSED_DATA_DIR
import joblib

app = typer.Typer()


def train(X, y):
    pipe = Pipeline(
        [
            ("imputer", SimpleImputer()),
            ("scaler", StandardScaler()),
            ("regressor", ExtraTreesRegressor(random_state=42)),
        ]
    )

    pipe = TransformedTargetRegressor(
        regressor=pipe,
        transformer=RobustScaler(),
    )

    return pipe.fit(X, y)


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = PROCESSED_DATA_DIR / "dataset.parquet",
    model_path: Path = MODELS_DIR / "model.joblib",
    # -----------------------------------------
):
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Training some model...")
    logger.info(f"Input path: {input_path}")
    df = pd.read_parquet(input_path)
    logger.info(f"Loaded dataset with shape {df.shape}")
    X = df.drop(columns=["color"])
    y = df["color"]

    logger.info("Training model...")
    model = train(X, y)

    logger.info(f"Saving model to {model_path}")
    joblib.dump(model, model_path)

    logger.success("Modeling training complete.")
    # -----------------------------------------


if __name__ == "__main__":
    app()
