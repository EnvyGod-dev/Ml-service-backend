import pandas as pd
import pickle
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'ml_model.pkl')
encoder_path = os.path.join(BASE_DIR, 'label_encoders.pkl')

# Load trained model
with open(model_path, 'rb') as f:
    model = pickle.load(f)

with open(encoder_path, 'rb') as f:
    label_encoders = pickle.load(f)

def preprocess_data(data):
    df = pd.DataFrame([data])

    # Normalize text inputs
    df['car_name'] = df['car_name'].astype(str).apply(lambda x: re.sub(r'\s+', ' ', x.strip().upper()))
    df['maker'] = df['maker'].astype(str).str.strip().str.upper()
    df['fuel_type'] = df['fuel_type'].astype(str).str.strip().str.upper()

    # Ensure numeric fields exist and are valid
    numeric_fields = ['registration_year', 'engine_size', 'odometer']
    for field in numeric_fields:
        if field not in df.columns:
            raise ValueError(f"Missing numeric field: {field}")
        df[field] = pd.to_numeric(df[field], errors='coerce')
        if df[field].isnull().any():
            raise ValueError(f"Invalid value in numeric field: {field}")

    # Encode categorical fields
    categorical_cols = ['maker', 'car_name', 'fuel_type']
    for col in categorical_cols:
        if col not in label_encoders:
            raise ValueError(f"No encoder found for column: {col}")
        value = df[col].iloc[0]
        if value not in label_encoders[col].classes_:
            raise ValueError(f"Unknown label '{value}' in column '{col}'")
        df[col] = label_encoders[col].transform([value])[0]

    # Select and return features in correct order
    return df[[
        'registration_year',
        'maker',
        'car_name',
        'fuel_type',
        'engine_size',
        'odometer'
    ]]
def predict_price(data):
    processed_data = preprocess_data(data)
    prediction = model.predict(processed_data)
    return round(prediction[0], 2)
