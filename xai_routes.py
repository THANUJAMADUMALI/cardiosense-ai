from fastapi import APIRouter

from app.schemas.prediction_schema import PredictionCreate

from app.xai.shap_explainer import explain_prediction

router = APIRouter(
    prefix="/xai",
    tags=["Explainable AI"]
)

@router.post("/")
def explain_ai(data: PredictionCreate):

    result = explain_prediction(data)

    return result