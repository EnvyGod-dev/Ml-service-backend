from django.urls import path
from .views import (
    predict_car_price,
    get_model_info,
    register_user,
    login_user,
    predict_batch,
    predict_time_series,
)

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('predict/', predict_car_price, name='predict_price'),
    path('predict/batch/', predict_batch, name='predict_batch'),
    path('predict/time-series/', predict_time_series, name='predict_time_series'),
    path('model-info/', get_model_info, name='model_info'),
]
