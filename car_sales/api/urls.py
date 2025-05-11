from django.urls import path
from .views import get_cars, predict_car_price, get_model_info, register_user, login_user

urlpatterns = [
    path("register/", register_user),
    path("login/", login_user),
    path('cars/', get_cars),
    path('predict/', predict_car_price),
    path('model-info/', get_model_info),
]

