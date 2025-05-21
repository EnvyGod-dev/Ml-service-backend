import os
import re
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble       import RandomForestRegressor
from sklearn.preprocessing  import LabelEncoder

# — Paths
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
CSV_PATH  = os.path.join(BASE_DIR, 'Data.csv')
OUT_DIR   = os.path.join(BASE_DIR, 'car_sales')
os.makedirs(OUT_DIR, exist_ok=True)

# — Load raw CSV
df = pd.read_csv(CSV_PATH)

# — Normalize chassis_id, colour, condition
df['chassis_id']        = df['Chassis ID'].astype(str).str.strip()
df['colour']            = df['Colour'].astype(str).str.strip().str.upper()
df['condition']         = pd.to_numeric(df['Condition'], errors='coerce')

# — Derive maker: MXUA80 → LEXUS, all others → TOYOTA
df['maker'] = np.where(df['chassis_id']=='MXUA80', 'LEXUS', 'TOYOTA')

# — Normalize car_name
df['car_name'] = (
    df['Box of Modif.']
      .astype(str)
      .apply(lambda x: re.sub(r'\s+', ' ', x.strip().upper()))
)

# — Other numeric fields
df['fuel_type']         = 'PETROL'
df['engine_size']       = pd.to_numeric(
    df['V,Engine CC'].astype(str).str.extract(r'(\d{3,5})')[0],
    errors='coerce'
)
df['odometer']          = pd.to_numeric(
    df['Mileage'].astype(str).str.replace(',', ''), errors='coerce'
)
df['registration_year'] = pd.to_numeric(df['year'], errors='coerce')
df['price']             = pd.to_numeric(
    df['sold price']
      .astype(str)
      .str.replace(r'[^0-9]', '', regex=True),
    errors='coerce'
)

# — Keep only the needed columns, drop any row with missing
keep = [
    'maker','car_name','fuel_type','engine_size','odometer',
    'registration_year','condition','chassis_id','colour','price'
]
df = df[keep].dropna()

# — Force correct dtypes
df = df.astype({
    'engine_size':'int',
    'odometer':'int',
    'registration_year':'int',
    'condition':'float',
    'price':'float'
})

# — Label-encode all categoricals
categorical = ['maker','car_name','fuel_type','chassis_id','colour']
encoders   = {}
for col in categorical:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# — Train/test split & model
features = [
    'registration_year','maker','car_name','fuel_type',
    'engine_size','odometer','condition','chassis_id','colour'
]
X, y = df[features], df['price']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# — Save artifacts
with open(os.path.join(OUT_DIR,'ml_model.pkl'), 'wb')   as f: pickle.dump(model, f)
with open(os.path.join(OUT_DIR,'label_encoders.pkl'),'wb') as f: pickle.dump(encoders, f)

print("✅ Trained model and encoders saved.")
