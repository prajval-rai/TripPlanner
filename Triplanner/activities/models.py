from django.db import models
from trips.models import Trips

class Activity(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ]
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    day_number = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
