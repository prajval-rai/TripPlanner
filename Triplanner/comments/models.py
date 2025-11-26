from django.db import models

# Create your models here.
from trips.models import Trips
from activities.models import Activity
from users.models import UserProfile

class TripComments(models.Model):
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
