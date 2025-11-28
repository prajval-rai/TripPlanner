from django.db import models

# Create your models here.
from trips.models import Trips
from django.contrib.auth.models import User

class TripRatings(models.Model):
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
