from django.db import models

# Create your models here.
from trips.models import Trips
from activities.models import Activity
from django.contrib.auth.models import User

class TripMedia(models.Model):
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    media_url = models.CharField(max_length=255)
    media_type = models.CharField(max_length=20)  # image/video
    uploaded_at = models.DateTimeField(auto_now_add=True)

