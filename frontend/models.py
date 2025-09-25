from django.db import models

# Create your models here.

class airport(models.Model):
    airport_name = models.CharField(max_length=100)
    airport_iata = models.CharField(max_length=3)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timezone = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.airport_name} ({self.airport_iata})"

class flights(models.Model):
    flight_iata = models.CharField(max_length=10)
    flight_icao = models.CharField(max_length=10)
    airline_name = models.CharField(max_length=100)
    airline_iata = models.CharField(max_length=10)
    airline_icao = models.CharField(max_length=10)
    flight_number = models.CharField(max_length=10)
    departure_airport = models.ForeignKey(airport, on_delete=models.CASCADE, related_name='departures')
    departure_scheduled = models.DateTimeField()
    arrival_airport = models.ForeignKey(airport, on_delete=models.CASCADE, related_name='arrivals')
    arrival_scheduled = models.DateTimeField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.flight_iata} - {self.airline_name}"

    def get_duration(self):
        duration = self.arrival_scheduled - self.departure_scheduled
        return duration