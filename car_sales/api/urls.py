from django.urls import path
from .views import get_cars, predict_car_price
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # API-г энд холбож өгнө
]


urlpatterns = [
    path('cars/', get_cars),  # Машины жагсаалт авах
    path('predict/', predict_car_price),  # Үнэ таамаглах
]
