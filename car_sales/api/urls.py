from django.urls import path
from .views import get_cars, predict_car_price, get_model_info

urlpatterns = [
    path('cars/', get_cars),
    path('predict/', predict_car_price),
    path('model-info/', get_model_info),
]

