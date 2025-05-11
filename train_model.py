import pandas as pd
import pickle
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, 'Data.csv')

# Load and clean CSV
df = pd.read_csv(file_path)

# Normalize car_name and other fields
df['maker'] = 'LEXUS'
df['car_name'] = df['Box of Modif.'].astype(str).apply(lambda x: re.sub(r'\s+', ' ', x.strip().upper()))
df['fuel_type'] = 'PETROL'
df['engine_size'] = pd.to_numeric(df['V,Engine CC'].astype(str).str.extract(r'(\d{3,5})')[0], errors='coerce')
df['odometer'] = pd.to_numeric(df['Mileage'].astype(str).str.replace(',', ''), errors='coerce')
df['registration_year'] = pd.to_numeric(df['year'], errors='coerce')
df['price'] = pd.to_numeric(df['sold price'].astype(str).str.replace('[^0-9]', '', regex=True), errors='coerce')

# Drop invalid rows
df = df[['maker', 'car_name', 'fuel_type', 'engine_size', 'odometer', 'registration_year', 'price']].dropna()

# Final type conversion
df['engine_size'] = df['engine_size'].astype(int)
df['odometer'] = df['odometer'].astype(int)
df['registration_year'] = df['registration_year'].astype(int)
df['price'] = df['price'].astype(float)

# Encode categorical columns
categorical_cols = ['maker', 'car_name', 'fuel_type']
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Features & target
FEATURE_COLUMNS = ['registration_year', 'maker', 'car_name', 'fuel_type', 'engine_size', 'odometer']
X = df[FEATURE_COLUMNS]
y = df['price']

# Train/test split and model training
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save artifacts
model_path = os.path.join(BASE_DIR, 'car_sales', 'ml_model.pkl')
encoder_path = os.path.join(BASE_DIR, 'car_sales', 'label_encoders.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
with open(encoder_path, 'wb') as f:
    pickle.dump(label_encoders, f)

print(f"✅ Model saved: {model_path}")
print(f"✅ Label encoders saved: {encoder_path}")
