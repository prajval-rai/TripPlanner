from django.db import models

# Create your models here.
# Create your models here.
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    contact = models.CharField(max_length=20, unique=True)
    current_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    device_token = models.CharField(max_length=255, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='userprofile_set',  # custom related_name
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='userprofile_set',  # custom related_name
        blank=True,
        help_text='Specific permissions for this user.'
    )


class FollowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    request_from = models.ForeignKey(UserProfile, related_name='requests_sent', on_delete=models.CASCADE)
    request_to = models.ForeignKey(UserProfile, related_name='requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('request_from', 'request_to')



class Follower(models.Model):
    user = models.ForeignKey(UserProfile, related_name='followers', on_delete=models.CASCADE)  # user being followed
    follow_by = models.ForeignKey(UserProfile, related_name='following', on_delete=models.CASCADE)  # follower
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'follow_by')