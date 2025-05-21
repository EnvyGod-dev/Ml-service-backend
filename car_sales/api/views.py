# car_sales/api/views.py

import re
import os
import pandas as pd
from pathlib import Path
from django.conf import settings
from django.contrib.auth import authenticate, models as auth_models
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .ml_model           import predict_price, label_encoders
from .time_series_model import forecast_price_series

def _get_classes(key):
    le = label_encoders.get(key)
    return le.classes_.tolist() if le is not None else []

@api_view(['GET'])
def get_model_info(request):
    """
    Returns dropdowns:
      - allowed_makers      (from encoder)
      - allowed_car_names   (from CSV)
      - allowed_fuel_types  (from encoder)
      - allowed_chassis_ids (from CSV)
      - allowed_colours     (from CSV)
      - allowed_years       (from CSV)

    Optional filter:
      ?maker=LEXUS or ?maker=TOYOTA
    """
    # 1) Locate Data.csv (one level above BASE_DIR)
    project_root = Path(settings.BASE_DIR).parent
    csv_path     = project_root / 'Data.csv'
    if not csv_path.exists():
        return Response(
            {'error': 'Data.csv not found on server'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 2) Load & lowercase column names
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    # 3) Verify we have the columns we expect
    required_cols = ['maker', 'box of modif.', 'chassis id', 'colour', 'year']
    for col in required_cols:
        if col not in df.columns:
            return Response(
                {'error': f"Required column '{col}' not in Data.csv"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # 4) Normalize them into the feature fields you trained on
    df['maker']      = df['maker'].astype(str).str.strip().str.upper()
    df['car_name']   = (
        df['box of modif.']
          .astype(str)
          .apply(lambda x: re.sub(r'\s+', ' ', x.strip().upper()))
    )
    df['chassis_id'] = df['chassis id'].astype(str).str.strip()
    df['colour']     = df['colour'].astype(str).str.strip().str.upper()
    df['year']       = pd.to_numeric(df['year'], errors='coerce')

    # 5) Optional maker filter
    maker_filter = request.query_params.get('maker')
    if maker_filter:
        mf = maker_filter.strip().upper()
        df = df[df['maker'] == mf]

    # 6) Return the six dropdown arrays
    return Response({
        'allowed_makers':       _get_classes('maker'),
        'allowed_car_names':    sorted(df['car_name'].dropna().unique().tolist()),
        'allowed_fuel_types':   _get_classes('fuel_type'),
        'allowed_chassis_ids':  sorted(df['chassis_id'].dropna().unique().tolist()),
        'allowed_colours':      sorted(df['colour'].dropna().unique().tolist()),
        'allowed_years':        sorted(df['year'].dropna().astype(int).unique().tolist()),
    })


@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Username and password required'},
                        status=status.HTTP_400_BAD_REQUEST)
    if auth_models.User.objects.filter(username=username).exists():
        return Response({'error': 'User already exists'},
                        status=status.HTTP_400_BAD_REQUEST)

    user = auth_models.User.objects.create_user(username=username, password=password)
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access':  str(refresh.access_token)
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_user(request):
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
    data = request.data
    required = [
        'registration_year', 'maker', 'car_name', 'fuel_type',
        'engine_size', 'odometer', 'condition', 'chassis_id', 'colour'
    ]
    missing = [f for f in required if f not in data]
    if missing:
        return Response({'error': f"Missing fields: {', '.join(missing)}"},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        price = predict_price(data)
        return Response({'predicted_price': price})
    except Exception as e:
        return Response({'error': str(e)},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def predict_batch(request):
    data_list = request.data
    if not isinstance(data_list, list):
        return Response({'error': 'Expected list of car data dicts'},
                        status=status.HTTP_400_BAD_REQUEST)

    results, errors = [], []
    for d in data_list:
        try:
            results.append(predict_price(d))
            errors.append(None)
        except Exception as e:
            results.append(None)
            errors.append(str(e))

    return Response({'predicted_prices': results, 'errors': errors})


@api_view(['GET'])
def predict_time_series(request):
    periods = request.query_params.get('periods')
    freq    = request.query_params.get('freq', 'M')
    if periods is None:
        return Response({'error': '"periods" is required'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        periods = int(periods)
    except ValueError:
        return Response({'error': '"periods" must be integer'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        forecast = forecast_price_series(periods=periods, freq=freq)
        return Response({'forecast': forecast})
    except Exception as e:
        return Response({'error': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
