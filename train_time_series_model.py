import os
import pandas as pd
import pickle
from statsmodels.tsa.arima.model import ARIMA

# Directory containing Data.csv and where ts_model.pkl will be saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, 'Data.csv')

# Load CSV (ensure header row is read correctly)
df = pd.read_csv(file_path, header=0)
# Normalize column names
df.columns = [c.strip().lower().replace('\xa0', ' ') for c in df.columns]

# Parse dates and numeric prices with coercion
df['sold_date'] = pd.to_datetime(df.get('sold date', pd.Series()), dayfirst=True, errors='coerce')
df['price'] = pd.to_numeric(
    df.get('sold price', pd.Series()).astype(str)
      .str.replace(r'[^0-9]', '', regex=True),
    errors='coerce'
)
# Drop rows with invalid dates or prices
df = df.dropna(subset=['sold_date', 'price'])

# Aggregate monthly average prices
ts = (
    df.groupby(pd.Grouper(key='sold_date', freq='M'))['price']
      .mean()
)

# Fit ARIMA(1,1,1) model
model = ARIMA(ts, order=(1,1,1))
model_fit = model.fit()

# Save the time-series model
ts_model_path = os.path.join(BASE_DIR, 'ts_model.pkl')
with open(ts_model_path, 'wb') as f:
    pickle.dump(model_fit, f)

print(f"✅ Time series model saved: {ts_model_path}")