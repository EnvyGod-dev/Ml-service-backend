
import os
import pickle
from django.conf import settings

# Try loading ts_model.pkl from BASE_DIR, then one level up
def _load_ts_model():
    # Primary location: alongside manage.py
    path = os.path.join(settings.BASE_DIR, 'ts_model.pkl')
    if not os.path.exists(path):
        # Fallback: parent of BASE_DIR (where you ran train_time_series_model.py)
        path = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'ts_model.pkl'))
    if not os.path.exists(path):
        raise FileNotFoundError(f"Time-series model not found at {path}")
    with open(path, 'rb') as f:
        return pickle.load(f)

# Load once at import time
_ts_model = _load_ts_model()


def forecast_price_series(periods: int, freq: str = 'M'):
    """
    Forecast future average prices for `periods` steps.
    Returns list of {'ds': date, 'yhat': value}.
    """
    forecast_res = _ts_model.get_forecast(steps=periods)
    mean_series = forecast_res.predicted_mean

    return [
        {'ds': idx.strftime('%Y-%m-%d'), 'yhat': float(val)}
        for idx, val in mean_series.items()
    ]
