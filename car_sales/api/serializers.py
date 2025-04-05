from rest_framework import serializers
from .models import CarSalesPrediction

class CarSalesPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarSalesPrediction
        fields = '__all__'
