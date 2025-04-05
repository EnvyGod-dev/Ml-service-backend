from django.http import JsonResponse
from rest_framework.decorators import api_view
from .ml_model import predict_price
from rest_framework.response import Response

CARS = [
    {"car_name": "Toyota Corolla"},
    {"car_name": "Honda Civic"},
    {"car_name": "BMW 3 Series"},
    {"car_name": "Nissan Altima"},
    {"car_name": "Ford Focus"},
]

@api_view(["GET"])
def get_cars(request):
    """ Машины жагсаалт буцаах API """
    return JsonResponse(CARS, safe=False)

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