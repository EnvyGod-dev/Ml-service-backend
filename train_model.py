# train_model.py
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "Data.csv")

# Load CSV
df = pd.read_csv(file_path)

# Select necessary columns
df_cleaned = df[['REGISTRATION YEAR', 'MANUFACTURE YEAR', 'MAKER', 'CAR NAME', 
                 'FUEL TYPE', 'Engine Size', 'KM', 'PRICE']]

# Drop rows with missing required fields
df_cleaned = df_cleaned.dropna(subset=[
    'REGISTRATION YEAR', 'MANUFACTURE YEAR', 'MAKER', 'CAR NAME',
    'FUEL TYPE', 'Engine Size', 'KM', 'PRICE'
])

# Rename for convenience
df_cleaned.columns = ['registration_year', 'manufacture_year', 'maker', 'car_name', 
                      'fuel_type', 'engine_size', 'odometer', 'price']

# Convert data types
df_cleaned = df_cleaned.astype({
    'registration_year': int,
    'manufacture_year': int,
    'engine_size': int,
    'odometer': int,
    'price': float
})

# Label encode
label_encoders = {}
categorical_columns = ['maker', 'car_name', 'fuel_type']
for col in categorical_columns:
    le = LabelEncoder()
    df_cleaned[col] = le.fit_transform(df_cleaned[col])
    label_encoders[col] = le

# Define features and target
X = df_cleaned.drop(columns=['price'])
y = df_cleaned['price']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model
model_path = os.path.join(BASE_DIR, "ml_model.pkl")
encoder_path = os.path.join(BASE_DIR, "label_encoders.pkl")

with open(model_path, "wb") as f:
    pickle.dump(model, f)

with open(encoder_path, "wb") as f:
    pickle.dump(label_encoders, f)

print(f"✅ Model saved to {model_path}")
