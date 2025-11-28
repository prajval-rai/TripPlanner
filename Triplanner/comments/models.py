from django.db import models

# Create your models here.
from trips.models import Trips
from activities.models import Activity
from django.contrib.auth.models import User

class TripComments(models.Model):
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
