from django.db import models

# Create your models here.
from trips.models import Trips
from users.models import UserProfile

class TripRatings(models.Model):
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
