# api/ml_model.py

import os
import pickle
import re
import pandas as pd
from django.conf import settings

# Project root where manage.py resides (and where artifacts are saved)
ARTIFACTS_DIR = settings.BASE_DIR

# Paths to the trained model and encoders
MODEL_PATH   = os.path.join(ARTIFACTS_DIR, 'ml_model.pkl')
ENCODER_PATH = os.path.join(ARTIFACTS_DIR, 'label_encoders.pkl')

# Load the trained model
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# Load the label encoders
with open(ENCODER_PATH, 'rb') as f:
    label_encoders = pickle.load(f)

print(f"[DEBUG] Loaded encoder keys: {list(label_encoders.keys())}")


def preprocess_data(data):
    """
    data: dict with keys registration_year, maker, car_name, fuel_type,
          engine_size, odometer, condition, chassis_id, colour
    returns: pandas DataFrame of features
    """
    df = pd.DataFrame([data])

    # Normalize text fields
    df['car_name']   = df['car_name'].astype(str).apply(
        lambda x: re.sub(r'\s+', ' ', x.strip().upper())
    )
    df['maker']      = df['maker'].astype(str).str.strip().str.upper()
    df['fuel_type']  = df['fuel_type'].astype(str).str.strip().str.upper()
    df['chassis_id'] = df['chassis_id'].astype(str).str.strip().str.upper()
    df['colour']     = df['colour'].astype(str).str.strip().str.upper()

    # Numeric conversions and validations
    for field in ['registration_year', 'engine_size', 'odometer', 'condition']:
        if field not in df.columns:
            raise ValueError(f"Missing required field: {field}")
        df[field] = pd.to_numeric(df[field], errors='coerce')
        if df[field].isnull().any():
            raise ValueError(f"Invalid numeric value in field: {field}")

    # Encode categorical fields
    for col in ['maker', 'car_name', 'fuel_type', 'chassis_id', 'colour']:
        if col not in label_encoders:
            raise KeyError(f"No encoder found for column: {col}")
        encoder = label_encoders[col]
        value = df.at[0, col]
        if value not in encoder.classes_:
            raise ValueError(f"Unknown label '{value}' in column '{col}'")
        df[col] = encoder.transform(df[col])

    # Return features in the order the model expects
    feature_order = [
        'registration_year', 'maker', 'car_name', 'fuel_type',
        'engine_size', 'odometer', 'condition', 'chassis_id', 'colour'
    ]
    return df[feature_order]


def predict_price(data):
    """Return the predicted price for a single car data dict"""
    X = preprocess_data(data)
    y_pred = model.predict(X)
    return round(float(y_pred[0]), 2)
