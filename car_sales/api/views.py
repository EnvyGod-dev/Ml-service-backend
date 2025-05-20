# car_sales/api/views.py

import os
import pandas as pd
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .ml_model import predict_price, label_encoders
from .time_series_model import forecast_price_series

# Helper to safely retrieve encoder classes
def _get_classes(key):
    le = label_encoders.get(key)
    return le.classes_.tolist() if le is not None else []

@api_view(['GET'])
def get_model_info(request):
    """
    Returns all allowed dropdown values: makers, car_names, fuel_types,
    chassis_ids, colours, and years (from Data.csv).
    """
    csv_path = os.path.join(settings.BASE_DIR, 'Data.csv')
    if not os.path.exists(csv_path):
        csv_path = os.path.join(settings.BASE_DIR, '..', 'Data.csv')

    allowed_years = []
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            df.columns = [c.strip().lower().replace('\xa0', ' ') for c in df.columns]
            if 'year' in df.columns:
                allowed_years = (
                    pd.to_numeric(df['year'], errors='coerce')
                      .dropna()
                      .astype(int)
                      .sort_values()
                      .unique()
                      .tolist()
                )
        except Exception as e:
            print(f"[DEBUG] Failed to load years: {e}")

    return Response({
        'allowed_makers':      _get_classes('maker'),
        'allowed_car_names':   _get_classes('car_name'),
        'allowed_fuel_types':  _get_classes('fuel_type'),
        'allowed_chassis_ids': _get_classes('chassis_id'),
        'allowed_colours':     _get_classes('colour'),
        'allowed_years':       allowed_years,
    })


@api_view(['POST'])
def register_user(request):
    """
    Register a new user and return JWT tokens.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required'},
                        status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'User already exists'},
                        status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access':  str(refresh.access_token)
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_user(request):
    """
    Authenticate and return fresh JWT tokens.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'},
                        status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access':  str(refresh.access_token)
    })


@api_view(['POST'])
def predict_car_price(request):
    """
    Accepts JSON with all required features and returns predicted price.
    """
    data = request.data
    required_fields = [
        'registration_year', 'maker', 'car_name', 'fuel_type',
        'engine_size', 'odometer', 'condition', 'chassis_id', 'colour'
    ]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return Response({'error': f"Missing fields: {', '.join(missing)}"},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        price = predict_price(data)
        return Response({'predicted_price': price})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def predict_batch(request):
    """
    Batch predictions for a list of car data dicts.
    """
    data_list = request.data
    if not isinstance(data_list, list):
        return Response({'error': 'Expected a list of car data dicts'},
                        status=status.HTTP_400_BAD_REQUEST)

    results, errors = [], []
    for data in data_list:
        try:
            results.append(predict_price(data))
            errors.append(None)
        except Exception as e:
            results.append(None)
            errors.append(str(e))

    return Response({'predicted_prices': results, 'errors': errors})


@api_view(['GET'])
def predict_time_series(request):
    """
    Forecast time-series of average prices.
    Query params:
      - periods (int, required)
      - freq (str, optional, default 'M')
    """
    periods = request.query_params.get('periods')
    freq    = request.query_params.get('freq', 'M')

    if periods is None:
        return Response({'error': 'Query param "periods" is required'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        periods = int(periods)
    except ValueError:
        return Response({'error': '"periods" must be an integer'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        forecast = forecast_price_series(periods=periods, freq=freq)
        return Response({'forecast': forecast})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
