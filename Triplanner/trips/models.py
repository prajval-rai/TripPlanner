from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class TripTags(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Trips(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True,blank=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    location = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(TripTags, through='TripTagMapping', blank=True)
    photo = models.CharField(max_length=100,null=True,blank=True)

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

class ItineraryActivity(models.Model):
    trip = models.ForeignKey(Trips,on_delete=models.CASCADE)
    date = models.DateField(null=True,blank=True)
    title = models.CharField(max_length=50,null=True,blank=True)
    desc = models.CharField(max_length=200,null=True,blank=True)
    location = models.CharField(max_length=500,null=True,blank=True)
    lon = models.CharField(max_length=20,null=True,blank=True)
    lat = models.CharField(max_length=20,null=True,blank=True)
    start_time = models.CharField(max_length=50,null=True,blank=True)
    end_time = models.CharField(max_length=50,null=True,blank=True)
    reminder = models.BooleanField(default=True)
    reminder_time = models.CharField(max_length=50,null=True,blank=True)
    photo = models.CharField(max_length=100,null=True,blank=True)