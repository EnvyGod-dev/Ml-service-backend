import pandas as pd
import pickle
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# — Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, 'Data.csv')

# — Load & clean
df = pd.read_csv(file_path)

# — New features
# 1) Chassis ID (as string)
df['chassis_id'] = df['Chassis ID'].astype(str).str.strip()

# 2) Colour (normalize to uppercase, no leading/trailing spaces)
df['colour'] = df['Colour'].astype(str).str.strip().str.upper()

# 3) Condition (float)
df['condition'] = pd.to_numeric(df['Condition'], errors='coerce')

# — Maker mapping (example: MXUA80 → TOYOTA; else LEXUS)
maker_map = {
    'MXUA80': 'TOYOTA',
    # add more chassis_id → maker entries as needed
}
df['maker'] = df['chassis_id'].map(maker_map).fillna('LEXUS')

# — Existing fields
df['car_name'] = (
    df['Box of Modif.']
    .astype(str)
    .apply(lambda x: re.sub(r'\s+', ' ', x.strip().upper()))
)
df['fuel_type'] = 'PETROL'
df['engine_size'] = pd.to_numeric(
    df['V,Engine CC'].astype(str).str.extract(r'(\d{3,5})')[0],
    errors='coerce'
)
df['odometer'] = pd.to_numeric(
    df['Mileage'].astype(str).str.replace(',', ''), errors='coerce'
)
df['registration_year'] = pd.to_numeric(df['year'], errors='coerce')
df['price'] = pd.to_numeric(
    df['sold price']
      .astype(str)
      .str.replace(r'[^0-9]', '', regex=True),
    errors='coerce'
)

cols_to_keep = [
    'maker', 'car_name', 'fuel_type',
    'engine_size', 'odometer', 'registration_year',
    'condition', 'chassis_id', 'colour', 'price'
]
df = df[cols_to_keep].dropna()

df = df.astype({
    'engine_size': 'int',
    'odometer': 'int',
    'registration_year': 'int',
    'condition': 'float',
    'price': 'float'
})

categorical_cols = ['maker', 'car_name', 'fuel_type', 'chassis_id', 'colour']
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# — Features & target
FEATURE_COLUMNS = [
    'registration_year', 'maker', 'car_name', 'fuel_type',
    'engine_size', 'odometer', 'condition', 'chassis_id', 'colour'
]
X = df[FEATURE_COLUMNS]
y = df['price']

# — Train/test split & model training
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# — Save artifacts
car_sales_dir = os.path.join(BASE_DIR, 'car_sales')
os.makedirs(car_sales_dir, exist_ok=True)

model_path   = os.path.join(car_sales_dir, 'ml_model.pkl')
encoder_path = os.path.join(car_sales_dir, 'label_encoders.pkl')

with open(model_path, 'wb') as f:
    pickle.dump(model, f)
with open(encoder_path, 'wb') as f:
    pickle.dump(label_encoders, f)

print(f"✅ Model saved: {model_path}")
print(f"✅ Label encoders saved: {encoder_path}")
