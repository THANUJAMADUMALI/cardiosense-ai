import joblib
import os

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "../../../ml-models/saved_models/xgb_model.pkl"
)

SCALER_PATH = os.path.join(
    BASE_DIR,
    "../../../ml-models/saved_models/scaler.pkl"
)

ENCODER_PATH = os.path.join(
    BASE_DIR,
    "../../../ml-models/saved_models/encoders.pkl"
)

# LOAD MODEL
xgb_model = joblib.load(MODEL_PATH)

# LOAD SCALER
scaler = joblib.load(SCALER_PATH)

# LOAD ENCODERS
encoders = joblib.load(ENCODER_PATH)