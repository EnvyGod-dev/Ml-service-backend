from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ml_model import predict_price, label_encoders  # ✅ Add label_encoders import
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
import os
CARS = [
    {"car_name": "Toyota Corolla"},
    {"car_name": "Honda Civic"},
    {"car_name": "BMW 3 Series"},
    {"car_name": "Nissan Altima"},
    {"car_name": "Ford Focus"},
]

@api_view(["GET"])
def get_cars(request):
    return Response(CARS)

@api_view(["GET"])
def get_model_info(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(BASE_DIR, 'Data.csv')

    allowed_years = []

    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            print("[DEBUG] CSV columns:", df.columns.tolist())  # <-- see the real names

            # Normalize column names
            df.columns = [c.strip().lower().replace('\xa0', ' ').replace(' ', ' ') for c in df.columns]

            if 'year' in df.columns:
                allowed_years = (
                    pd.to_numeric(df['year'], errors='coerce')
                    .dropna()
                    .astype(int)
                    .sort_values()
                    .unique()
                    .tolist()
                )
            else:
                print("[DEBUG] 'year' column not found after normalization.")

        except Exception as e:
            print(f"[DEBUG] Failed to load years: {e}")

    return Response({
        "allowed_makers": label_encoders["maker"].classes_.tolist(),
        "allowed_car_names": label_encoders["car_name"].classes_.tolist(),
        "allowed_fuel_types": label_encoders["fuel_type"].classes_.tolist(),
        "allowed_years": allowed_years
    })
@api_view(["POST"])
def predict_car_price(request):
    try:
        data = request.data
        required_fields = ['registration_year', 'maker', 'car_name', 'fuel_type', 'engine_size', 'odometer']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=400)

        price = predict_price(data)
        return Response({"predicted_price": price})
    except Exception as e:
        return Response({"error": str(e)}, status=400)



@api_view(["POST"])
def register_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "User already exists"}, status=400)

    user = User.objects.create_user(username=username, password=password)
    token = Token.objects.create(user=user)
    return Response({"message": "User registered", "token": token.key}, status=201)


@api_view(["POST"])
def login_user(request):
    from django.contrib.auth import authenticate

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
    return Response({"error": "Invalid credentials"}, status=401)