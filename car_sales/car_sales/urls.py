from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Нүүр хуудсыг харуулах функц
def home(request):
    return HttpResponse("<h1>Сайн байна уу! Энэ бол Django API-ийн эхлэл хуудас.</h1>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # API чиглүүлэлт
    path('', home),  # Нүүр хуудасны чиглүүлэлт
]
