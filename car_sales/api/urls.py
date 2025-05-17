from django.urls import path
from .views import (
    register_user,
    login_user,
    get_model_info,
    predict_car_price,
    predict_batch,
    predict_time_series,
)

urlpatterns = [
    # Auth
    path('register/', register_user,       name='register'),
    path('login/',    login_user,          name='login'),

    path('model-info/', get_model_info,    name='model_info'),

    path('predict/',           predict_car_price,    name='predict_price'),
    path('predict/batch/',     predict_batch,        name='predict_batch'),
    path('predict/time-series/', predict_time_series, name='predict_time_series'),
]
