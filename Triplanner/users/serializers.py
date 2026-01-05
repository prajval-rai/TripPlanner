from rest_framework import serializers
from .models import Profile,Follower
from django.contrib.auth.models import User


class ProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class FollowerDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='follow_by.first_name')
    last_name = serializers.CharField(source='follow_by.last_name')
    username = serializers.CharField(source='follow_by.username')
    userid = serializers.IntegerField(source='follow_by.id')
    class Meta:
        model = Follower
        fields = ['userid', 'first_name', 'last_name', 'username', 'followed_at']
