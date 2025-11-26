from django.db import models

# Create your models here.
from users.models import UserProfile

class Notifications(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)  # invite, reminder, etc
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


