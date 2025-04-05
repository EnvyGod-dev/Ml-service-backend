from django.db import models

class CarSalesPrediction(models.Model):
    car_model = models.CharField(max_length=255)
    year = models.IntegerField()
    mileage = models.IntegerField()
    price = models.FloatField()

    def __str__(self):
        return f"{self.car_model} ({self.year}) - {self.price}$"
