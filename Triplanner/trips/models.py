from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class TripTags(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Trips(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(TripTags, through='TripTagMapping', blank=True)

class TripTagMapping(models.Model):
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    tag = models.ForeignKey(TripTags, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('trip', 'tag')

class InvitedPeople(models.Model):
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    ]
    trip = models.ForeignKey(Trips, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_msg = models.TextField(blank=True, null=True)
    reminder_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')
