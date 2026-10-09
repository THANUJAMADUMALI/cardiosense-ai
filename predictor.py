import pandas as pd

from app.models.prediction import Prediction
from app.ml.load_model import (
    xgb_model,
    scaler,
    encoders
)


# =====================================
# NORMALIZE CATEGORICAL VALUES
# =====================================

def normalize_prediction_input(input_data):
    """Convert frontend values to exactly what the trained encoders expect."""

    # Resting ECG mapping
    restecg_map = {
        "normal": "normal",
        "st-t abnormality": "st-t abnormality",
        "left ventricular hypertrophy": "lv hypertrophy",
        "lv hypertrophy": "lv hypertrophy",
        "left ventricular": "lv hypertrophy"
    }

    # Chest pain mapping
    cp_map = {
        "typical angina": "typical angina",
        "atypical angina": "atypical angina",
        "non-anginal": "non-anginal",
        "asymptomatic": "asymptomatic"
    }

    # Slope mapping
    slope_map = {
        "upsloping": "upsloping",
        "flat": "flat",
        "downsloping": "downsloping"
    }

    # Thal mapping
    thal_map = {
        "normal": "normal",
        "fixed defect": "fixed defect",
        "reversable defect": "reversable defect"
    }

    input_data["restecg"] = input_data["restecg"].replace(restecg_map)
    input_data["cp"] = input_data["cp"].replace(cp_map)
    input_data["slope"] = input_data["slope"].replace(slope_map)
    input_data["thal"] = input_data["thal"].replace(thal_map)

    return input_data


# =====================================
# PREDICT HEART RISK
# =====================================

def predict_heart_risk(data, db, patient_id):

    input_data = pd.DataFrame([{
        "age": data.age,
        "sex": data.sex,
        "cp": data.cp,
        "trestbps": data.trestbps,
        "chol": data.chol,
        "fbs": data.fbs,
        "restecg": data.restecg,
        "thalch": data.thalch,
        "exang": data.exang,
        "oldpeak": data.oldpeak,
        "slope": data.slope,
        "ca": data.ca,
        "thal": data.thal
    }])

    # ---------------------------------
    # Normalize values from frontend
    # ---------------------------------

    input_data = normalize_prediction_input(input_data)

    print("Normalized Input")
    print(input_data)

    # ---------------------------------
    # Encode categorical features
    # ---------------------------------

    categorical_columns = [
        "sex",
        "cp",
        "fbs",
        "restecg",
        "exang",
        "slope",
        "thal"
    ]

    for column in categorical_columns:
        encoder = encoders[column]

        if column not in ["fbs", "exang"]:
            input_data[column] = input_data[column].astype(str)

        # Helpful debug
        print(f"\nEncoding {column}")
        print("Input :", input_data[column].tolist())
        print("Classes:", encoder.classes_)

        input_data[column] = encoder.transform(input_data[column])

    # ---------------------------------
    # Scale
    # ---------------------------------

    scaled_data = scaler.transform(input_data)

    # ---------------------------------
    # Predict
    # ---------------------------------

    prediction = int(xgb_model.predict(scaled_data)[0])
    probabilities = xgb_model.predict_proba(scaled_data)[0]

    labels = {
        0: "No Risk",
        1: "Moderate Risk",
        2: "High Risk"
    }

    result = {
        "prediction": prediction,
        "risk_level": labels[prediction],

        # Decimal confidence (React multiplies by 100)
        "confidence_score": round(float(max(probabilities)), 4),

        "no_risk_probability": round(float(probabilities[0]), 4),
        "moderate_risk_probability": round(float(probabilities[1]), 4),
        "high_risk_probability": round(float(probabilities[2]), 4)
    }

    # ---------------------------------
    # Save prediction
    # ---------------------------------

    new_prediction = Prediction(
        patient_id=patient_id,
        prediction=result["prediction"],
        risk_level=result["risk_level"],

        # Database stores percentages
        confidence_score=result["confidence_score"] * 100,
        no_risk_probability=result["no_risk_probability"] * 100,
        moderate_risk_probability=result["moderate_risk_probability"] * 100,
        high_risk_probability=result["high_risk_probability"] * 100
    )

    db.add(new_prediction)
    db.commit()

    return result