from django.db import models

class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2)
    seats = models.IntegerField()

    def __str__(self):
        return self.name
