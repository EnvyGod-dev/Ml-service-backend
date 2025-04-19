import pickle
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "ml_model.pkl")
encoder_path = os.path.join(BASE_DIR, "label_encoders.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

with open(encoder_path, "rb") as f:
    label_encoders = pickle.load(f)

def preprocess_data(data):
    df = pd.DataFrame([data])
    categorical_columns = ['maker', 'car_name', 'fuel_type']
    for col in categorical_columns:
        le = label_encoders[col]
        if data[col] not in le.classes_:
            raise ValueError(f"{col} contains unknown label: {data[col]}")
        df[col] = le.transform([data[col]])[0]
    return df

def predict_price(data):
    processed_data = preprocess_data(data)
    prediction = model.predict(processed_data)
    return round(prediction[0], 2)
