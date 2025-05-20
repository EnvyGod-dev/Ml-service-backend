import os
import pickle
import re
import numpy as np
import pandas as pd
from django.conf import settings

# Project root where artifacts live
ARTIFACTS_DIR = settings.BASE_DIR
MODEL_PATH   = os.path.join(ARTIFACTS_DIR, 'ml_model.pkl')
ENCODER_PATH = os.path.join(ARTIFACTS_DIR, 'label_encoders.pkl')

# Load trained model and encoders
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)
with open(ENCODER_PATH, 'rb') as f:
    label_encoders = pickle.load(f)

print(f"[DEBUG] Loaded encoder keys: {list(label_encoders.keys())}")


def preprocess_data(data):
    """
    Normalize and encode a single car data dict.
    Allows unseen categorical labels by dynamically appending them to the encoder.
    """
    df = pd.DataFrame([data])

    # 1) Normalize text fields (strip NBSP, uppercase, collapse whitespace)
    for col in ['car_name', 'maker', 'fuel_type', 'chassis_id', 'colour']:
        df[col] = df[col].astype(str).apply(
            lambda x: re.sub(r"\s+", " ", x.replace('\xa0', ' ').strip().upper())
        )

    # 2) Numeric fields conversion & validation
    for field in ['registration_year', 'engine_size', 'odometer', 'condition']:
        if field not in df.columns:
            raise ValueError(f"Missing required field: {field}")
        df[field] = pd.to_numeric(df[field], errors='coerce')
        if df[field].isnull().any():
            raise ValueError(f"Invalid numeric value in field: {field}")

    # 3) Encode categorical, append unseen labels
    for col in ['maker', 'car_name', 'fuel_type', 'chassis_id', 'colour']:
        encoder = label_encoders[col]
        val = df.at[0, col]
        if val not in encoder.classes_:
            # dynamically extend encoder to include new label
            encoder.classes_ = np.append(encoder.classes_, val)
        df[col] = encoder.transform(df[col])

    # 4) Return features in model's expected order
    feature_cols = [
        'registration_year', 'maker', 'car_name', 'fuel_type',
        'engine_size', 'odometer', 'condition', 'chassis_id', 'colour'
    ]
    return df[feature_cols]


def predict_price(data):
    """Predict price for a single car data dict."""
    X = preprocess_data(data)
    y_pred = model.predict(X)
    return round(float(y_pred[0]), 2)
