from django.db import models

# Create your models here.
class flights(models.Model):
    flight_iata = models.CharField(max_length=10, null=True, blank=True)
    flight_icao = models.CharField(max_length=10, null=True, blank=True)
    flight_number = models.CharField(max_length=10, null=True, blank=True)
    airline_name = models.CharField(max_length=100, null=True, blank=True)
    airline_iata = models.CharField(max_length=3, null=True, blank=True)
    airline_icao = models.CharField(max_length=10, null=True, blank=True)
    departure_airport = models.CharField(max_length=100, null=True, blank=True)
    departure_iata = models.CharField(max_length=10, null=True, blank=True)
    departure_scheduled = models.DateTimeField(null=True, blank=True)
    arrival_airport = models.CharField(max_length=100, null=True, blank=True)
    arrival_iata = models.CharField(max_length=10, null=True, blank=True)
    arrival_scheduled = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.flight_iata} - {self.airline_name}"

    def get_duration(self):
        duration = self.arrival_scheduled - self.departure_scheduled
        return duration