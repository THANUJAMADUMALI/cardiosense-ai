from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.prediction_schema import PredictionCreate

from app.ml.predictor import predict_heart_risk

router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)

@router.post("/")
def predict(
    data: PredictionCreate,
    db: Session = Depends(get_db)
):

    
    print("Incoming Prediction:", data.model_dump())

    result = predict_heart_risk(
        data,
        db,
        patient_id=data.patient_id
    )

    return result