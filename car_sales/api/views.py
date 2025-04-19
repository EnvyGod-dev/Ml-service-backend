from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ml_model import predict_price, label_encoders  # ✅ Add label_encoders import

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
    return Response({
        "allowed_makers": label_encoders["maker"].classes_.tolist(),
        "allowed_car_names": label_encoders["car_name"].classes_.tolist(),
        "allowed_fuel_types": label_encoders["fuel_type"].classes_.tolist()
    })

@api_view(["POST"])
def predict_car_price(request):
    try:
        data = request.data
        required_fields = ['registration_year', 'manufacture_year', 'maker', 'car_name', 'fuel_type', 'engine_size', 'odometer']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=400)

        price = predict_price(data)
        return Response({"predicted_price": price})
    except Exception as e:
        return Response({"error": str(e)}, status=400)

