from http import HTTPStatus

import joblib
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import Field

from beer_color_prediction.config import MODELS_DIR


app = FastAPI(
    title="Beer Color Prediction API",
    description="API para predição da cor da cerveja",
    version="0.1.0",
    docs_url="/",
    redoc_url=None,
)


class Prediction(BaseModel):
    roast_amount_kg: float = Field(
        36.22, title="Roast amount (kg)", description="Roast amount (kg)"
    )
    first_malt_amount_kg: float = Field(
        14037.08, title="1st malt amount (kg)", description="1st malt amount (kg)"
    )
    second_malt_amount_kg: float = Field(
        6382.39, title="2nd malt amount (kg)", description="2nd malt amount (kg)"
    )
    mt_temperature: float = Field(
        67.31, title="MT - Temperature", description="MT - Temperature"
    )
    mt_time: float = Field(6711.59, title="MT - Time", description="MT - Time")
    wk_temperature: float = Field(
        105.24, title="WK - Temperature", description="WK - Temperature"
    )
    wk_steam: float = Field(6791.16, title="WK - Steam", description="WK - Steam")
    wk_time: float = Field(6704.51, title="WK - Time", description="WK - Time")
    total_cold_wort: float = Field(
        962.12, title="Total cold wort", description="Total cold wort"
    )
    ph: float = Field(5.60, title="pH", description="pH")
    extract: float = Field(15.30, title="Extract", description="Extract")
    woc_time: float = Field(3180.39, title="WOC - Time", description="WOC - Time")
    whp_transfer_time: float = Field(
        749.97, title="WHP Transfer - Time", description="WHP Transfer - Time"
    )
    whp_rest_time: float = Field(
        749.97, title="WHP Rest - Time", description="WHP Rest - Time"
    )
    first_malt_color: float = Field(
        14.49, title="1st malt color", description="1st malt color"
    )
    second_malt_color: float = Field(
        6.02, title="2nd malt color", description="2nd malt color"
    )


class Message(BaseModel):
    message: str


# global apenas para simplicidade
model = joblib.load(f"{MODELS_DIR}/model.joblib")


@app.post("/predict", status_code=HTTPStatus.OK)
def predict_color(prediction: Prediction):
    """Realiza a predição da cor da cerveja"""
    X = prediction.model_dump()
    color = model.predict([list(X.values())])[0]
    return {"color": color}


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "API de exemplo"}


@app.get("/health", status_code=HTTPStatus.OK, response_model=Message)
def health():
    return {"message": "API is running"}
